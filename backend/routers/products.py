from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Product, ProductCategory, User, UserRole
from backend.schemas import ProductCreate, ProductUpdate, ProductResponse
from backend.auth import get_current_user, require_roles

router = APIRouter(prefix="/api/products", tags=["Marketplace Products"])

@router.get("", response_model=List[ProductResponse])
def get_products(
    category: Optional[ProductCategory] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Product)
    if category:
        query = query.filter(Product.category == category)
    if search:
        query = query.filter(
            Product.name.ilike(f"%{search}%") | Product.description.ilike(f"%{search}%")
        )
    products = query.order_by(Product.created_at.desc()).all()
    # Populate vendor name
    result = []
    for p in products:
        p_dict = ProductResponse.from_orm(p)
        if p.vendor:
            p_dict.vendor_name = p.vendor.name
        result.append(p_dict)
    return result

@router.get("/my", response_model=List[ProductResponse])
def get_my_products(
    current_user: User = Depends(require_roles([UserRole.VENDOR, UserRole.ADMIN])),
    db: Session = Depends(get_db),
):
    products = db.query(Product).filter(Product.vendor_id == current_user.id).all()
    return [ProductResponse.from_orm(p) for p in products]

@router.get("/{id}", response_model=ProductResponse)
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    resp = ProductResponse.from_orm(product)
    if product.vendor:
        resp.vendor_name = product.vendor.name
    return resp

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    prod_in: ProductCreate,
    current_user: User = Depends(require_roles([UserRole.VENDOR, UserRole.ADMIN])),
    db: Session = Depends(get_db),
):
    product = Product(
        vendor_id=current_user.id,
        name=prod_in.name,
        category=prod_in.category,
        description=prod_in.description,
        price=prod_in.price,
        stock=prod_in.stock,
        image_url=prod_in.image_url,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    resp = ProductResponse.from_orm(product)
    resp.vendor_name = current_user.name
    return resp

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

    update_data = prod_update.dict(exclude_unset=True)
    for field, val in update_data.items():
        setattr(product, field, val)

    db.commit()
    db.refresh(product)
    resp = ProductResponse.from_orm(product)
    resp.vendor_name = current_user.name
    return resp

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
