import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Krishisetu - Smart Agricultural Marketplace & Equipment Rental"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/krishisetu_db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "btech_krishisetu_super_secret_jwt_key_2026_safe")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Razorpay Test Credentials
    RAZORPAY_KEY_ID: str = os.getenv("RAZORPAY_KEY_ID", "rzp_test_KRISHISETU12345")
    RAZORPAY_KEY_SECRET: str = os.getenv("RAZORPAY_KEY_SECRET", "test_secret_krishisetu98765")
    
    # FCFS Rental Window Rules
    BOOKING_CONFIRMATION_HOURS: int = 24

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
