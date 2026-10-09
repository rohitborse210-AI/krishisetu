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
        if db.query(User).first():
            print("Database already contains data. Skipping seed.")
            return

        print("Seeding Krishisetu database with 7 users, 14 products, and 10 machinery items...")

        pw_hash = get_password_hash("password123")

        # 1. Users (IDs 1..7)
        users = [
            User(
                name="Ramesh Kumar (Farmer & Owner)",
                email="farmer@krishisetu.com",
                hashed_password=pw_hash,
                phone="9876543210",
                role=UserRole.FARMER,
                is_equipment_owner=True,
                location="Nashik, Maharashtra",
            ),
            User(
                name="Suresh Patil (Farmer & Owner)",
                email="farmer2@krishisetu.com",
                hashed_password=pw_hash,
                phone="9876543211",
                role=UserRole.FARMER,
                is_equipment_owner=True,
                location="Pune, Maharashtra",
            ),
            User(
                name="AgriCorp Agro Chemicals",
                email="vendor@krishisetu.com",
                hashed_password=pw_hash,
                phone="9876543220",
                role=UserRole.VENDOR,
                is_equipment_owner=False,
                location="Nagpur, Maharashtra",
            ),
            User(
                name="Krishisetu Administrator",
                email="admin@krishisetu.com",
                hashed_password=pw_hash,
                phone="9876543230",
                role=UserRole.ADMIN,
                is_equipment_owner=False,
                location="Mumbai, Maharashtra",
            ),
            User(
                name="Kisan Krishi Seva Kendra",
                email="vendor2@krishisetu.com",
                hashed_password=pw_hash,
                phone="9823114455",
                role=UserRole.VENDOR,
                is_equipment_owner=False,
                location="Kolhapur, Maharashtra",
            ),
            User(
                name="Godavari Irrigation & Farm Tech",
                email="vendor3@krishisetu.com",
                hashed_password=pw_hash,
                phone="9850223344",
                role=UserRole.VENDOR,
                is_equipment_owner=False,
                location="Ahmednagar, Maharashtra",
            ),
            User(
                name="Vikram Deshmukh (Machinery Owner)",
                email="owner3@krishisetu.com",
                hashed_password=pw_hash,
                phone="9890445566",
                role=UserRole.FARMER,
                is_equipment_owner=True,
                location="Satara, Maharashtra",
            ),
        ]
        db.add_all(users)
        db.commit()
        for u in users:
            db.refresh(u)

        farmer1, farmer2, vendor1, admin1, vendor2, vendor3, owner3 = users

        # 2. Products (14 realistic items across SEEDS, FERTILIZER, PESTICIDE, IRRIGATION, SPRAYER)
        products = [
            Product(
                vendor_id=vendor1.id,
                name="Certified Golden Wheat Seeds - HD 2967 (50kg Sack)",
                category=ProductCategory.SEEDS,
                description="ICAR-certified high-yield, yellow-rust resistant wheat seed variety suitable for irrigated and timely sown conditions across northern and central plains. Germination rate above 96%.",
                price=1650.0,
                stock=95,
                availability_status="IN_STOCK",
                image_url="/assets/images/wheat_seeds_sack_1791500903435.jpg",
            ),
            Product(
                vendor_id=vendor2.id,
                name="Royal Harvest Pusa-1121 Basmati Paddy Seeds (25kg)",
                category=ProductCategory.SEEDS,
                description="Extra-long slender grain aromatic Basmati paddy seeds with high market value, strong culm strength, and superior milling recovery. Ideal for Kharif transplanting.",
                price=2150.0,
                stock=64,
                availability_status="IN_STOCK",
                image_url="/assets/images/basmati_paddy_seeds_1791500920007.jpg",
            ),
            Product(
                vendor_id=vendor1.id,
                name="Progeny F1 Hybrid Bt Cotton Seeds - ACT-777 (450g)",
                category=ProductCategory.SEEDS,
                description="Cruiser-Plus systemic fungicide & insecticide treated F1 hybrid cotton seeds with big boll size, high ginning percentage, and tolerance against pink bollworm and jassids.",
                price=860.0,
                stock=120,
                availability_status="IN_STOCK",
                image_url="/assets/images/hybrid_cotton_seeds_1791500931145.jpg",
            ),
            Product(
                vendor_id=vendor2.id,
                name="High-Yield Hybrid Maize & JS-9560 Soybean Combo (25kg)",
                category=ProductCategory.SEEDS,
                description="Certified bold-seeded yellow maize and high-oil JS-9560 soybean foundation seeds. Features drought tolerance, early maturity (95 days), and shatter-resistant pods.",
                price=1920.0,
                stock=48,
                availability_status="IN_STOCK",
                image_url="/assets/images/soybean_maize_seeds_1791500943314.jpg",
            ),
            Product(
                vendor_id=vendor1.id,
                name="GrowMax NPK 19:19:19 100% Water Soluble Fertilizer (25kg)",
                category=ProductCategory.FERTILIZER,
                description="Free-flowing crystalline balanced macronutrient formula (19% N, 19% P, 19% K) for drip fertigation and foliar spray. Boosts vegetative branching, root vigor, and fruit setting.",
                price=1850.0,
                stock=72,
                availability_status="IN_STOCK",
                image_url="/assets/images/npk_fertilizer_bag_1791500953747.jpg",
            ),
            Product(
                vendor_id=vendor2.id,
                name="Krishi Neem Coated Urea 46% Nitrogen Fertilizer (45kg)",
                category=ProductCategory.FERTILIZER,
                description="Government-grade prilled urea coated with natural neem oil to slow nitrification, prevent leaching loss, and deliver sustained nitrogen nutrition to cereal and cash crops.",
                price=268.0,
                stock=310,
                availability_status="IN_STOCK",
                image_url="/assets/images/neem_coated_urea_1791500964626.jpg",
            ),
            Product(
                vendor_id=vendor1.id,
                name="Granular DAP (18:46:0) & Zinc Sulphate 33% Combo Pack (50kg)",
                category=ProductCategory.FERTILIZER,
                description="Basal dose Di-Ammonium Phosphate paired with Zinc Sulphate Monohydrate 33% to eliminate Khaira disease in paddy and establish deep root architecture in wheat and sugarcane.",
                price=1580.0,
                stock=55,
                availability_status="IN_STOCK",
                image_url="/assets/images/dap_zinc_fertilizer_1791500980608.jpg",
            ),
            Product(
                vendor_id=vendor2.id,
                name="Eco-Gro Enriched Organic Vermicompost & Bio-Potash (50kg)",
                category=ProductCategory.FERTILIZER,
                description="Earthworm-processed humus-rich organic manure blended with mobilized bio-potash granules and Trichoderma viride. Improves soil water retention, aeration, and microbial life.",
                price=540.0,
                stock=140,
                availability_status="IN_STOCK",
                image_url="/assets/images/organic_vermicompost_potash_1791500991903.jpg",
            ),
            Product(
                vendor_id=vendor1.id,
                name="Cold-Pressed Azadirachtin 10000 ppm Neem Oil Bio-Pesticide (5L)",
                category=ProductCategory.PESTICIDE,
                description="100% organic botanical antifeedant and insect growth regulator effective against whiteflies, aphids, thrips, mites, and leaf miners without harming beneficial pollinators.",
                price=1120.0,
                stock=68,
                availability_status="IN_STOCK",
                image_url="/assets/images/neem_oil_biopesticide_1791501004700.jpg",
            ),
            Product(
                vendor_id=vendor1.id,
                name="CropShield Systemic Fungicide & Broad-Spectrum Insecticide Kit (1L)",
                category=ProductCategory.PESTICIDE,
                description="Dual-action systemic crop protection pack containing Azoxystrobin + Tebuconazole fungicide and Thiamethoxam insecticide for rapid control of blight, rust, and stem borers.",
                price=890.0,
                stock=42,
                availability_status="IN_STOCK",
                image_url="/assets/images/crop_fungicide_insecticide_1791501015614.jpg",
            ),
            Product(
                vendor_id=vendor3.id,
                name="DripLine 16mm Inline HDPE Irrigation Pipe Coil & Valve Kit (300m)",
                category=ProductCategory.IRRIGATION,
                description="UV-stabilized Virgin Grade PE-100 HDPE drip irrigation lateral coil with pre-fitted cylindrical emitters at 40cm spacing, PVC ball valves, and brass impact sprinkler heads.",
                price=3450.0,
                stock=28,
                availability_status="IN_STOCK",
                image_url="/assets/images/hdpe_irrigation_pipes_1791501025898.jpg",
            ),
            Product(
                vendor_id=vendor3.id,
                name="AgriFlow 110mm Quick-Connect PVC Sprinkler Pipes & Brass Rain Gun",
                category=ProductCategory.IRRIGATION,
                description="Heavy-duty ISI-marked 6 kg/cm² quick-coupled PVC portable irrigation pipes (6m lengths) with galvanized latch couplers and a 1.5-inch adjustable brass rain gun on tripod stand.",
                price=5800.0,
                stock=19,
                availability_status="IN_STOCK",
                image_url="/assets/images/rain_gun_sprinkler_pipes_1791501234370.jpg",
            ),
            Product(
                vendor_id=vendor3.id,
                name="FarmQuip 16L 12V-8Ah Li-Ion Battery Knapsack Sprayer with Brass Lance",
                category=ProductCategory.SPRAYER,
                description="High-pressure diaphragm pump rechargeable knapsack sprayer capable of spraying 18–20 tanks per charge. Includes telescopic brass lance, pressure regulator gauge, and 4-nozzle set.",
                price=2650.0,
                stock=34,
                availability_status="IN_STOCK",
                image_url="/assets/images/battery_knapsack_sprayer_1791501046903.jpg",
            ),
            Product(
                vendor_id=vendor3.id,
                name="Solo 435 Petrol Motorized Knapsack Mist Blower & Duster Sprayer (20L)",
                category=ProductCategory.SPRAYER,
                description="2-stroke 42cc petrol engine motorized orchard mist blower reaching up to 11 meters horizontal spray throw. Ideal for mango, pomegranate, vineyard, and tall field crops.",
                price=7400.0,
                stock=8,
                availability_status="LOW_STOCK",
                image_url="/assets/images/power_mist_blower_sprayer_1791501245816.jpg",
            ),
        ]
        db.add_all(products)

        # 3. Equipment (10 realistic machinery items)
        equipment = [
            Equipment(
                owner_id=farmer1.id,
                name="Mahindra 575 DI XP Plus 50 HP 4WD Tractor",
                type=EquipmentType.TRACTOR,
                description="High-torque 4-cylinder ELS diesel tractor with ROPS canopy, power steering, and heavy-duty ADDC hydraulic lift. Well-maintained and ready for deep ploughing, puddling, and haulage.",
                specifications="50 HP Engine | 4WD Front Axle | Dual Clutch | 1800 kg Hydraulic Lift | Oil Immersed Brakes",
                rate=650.0,
                rate_unit=RateUnit.HOUR,
                location="Nashik, Maharashtra",
                stock_quantity=2,
                availability_status="AVAILABLE",
                image_url="/assets/images/mahindra_red_tractor_1791501058296.jpg",
            ),
            Equipment(
                owner_id=farmer2.id,
                name="John Deere 5310 PowerTech 55 HP 4WD Utility Tractor",
                type=EquipmentType.TRACTOR,
                description="Turbocharged 55 HP 4-wheel-drive tractor featuring collar-shift gearbox, planetary gear reduction, and independent PTO for heavy-duty laser leveling and baler operations.",
                specifications="55 HP @ 2400 RPM | 9F + 3R CollarShift | 2000 kg Lift Capacity | Dual-RPM PTO (540/540E)",
                rate=780.0,
                rate_unit=RateUnit.HOUR,
                location="Pune, Maharashtra",
                stock_quantity=1,
                availability_status="AVAILABLE",
                image_url="/assets/images/john_deere_green_tractor_1791501071564.jpg",
            ),
            Equipment(
                owner_id=owner3.id,
                name="New Holland 5500 Turbo Super 48 HP Tractor with Canopy",
                type=EquipmentType.TRACTOR,
                description="Fuel-efficient 3-cylinder tractor with sun canopy, front counterweight ballast, and synchromesh transmission. Ideal for inter-cultivation, rotavator tillage, and trolley transport.",
                specifications="48 HP Engine | 8F + 2R Constant Mesh | 1700 kg Sensomatic24 Hydraulics | Power Steering",
                rate=580.0,
                rate_unit=RateUnit.HOUR,
                location="Satara, Maharashtra",
                stock_quantity=2,
                availability_status="AVAILABLE",
                image_url="/assets/images/swaraj_blue_tractor_1791501084071.jpg",
            ),
            Equipment(
                owner_id=farmer1.id,
                name="Maschio Gaspardo Virat Pro 7 Feet Heavy Duty Rotavator",
                type=EquipmentType.ROTAVATOR,
                description="Multi-speed gear-driven rotary tiller with boron steel curved L-blades that pulverizes clods, incorporates crop residue, and prepares a fine seedbed in a single pass.",
                specifications="7 Feet Working Width | 48 Boron Steel L-Blades | Multi-Speed Gearbox (540/1000 RPM) | Side Gear Drive",
                rate=420.0,
                rate_unit=RateUnit.HOUR,
                location="Nashik, Maharashtra",
                stock_quantity=3,
                availability_status="AVAILABLE",
                image_url="/assets/images/rotavator_rotary_tiller_1791501094685.jpg",
            ),
            Equipment(
                owner_id=farmer2.id,
                name="John Deere W70 Self-Propelled Multi-Crop Combine Harvester",
                type=EquipmentType.HARVESTER,
                description="High-throughput self-propelled combine harvester with air-conditioned operator cabin, 14-foot header reel, and 6-straw-walker threshing system for wheat, soybean, and gram.",
                specifications="100 HP Turbocharged Engine | 14 Ft Cutter Bar | 2700L Grain Tank | Posi-Torq Drive",
                rate=1950.0,
                rate_unit=RateUnit.HOUR,
                location="Pune, Maharashtra",
                stock_quantity=1,
                availability_status="HIGH_DEMAND",
                image_url="/assets/images/combine_harvester_machine_1791501105447.jpg",
            ),
            Equipment(
                owner_id=owner3.id,
                name="Yanmar YH600 Rubber-Track Paddy Combine Harvester",
                type=EquipmentType.HARVESTER,
                description="Specialized rubber-crawler combine harvester engineered for wet and muddy paddy fields. Delivers ultra-low grain breakage and high-speed harvesting without soil compaction.",
                specifications="65 HP Diesel Engine | Rubber Crawler Tracks | 2.1m Reaping Width | Auto-Leveling Auger",
                rate=1750.0,
                rate_unit=RateUnit.HOUR,
                location="Kolhapur, Maharashtra",
                stock_quantity=1,
                availability_status="AVAILABLE",
                image_url="/assets/images/paddy_combine_harvester_1791501270303.jpg",
            ),
            Equipment(
                owner_id=farmer1.id,
                name="Fieldking 9-Tyne Spring Loaded Cultivator & Reversible MB Plough",
                type=EquipmentType.CULTIVATOR,
                description="Heavy-duty spring-loaded 9-tyne cultivator paired with a 2-bottom hydraulic reversible mould-board plough for breaking hardpan, aerating sub-soil, and uprooting stubborn weeds.",
                specifications="9 Heavy Duty Tynes | Twin-Spring Overload Protection | Reversible High-Carbon Shares | Cat-II Hitch",
                rate=320.0,
                rate_unit=RateUnit.HOUR,
                location="Nashik, Maharashtra",
                stock_quantity=4,
                availability_status="AVAILABLE",
                image_url="/assets/images/spring_tyne_cultivator_1791501117714.jpg",
            ),
            Equipment(
                owner_id=farmer2.id,
                name="FarmPower 9-Row Zero-Till Multi-Crop Seed Cum Fertilizer Drill",
                type=EquipmentType.SEED_DRILL,
                description="Precision zero-tillage seed and fertilizer drill that sows wheat, soybean, maize, and pulses directly into crop stubble while banding basal fertilizer at calibrated depth.",
                specifications="9 Rows | Inverted-T Furrow Openers | Dual Compartment Hopper | Ground-Wheel Chain Drive",
                rate=400.0,
                rate_unit=RateUnit.HOUR,
                location="Ahmednagar, Maharashtra",
                stock_quantity=2,
                availability_status="AVAILABLE",
                image_url="/assets/images/seed_cum_fertilizer_drill_1791501128600.jpg",
            ),
            Equipment(
                owner_id=farmer1.id,
                name="Aspee HTP 500L Tractor Mounted Hydraulic Boom Sprayer",
                type=EquipmentType.SPRAYER,
                description="High-volume tractor PTO-driven boom sprayer with a 40-foot foldable aluminum-steel truss boom and 28 anti-drift hollow-cone nozzles for rapid, uniform foliar application.",
                specifications="500L UV-Stabilized Tank | 40 Ft Folding Boom | 3-Piston Brass HTP Pump | 540 PTO Drive",
                rate=380.0,
                rate_unit=RateUnit.HOUR,
                location="Nashik, Maharashtra",
                stock_quantity=2,
                availability_status="AVAILABLE",
                image_url="/assets/images/tractor_boom_sprayer_1791501140854.jpg",
            ),
            Equipment(
                owner_id=owner3.id,
                name="Apogee AP-20 Automatic Laser Guided Land Leveler Bucket",
                type=EquipmentType.PLOUGH_LEVELER,
                description="Precision laser-guided drag bucket leveler with rotary laser transmitter and mast receiver. Saves up to 35% irrigation water and ensures uniform crop stand across fields.",
                specifications="7 Feet Scraper Bucket | 800m Laser Range | ±2mm Leveling Accuracy | 12V Solenoid Hydraulic Valve",
                rate=550.0,
                rate_unit=RateUnit.HOUR,
                location="Satara, Maharashtra",
                stock_quantity=1,
                availability_status="AVAILABLE",
                image_url="/assets/images/laser_land_leveler_plough_1791501258441.jpg",
            ),
        ]
        db.add_all(equipment)
        db.commit()

        # 4. Bookings Demo (FCFS active booking + queued booking)
        now = datetime.utcnow()
        b1 = BookingRequest(
            farmer_id=farmer2.id,
            equipment_id=1,
            start_date=now + timedelta(days=1),
            end_date=now + timedelta(days=2),
            status=BookingStatus.CONFIRMATION_PENDING,
            confirmation_deadline=now + timedelta(hours=24),
            queue_position=1,
        )
        b2 = BookingRequest(
            farmer_id=farmer1.id,
            equipment_id=1,
            start_date=now + timedelta(days=1),
            end_date=now + timedelta(days=2),
            status=BookingStatus.QUEUED,
            queue_position=2,
            confirmation_deadline=None,
        )
        db.add_all([b1, b2])
        db.commit()

        print("Database seeded successfully with 7 users, 14 products, 10 equipment items, and 2 FCFS bookings!")
    finally:
        db.close()

if __name__ == "__main__":
    seed()

