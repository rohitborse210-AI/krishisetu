from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from backend.database import get_db
from backend.models import Equipment, EquipmentType, User, UserRole
from backend.schemas import EquipmentCreate, EquipmentUpdate, EquipmentResponse
from backend.auth import get_current_user

router = APIRouter(prefix="/api/equipment", tags=["Farm Equipment"])

def format_equipment_response(eq: Equipment) -> EquipmentResponse:
    return EquipmentResponse(
        id=eq.id,
        owner_id=eq.owner_id,
        owner_name=eq.owner.name if eq.owner else "Equipment Owner",
        owner_phone=eq.owner.phone if eq.owner else None,
        name=eq.name,
        type=eq.type,
        description=eq.description,
        specifications=eq.specifications,
        rate=eq.rate,
        rate_unit=eq.rate_unit,
        location=eq.location,
        stock_quantity=getattr(eq, "stock_quantity", 1) or 1,
        availability_status=getattr(eq, "availability_status", "AVAILABLE") or "AVAILABLE",
        image_url=eq.image_url,
        created_at=eq.created_at,
        updated_at=getattr(eq, "updated_at", None),
    )

@router.get("", response_model=List[EquipmentResponse])
def get_equipment(
    type: Optional[str] = None,
    location: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Equipment).outerjoin(User, Equipment.owner_id == User.id)
    if type and type != "ALL":
        query = query.filter(Equipment.type == type)
    if location:
        query = query.filter(Equipment.location.ilike(f"%{location.strip()}%"))
    if search:
        q = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Equipment.name.ilike(q),
                Equipment.description.ilike(q),
                Equipment.specifications.ilike(q),
                User.name.ilike(q),
            )
        )
    equipment_list = query.order_by(Equipment.id.asc()).all()
    return [format_equipment_response(eq) for eq in equipment_list]

@router.get("/my", response_model=List[EquipmentResponse])
def get_my_equipment(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role == UserRole.ADMIN:
        equipment_list = db.query(Equipment).order_by(Equipment.id.asc()).all()
    else:
        equipment_list = db.query(Equipment).filter(Equipment.owner_id == current_user.id).order_by(Equipment.id.asc()).all()
    return [format_equipment_response(eq) for eq in equipment_list]

@router.get("/{id}", response_model=EquipmentResponse)
def get_equipment_by_id(id: int, db: Session = Depends(get_db)):
    eq = db.query(Equipment).filter(Equipment.id == id).first()
    if not eq:
        raise HTTPException(status_code=404, detail="Equipment machinery not found")
    return format_equipment_response(eq)

@router.post("", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED)
def create_equipment(
    eq_in: EquipmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.is_equipment_owner and current_user.role != UserRole.ADMIN:
        current_user.is_equipment_owner = True
        db.add(current_user)

    equipment = Equipment(
        owner_id=current_user.id,
        name=eq_in.name,
        type=eq_in.type,
        description=eq_in.description,
        specifications=eq_in.specifications,
        rate=eq_in.rate,
        rate_unit=eq_in.rate_unit,
        location=eq_in.location,
        stock_quantity=eq_in.stock_quantity or 1,
        availability_status=eq_in.availability_status or "AVAILABLE",
        image_url=eq_in.image_url,
    )
    db.add(equipment)
    db.commit()
    db.refresh(equipment)
    return format_equipment_response(equipment)

@router.put("/{id}", response_model=EquipmentResponse)
def update_equipment(
    id: int,
    eq_update: EquipmentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    eq = db.query(Equipment).filter(Equipment.id == id).first()
    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")
    if eq.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to modify this equipment")

    update_data = eq_update.model_dump(exclude_unset=True) if hasattr(eq_update, "model_dump") else eq_update.dict(exclude_unset=True)
    for field, val in update_data.items():
        setattr(eq, field, val)

    db.commit()
    db.refresh(eq)
    return format_equipment_response(eq)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_equipment(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    eq = db.query(Equipment).filter(Equipment.id == id).first()
    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")
    if eq.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to delete this equipment")

    db.delete(eq)
    db.commit()
    return None

