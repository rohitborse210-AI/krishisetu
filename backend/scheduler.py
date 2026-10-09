import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import BookingRequest, BookingStatus
from backend.config import settings

logger = logging.getLogger("krishisetu.scheduler")

def process_expired_bookings():
    """
    APScheduler Background Task:
    1. Scans for bookings in CONFIRMATION_PENDING past their 24-hour deadline.
    2. Marks them as EXPIRED.
    3. Promotes the next QUEUED booking for the same equipment and dates.
    """
    db: Session = SessionLocal()
    now = datetime.utcnow()
    try:
        expired_bookings = (
            db.query(BookingRequest)
            .filter(
                BookingRequest.status == BookingStatus.CONFIRMATION_PENDING,
                BookingRequest.confirmation_deadline < now,
            )
            .all()
        )

        for booking in expired_bookings:
            logger.info(f"Booking {booking.id} expired past deadline: {booking.confirmation_deadline}")
            booking.status = BookingStatus.EXPIRED

            # Find next in queue for this equipment with overlapping dates
            next_in_queue = (
                db.query(BookingRequest)
                .filter(
                    BookingRequest.equipment_id == booking.equipment_id,
                    BookingRequest.status == BookingStatus.QUEUED,
                    BookingRequest.start_date < booking.end_date,
                    BookingRequest.end_date > booking.start_date,
                )
                .order_by(BookingRequest.queue_position.asc(), BookingRequest.created_at.asc())
                .first()
            )

            if next_in_queue:
                logger.info(f"Promoting queued booking {next_in_queue.id} to CONFIRMATION_PENDING")
                next_in_queue.status = BookingStatus.CONFIRMATION_PENDING
                next_in_queue.queue_position = None
                next_in_queue.confirmation_deadline = now + timedelta(
                    hours=settings.BOOKING_CONFIRMATION_HOURS
                )

        db.commit()
    except Exception as e:
        logger.error(f"Error in APScheduler process_expired_bookings: {e}")
        db.rollback()
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Runs every 1 minute to check for expired booking deadlines
    scheduler.add_job(process_expired_bookings, "interval", minutes=1, id="check_expired_bookings")
    scheduler.start()
    logger.info("APScheduler initialized for Krishisetu FCFS booking queues.")
    return scheduler
