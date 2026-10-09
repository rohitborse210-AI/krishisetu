import enum
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Enum,
    Text,
)
from sqlalchemy.orm import relationship
from backend.database import Base

class UserRole(str, enum.Enum):
    FARMER = "FARMER"
    VENDOR = "VENDOR"
    ADMIN = "ADMIN"

class ProductCategory(str, enum.Enum):
    SEEDS = "SEEDS"
    FERTILIZER = "FERTILIZER"
    PESTICIDE = "PESTICIDE"

class EquipmentType(str, enum.Enum):
    TRACTOR = "TRACTOR"
    ROTAVATOR = "ROTAVATOR"
    HARVESTER = "HARVESTER"
    CULTIVATOR = "CULTIVATOR"
    SEED_DRILL = "SEED_DRILL"
    SPRAYER = "SPRAYER"

class RateUnit(str, enum.Enum):
    HOUR = "HOUR"
    DAY = "DAY"

class BookingStatus(str, enum.Enum):
    CONFIRMATION_PENDING = "CONFIRMATION_PENDING"
    QUEUED = "QUEUED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"

class OrderStatus(str, enum.Enum):
    PLACED = "PLACED"
    CONFIRMED = "CONFIRMED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    phone = Column(String(30), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.FARMER, nullable=False)
    is_equipment_owner = Column(Boolean, default=False, nullable=False)
    location = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    products = relationship("Product", back_populates="vendor")
    orders = relationship("Order", back_populates="farmer")
    cart_items = relationship("CartItem", back_populates="farmer")
    equipment = relationship("Equipment", back_populates="owner")
    bookings = relationship("BookingRequest", back_populates="farmer")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), index=True, nullable=False)
    category = Column(Enum(ProductCategory), nullable=False, index=True)
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0, nullable=False)
    image_url = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    vendor = relationship("User", back_populates="products")
    cart_items = relationship("CartItem", back_populates="product", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product")

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PLACED, nullable=False)
    delivery_address = Column(String(500), nullable=False)
    razorpay_order_id = Column(String(255), nullable=True)
    razorpay_payment_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), index=True, nullable=False)
    type = Column(Enum(EquipmentType), nullable=False, index=True)
    description = Column(Text, nullable=False)
    specifications = Column(Text, nullable=False)
    rate = Column(Float, nullable=False)
    rate_unit = Column(Enum(RateUnit), default=RateUnit.HOUR, nullable=False)
    location = Column(String(255), nullable=False, index=True)
    image_url = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="equipment")
    bookings = relationship("BookingRequest", back_populates="equipment", cascade="all, delete-orphan")

class BookingRequest(Base):
    __tablename__ = "booking_requests"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.CONFIRMATION_PENDING, nullable=False, index=True)
    queue_position = Column(Integer, nullable=True)
    confirmation_deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("User", back_populates="bookings")
    equipment = relationship("Equipment", back_populates="bookings")
