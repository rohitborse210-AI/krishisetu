# Krishisetu Backend (Python + FastAPI + PostgreSQL + SQLAlchemy + Alembic)

## 📌 Project Overview
Krishisetu is a comprehensive agricultural technology platform providing:
1. **Certified Inputs Marketplace**: Seeds, fertilizers, and crop protection chemicals with stock management.
2. **Machinery Sharing & Equipment Rental**: Tractors, rotavators, and harvesters with automated First-Come, First-Served (FCFS) slot scheduling.
3. **Razorpay Payments (Test Mode)**: Secure online order processing and signature verification.
4. **APScheduler Background Service**: Automated 24-hour deadline expiration and queue promotion.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+
- PostgreSQL (or local SQLite fallback)

### 2. Setup Virtual Environment
```bash
cd backend
python -m venv venv
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup & Migrations
Create PostgreSQL database:
```sql
CREATE DATABASE krishisetu_db;
```
Configure your connection string in `.env` or `config.py`:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/krishisetu_db
```
Apply Alembic migrations:
```bash
alembic upgrade head
```

### 5. Seed Demonstration Data
Pre-populates 4 users (Farmer/Owner, Farmer, Vendor, Admin), catalog products, and machinery:
```bash
python seed.py
```

### 6. Run FastAPI Server
```bash
uvicorn backend.main:app --reload --port 8000
```
- Interactive Swagger UI: `http://localhost:8000/docs`
- ReDoc Documentation: `http://localhost:8000/redoc`

---

## 🎯 BTech Viva Questions & Answers

### Q1: How does your First-Come, First-Served (FCFS) Booking Queue work?
**Answer**:
When a farmer requests to rent equipment for dates $[S, E]$:
1. The server checks for existing active bookings (`CONFIRMATION_PENDING` or `CONFIRMED`) where:
   `existing.start_date < requested.end_date AND existing.end_date > requested.start_date`
2. If **no overlap** exists, the slot is immediately granted with status `CONFIRMATION_PENDING` and a `confirmation_deadline` set to $24\text{ hours}$ from now.
3. If an overlap **does exist**, the request is placed into `QUEUED` status, assigned `queue_position = total_queued + 1`.
4. When an active booking is cancelled or expires past its 24-hour window, the background task (`APScheduler`) automatically promotes the booking with `queue_position = 1` to `CONFIRMATION_PENDING`.

### Q2: Why did you use APScheduler instead of Celery or Cron?
**Answer**:
APScheduler runs in-process inside Python without requiring an external message broker like Redis or RabbitMQ. For a college project scale, it provides accurate, lightweight interval execution while maintaining transaction safety.

### Q3: How is Razorpay Test Mode integrated?
**Answer**:
1. Client adds items to cart and requests order checkout.
2. Server initiates order creation via `razorpay.Client.order.create({ amount, currency: 'INR' })`.
3. Client completes test payment via Razorpay modal using test card or UPI credentials.
4. Server verifies HMAC-SHA256 signature: `HMAC_SHA256(order_id + "|" + payment_id, secret_key)` to confirm genuine payment capture before updating order status.

### Q4: How is Role-Based Access Control (RBAC) enforced?
**Answer**:
We use FastAPI dependency injection (`require_roles([UserRole.VENDOR])`) alongside JWT bearer tokens (`python-jose`). A farmer with `is_equipment_owner=True` can both buy products and rent out personal farm machinery.
