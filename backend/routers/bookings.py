from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import BookingRequest, BookingStatus, Equipment, User, UserRole
from backend.schemas import BookingCreate, BookingResponse
from backend.auth import get_current_user
from backend.config import settings

router = APIRouter(prefix="/api/bookings", tags=["Equipment Bookings & FCFS Queue"])

def format_booking_response(b: BookingRequest) -> BookingResponse:
    resp = BookingResponse.from_orm(b)
    if b.farmer:
        resp.farmer_name = b.farmer.name
        resp.farmer_phone = b.farmer.phone
    if b.equipment:
        resp.equipment_name = b.equipment.name
        resp.equipment_location = b.equipment.location
    return resp

@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_in: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if booking_in.start_date >= booking_in.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be strictly after start date."
        )

    eq = db.query(Equipment).filter(Equipment.id == booking_in.equipment_id).first()
    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found.")

    now = datetime.utcnow()

    # Query overlapping bookings that are active (CONFIRMED or CONFIRMATION_PENDING)
    overlapping_active = (
        db.query(BookingRequest)
        .filter(
            BookingRequest.equipment_id == booking_in.equipment_id,
            BookingRequest.status.in_([BookingStatus.CONFIRMED, BookingStatus.CONFIRMATION_PENDING]),
            BookingRequest.start_date < booking_in.end_date,
            BookingRequest.end_date > booking_in.start_date,
        )
        .first()
    )

    if not overlapping_active:
        # First-Come First-Served slot granted!
        new_booking = BookingRequest(
            farmer_id=current_user.id,
            equipment_id=booking_in.equipment_id,
            start_date=booking_in.start_date,
            end_date=booking_in.end_date,
            status=BookingStatus.CONFIRMATION_PENDING,
            queue_position=None,
            confirmation_deadline=now + timedelta(hours=settings.BOOKING_CONFIRMATION_HOURS),
        )
    else:
        # Overlapping booking exists, place into FCFS queue
        queued_count = (
            db.query(BookingRequest)
            .filter(
                BookingRequest.equipment_id == booking_in.equipment_id,
                BookingRequest.status == BookingStatus.QUEUED,
                BookingRequest.start_date < booking_in.end_date,
                BookingRequest.end_date > booking_in.start_date,
            )
            .count()
        )
        new_booking = BookingRequest(
            farmer_id=current_user.id,
            equipment_id=booking_in.equipment_id,
            start_date=booking_in.start_date,
            end_date=booking_in.end_date,
            status=BookingStatus.QUEUED,
            queue_position=queued_count + 1,
            confirmation_deadline=None,
        )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return format_booking_response(new_booking)

@router.get("/my", response_model=List[BookingResponse])
def get_my_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bookings = (
        db.query(BookingRequest)
        .filter(BookingRequest.farmer_id == current_user.id)
        .order_by(BookingRequest.created_at.desc())
        .all()
    )
    return [format_booking_response(b) for b in bookings]

@router.get("/owner", response_model=List[BookingResponse])
def get_owner_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Bookings made for equipment owned by this user
    bookings = (
        db.query(BookingRequest)
        .join(Equipment, BookingRequest.equipment_id == Equipment.id)
        .filter(Equipment.owner_id == current_user.id)
        .order_by(BookingRequest.created_at.desc())
        .all()
    )
    return [format_booking_response(b) for b in bookings]

@router.get("/{id}", response_model=BookingResponse)
def get_booking_by_id(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    b = db.query(BookingRequest).filter(BookingRequest.id == id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Booking request not found")
    return format_booking_response(b)

@router.post("/{id}/confirm", response_model=BookingResponse)
def confirm_booking(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    b = db.query(BookingRequest).filter(BookingRequest.id == id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Booking request not found")
    if b.farmer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to confirm this booking")
    if b.status != BookingStatus.CONFIRMATION_PENDING:
        raise HTTPException(status_code=400, detail=f"Cannot confirm booking in status '{b.status}'")

    b.status = BookingStatus.CONFIRMED
    b.confirmation_deadline = None
    db.commit()
    db.refresh(b)
    return format_booking_response(b)

@router.post("/{id}/cancel", response_model=BookingResponse)
def cancel_booking(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    b = db.query(BookingRequest).filter(BookingRequest.id == id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Booking request not found")
    if b.farmer_id != current_user.id and current_user.role != UserRole.ADMIN:
        # Also allow equipment owner to cancel
        if not b.equipment or b.equipment.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to cancel this booking")

    prev_status = b.status
    b.status = BookingStatus.CANCELLED
    b.queue_position = None
    now = datetime.utcnow()

    # If cancelled booking was holding the slot, promote next queued booking!
    if prev_status in [BookingStatus.CONFIRMATION_PENDING, BookingStatus.CONFIRMED]:
        next_in_queue = (
            db.query(BookingRequest)
            .filter(
                BookingRequest.equipment_id == b.equipment_id,
                BookingRequest.status == BookingStatus.QUEUED,
                BookingRequest.start_date < b.end_date,
                BookingRequest.end_date > b.start_date,
            )
            .order_by(BookingRequest.queue_position.asc(), BookingRequest.created_at.asc())
            .first()
        )
        if next_in_queue:
            next_in_queue.status = BookingStatus.CONFIRMATION_PENDING
            next_in_queue.queue_position = None
            next_in_queue.confirmation_deadline = now + timedelta(
                hours=settings.BOOKING_CONFIRMATION_HOURS
            )

    db.commit()
    db.refresh(b)
    return format_booking_response(b)
