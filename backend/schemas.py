from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from backend.models import UserRole, ProductCategory, EquipmentType, RateUnit, BookingStatus, OrderStatus

# User Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: str
    role: UserRole
    is_equipment_owner: bool = False
    location: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Product Schemas
class ProductBase(BaseModel):
    name: str
    category: ProductCategory
    description: str
    price: float
    stock: int
    image_url: str

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[ProductCategory] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    image_url: Optional[str] = None

class ProductResponse(ProductBase):
    id: int
    vendor_id: int
    vendor_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Cart Schemas
class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: ProductResponse
    created_at: datetime

    class Config:
        from_attributes = True

# Order Schemas
class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price_at_purchase: float
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    delivery_address: str
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None

class OrderUpdateStatus(BaseModel):
    status: OrderStatus

class OrderResponse(BaseModel):
    id: int
    farmer_id: int
    farmer_name: Optional[str] = None
    total_amount: float
    status: OrderStatus
    delivery_address: str
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    items: List[OrderItemResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True

# Equipment Schemas
class EquipmentBase(BaseModel):
    name: str
    type: EquipmentType
    description: str
    specifications: str
    rate: float
    rate_unit: RateUnit
    location: str
    image_url: str

class EquipmentCreate(EquipmentBase):
    pass

class EquipmentUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[EquipmentType] = None
    description: Optional[str] = None
    specifications: Optional[str] = None
    rate: Optional[float] = None
    rate_unit: Optional[RateUnit] = None
    location: Optional[str] = None
    image_url: Optional[str] = None

class EquipmentResponse(EquipmentBase):
    id: int
    owner_id: int
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Booking Schemas
class BookingCreate(BaseModel):
    equipment_id: int
    start_date: datetime
    end_date: datetime

class BookingResponse(BaseModel):
    id: int
    farmer_id: int
    farmer_name: Optional[str] = None
    farmer_phone: Optional[str] = None
    equipment_id: int
    equipment_name: Optional[str] = None
    equipment_location: Optional[str] = None
    start_date: datetime
    end_date: datetime
    status: BookingStatus
    queue_position: Optional[int] = None
    confirmation_deadline: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Payment Verification Schema
class PaymentVerifyRequest(BaseModel):
    order_id: int
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

class AdminStatsResponse(BaseModel):
    total_users: int
    total_farmers: int
    total_vendors: int
    total_equipment: int
    total_products: int
    total_orders: int
    total_bookings: int
    total_revenue: float
