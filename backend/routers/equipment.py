from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Equipment, EquipmentType, User, UserRole
from backend.schemas import EquipmentCreate, EquipmentUpdate, EquipmentResponse
from backend.auth import get_current_user

router = APIRouter(prefix="/api/equipment", tags=["Farm Equipment"])

@router.get("", response_model=List[EquipmentResponse])
def get_equipment(
    type: Optional[EquipmentType] = None,
    location: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Equipment)
    if type:
        query = query.filter(Equipment.type == type)
    if location:
        query = query.filter(Equipment.location.ilike(f"%{location}%"))
    if search:
        query = query.filter(
            Equipment.name.ilike(f"%{search}%") | Equipment.description.ilike(f"%{search}%")
        )
    equipment_list = query.order_by(Equipment.created_at.desc()).all()
    results = []
    for eq in equipment_list:
        resp = EquipmentResponse.from_orm(eq)
        if eq.owner:
            resp.owner_name = eq.owner.name
            resp.owner_phone = eq.owner.phone
        results.append(resp)
    return results

@router.get("/my", response_model=List[EquipmentResponse])
def get_my_equipment(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    equipment_list = db.query(Equipment).filter(Equipment.owner_id == current_user.id).all()
    return [EquipmentResponse.from_orm(eq) for eq in equipment_list]

@router.get("/{id}", response_model=EquipmentResponse)
def get_equipment_by_id(id: int, db: Session = Depends(get_db)):
    eq = db.query(Equipment).filter(Equipment.id == id).first()
    if not eq:
        raise HTTPException(status_code=404, detail="Equipment machinery not found")
    resp = EquipmentResponse.from_orm(eq)
    if eq.owner:
        resp.owner_name = eq.owner.name
        resp.owner_phone = eq.owner.phone
    return resp

@router.post("", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED)
def create_equipment(
    eq_in: EquipmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Ensure current user has is_equipment_owner enabled
    if not current_user.is_equipment_owner and current_user.role != UserRole.ADMIN:
        # Auto-grant owner privilege if farmer lists machinery
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
        image_url=eq_in.image_url,
    )
    db.add(equipment)
    db.commit()
    db.refresh(equipment)

    resp = EquipmentResponse.from_orm(equipment)
    resp.owner_name = current_user.name
    resp.owner_phone = current_user.phone
    return resp

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

    update_data = eq_update.dict(exclude_unset=True)
    for field, val in update_data.items():
        setattr(eq, field, val)

    db.commit()
    db.refresh(eq)
    resp = EquipmentResponse.from_orm(eq)
    resp.owner_name = current_user.name
    return resp

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
