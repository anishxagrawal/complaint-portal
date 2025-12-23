from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    residential_address = Column(String, nullable=False)
    role = Column(String, default="USER")
    is_verified = Column(Boolean, default=False)

    # OTP fields (NEW)
    otp_secret = Column(String, nullable=True)                    # Secret for generating OTP
    otp_expires_at = Column(DateTime, nullable=True)              # When OTP expires
    failed_otp_attempts = Column(Integer, default=0)              # Count failed attempts
    otp_locked_until = Column(DateTime, nullable=True)            # When to unlock after too many attempts

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)





