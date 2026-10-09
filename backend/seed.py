from datetime import datetime, timedelta
from backend.database import SessionLocal, engine, Base
from backend.models import (
    User,
    UserRole,
    Product,
    ProductCategory,
    Equipment,
    EquipmentType,
    RateUnit,
    BookingRequest,
    BookingStatus,
)
from backend.auth import get_password_hash

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        if db.query(User).first():
            print("Database already contains data. Skipping seed.")
            return

        print("Seeding Krishisetu database...")

        # 1. Users
        farmer1 = User(
            name="Ramesh Kumar (Farmer & Owner)",
            email="farmer@krishisetu.com",
            hashed_password=get_password_hash("farmer123"),
            phone="9876543210",
            role=UserRole.FARMER,
            is_equipment_owner=True,
            location="Nashik, Maharashtra",
        )
        farmer2 = User(
            name="Suresh Patil (Farmer)",
            email="farmer2@krishisetu.com",
            hashed_password=get_password_hash("farmer123"),
            phone="9823456789",
            role=UserRole.FARMER,
            is_equipment_owner=False,
            location="Pune, Maharashtra",
        )
        vendor1 = User(
            name="Kisan Agro Krishi Kendra",
            email="vendor@krishisetu.com",
            hashed_password=get_password_hash("vendor123"),
            phone="9123456780",
            role=UserRole.VENDOR,
            is_equipment_owner=False,
            location="Nagpur, Maharashtra",
        )
        admin1 = User(
            name="Krishisetu Platform Admin",
            email="admin@krishisetu.com",
            hashed_password=get_password_hash("admin123"),
            phone="9999988888",
            role=UserRole.ADMIN,
            is_equipment_owner=False,
            location="Central Hub, New Delhi",
        )

        db.add_all([farmer1, farmer2, vendor1, admin1])
        db.commit()
        db.refresh(farmer1)
        db.refresh(vendor1)

        # 2. Products
        products = [
            Product(
                vendor_id=vendor1.id,
                name="Certified HD-2967 High Yield Wheat Seeds",
                category=ProductCategory.SEEDS,
                description="ICAR-certified rust-resistant wheat seed variety suitable for irrigated fertile loamy soils. Germination rate exceeds 95%.",
                price=450.0,
                stock=120,
                image_url="https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=800&auto=format&fit=crop&q=60",
            ),
            Product(
                vendor_id=vendor1.id,
                name="Neem Coated Urea (45 kg)",
                category=ProductCategory.FERTILIZER,
                description="Slow-release nitrogen fertilizer treated with natural neem oil extract to minimize nitrogen volatilization and boost soil microbiome.",
                price=268.0,
                stock=450,
                image_url="https://images.unsplash.com/photo-1585336261024-64ed7d013cd1?w=800&auto=format&fit=crop&q=60",
            ),
            Product(
                vendor_id=vendor1.id,
                name="NPK 19:19:19 100% Water Soluble Fertilizer",
                category=ProductCategory.FERTILIZER,
                description="Balanced macronutrient foliar spray and drip irrigation formulation for rapid absorption during vegetative and flowering phases.",
                price=180.0,
                stock=80,
                image_url="https://images.unsplash.com/photo-1628352081506-83c43123ed6d?w=800&auto=format&fit=crop&q=60",
            ),
            Product(
                vendor_id=vendor1.id,
                name="Broad-Spectrum Chlorpyrifos 20% EC",
                category=ProductCategory.PESTICIDE,
                description="Systemic contact insecticide targeted for termite, stem borer, and root grub control in paddy and cereal crops.",
                price=320.0,
                stock=65,
                image_url="https://images.unsplash.com/photo-1615811361523-6bd03d7748e7?w=800&auto=format&fit=crop&q=60",
            ),
        ]
        db.add_all(products)

        # 3. Equipment
        equipment = [
            Equipment(
                owner_id=farmer1.id,
                name="Mahindra 575 DI 45 HP Tractor",
                type=EquipmentType.TRACTOR,
                description="Fuel-efficient 4-cylinder engine tractor with power steering, dual clutch, and heavy-duty rear hydraulic lift capacity.",
                specifications="Engine: 45 HP | Fuel: Diesel | PTO: 39.8 HP | Hydraulics: 1600 kg capacity",
                rate=450.0,
                rate_unit=RateUnit.HOUR,
                location="Nashik, Maharashtra",
                image_url="https://images.unsplash.com/photo-1592878904946-b3cd8ae243d0?w=800&auto=format&fit=crop&q=60",
            ),
            Equipment(
                owner_id=farmer1.id,
                name="Shaktiman 7 Feet Heavy Duty Rotavator",
                type=EquipmentType.ROTAVATOR,
                description="Boron steel curved blades designed for effective seedbed preparation, soil pulverization, and crop stubble mixing.",
                specifications="Tillage Width: 7 Feet | Blades: 48 Boron Steel L-Type | Hitch: 3-Point Category II",
                rate=350.0,
                rate_unit=RateUnit.HOUR,
                location="Nashik, Maharashtra",
                image_url="https://images.unsplash.com/photo-1595838788414-b15c92c902ff?w=800&auto=format&fit=crop&q=60",
            ),
            Equipment(
                owner_id=farmer1.id,
                name="Preet 987 Self Propelled Combine Harvester",
                type=EquipmentType.HARVESTER,
                description="Multicrop combine harvester suitable for wheat, paddy, soybean, and mustard harvesting with minimal grain loss.",
                specifications="Cutter Bar: 14 Feet | Engine: 101 HP Ashok Leyland Turbo | Grain Tank: 2400 Liters",
                rate=2200.0,
                rate_unit=RateUnit.HOUR,
                location="Pune, Maharashtra",
                image_url="https://images.unsplash.com/photo-1589923188900-85dae523342b?w=800&auto=format&fit=crop&q=60",
            ),
        ]
        db.add_all(equipment)
        db.commit()

        # 4. Bookings Demo (FCFS active booking + queued booking)
        now = datetime.utcnow()
        b1 = BookingRequest(
            farmer_id=farmer1.id,
            equipment_id=1,
            start_date=now + timedelta(days=2),
            end_date=now + timedelta(days=4),
            status=BookingStatus.CONFIRMATION_PENDING,
            confirmation_deadline=now + timedelta(hours=24),
            queue_position=None,
        )
        b2 = BookingRequest(
            farmer_id=farmer2.id,
            equipment_id=1,
            start_date=now + timedelta(days=3),
            end_date=now + timedelta(days=5),
            status=BookingStatus.QUEUED,
            queue_position=1,
            confirmation_deadline=None,
        )
        db.add_all([b1, b2])
        db.commit()

        print("Database seeded successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
