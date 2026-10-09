import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.config import settings

logger = logging.getLogger("krishisetu.database")

DATABASE_URL = settings.sqlalchemy_database_url

# Support PostgreSQL as primary database, with graceful SQLite fallback if local PostgreSQL is not running
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    try:
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )
        # Test actual connection on startup if fallback isn't disabled
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        logger.warning(f"PostgreSQL connection failed ({exc}). Falling back to local SQLite database for portable execution.")
        fallback_url = "sqlite:///./krishisetu_demo.db"
        engine = create_engine(fallback_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

