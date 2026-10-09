from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from backend.database import get_db
from backend.models import Product, ProductCategory, User, UserRole
from backend.schemas import ProductCreate, ProductUpdate, ProductResponse
from backend.auth import get_current_user, require_roles

router = APIRouter(prefix="/api/products", tags=["Marketplace Products"])

def format_product_response(p: Product) -> ProductResponse:
    availability = getattr(p, "availability_status", None) or (
        "OUT_OF_STOCK" if p.stock <= 0 else "LOW_STOCK" if p.stock <= 15 else "IN_STOCK"
    )
    return ProductResponse(
        id=p.id,
        vendor_id=p.vendor_id,
        vendor_name=p.vendor.name if p.vendor else "Verified Agro Vendor",
        name=p.name,
        category=p.category,
        description=p.description,
        price=p.price,
        stock=p.stock,
        availability_status=availability,
        image_url=p.image_url,
        created_at=p.created_at,
        updated_at=getattr(p, "updated_at", None),
    )

@router.get("", response_model=List[ProductResponse])
def get_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Product).outerjoin(User, Product.vendor_id == User.id)
    if category and category != "ALL":
        query = query.filter(Product.category == category)
    if search:
        q = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Product.name.ilike(q),
                Product.description.ilike(q),
                User.name.ilike(q),
            )
        )
    products = query.order_by(Product.id.asc()).all()
    return [format_product_response(p) for p in products]

@router.get("/my", response_model=List[ProductResponse])
def get_my_products(
    current_user: User = Depends(require_roles([UserRole.VENDOR, UserRole.ADMIN])),
    db: Session = Depends(get_db),
):
    if current_user.role == UserRole.ADMIN:
        products = db.query(Product).order_by(Product.id.asc()).all()
    else:
        products = db.query(Product).filter(Product.vendor_id == current_user.id).order_by(Product.id.asc()).all()
    return [format_product_response(p) for p in products]

@router.get("/{id}", response_model=ProductResponse)
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return format_product_response(product)

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    prod_in: ProductCreate,
    current_user: User = Depends(require_roles([UserRole.VENDOR, UserRole.ADMIN])),
    db: Session = Depends(get_db),
):
    availability = prod_in.availability_status or (
        "OUT_OF_STOCK" if prod_in.stock <= 0 else "LOW_STOCK" if prod_in.stock <= 15 else "IN_STOCK"
    )
    product = Product(
        vendor_id=current_user.id,
        name=prod_in.name,
        category=prod_in.category,
        description=prod_in.description,
        price=prod_in.price,
        stock=prod_in.stock,
        availability_status=availability,
        image_url=prod_in.image_url,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return format_product_response(product)

@router.put("/{id}", response_model=ProductResponse)
def update_product(
    id: int,
    prod_update: ProductUpdate,
    current_user: User = Depends(require_roles([UserRole.VENDOR, UserRole.ADMIN])),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.vendor_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to edit this product")

    update_data = prod_update.model_dump(exclude_unset=True) if hasattr(prod_update, "model_dump") else prod_update.dict(exclude_unset=True)
    for field, val in update_data.items():
        setattr(product, field, val)

    if "stock" in update_data and "availability_status" not in update_data:
        product.availability_status = (
            "OUT_OF_STOCK" if product.stock <= 0 else "LOW_STOCK" if product.stock <= 15 else "IN_STOCK"
        )

    db.commit()
    db.refresh(product)
    return format_product_response(product)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    id: int,
    current_user: User = Depends(require_roles([UserRole.VENDOR, UserRole.ADMIN])),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.vendor_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to delete this product")

    db.delete(product)
    db.commit()
    return None

