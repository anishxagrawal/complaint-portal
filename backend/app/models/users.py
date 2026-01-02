# app/models/users.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from datetime import datetime
from app.database import Base
from app.enums import UserRole  

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Basic user details
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

    # 🔐 AUTH FIELDS
    # Password-based login (OTP is NOT used for login)
    hashed_password = Column(String, nullable=False)

    # Verification status
    # True only after successful email OTP verification
    is_verified = Column(Boolean, default=False, nullable=False)

    # Login abuse protection
    failed_login_attempts = Column(Integer, default=0)            # Track failed password login attempts
    login_locked_until = Column(DateTime, nullable=True)          # Temporarily lock account after repeated failures

    # 🧑 ROLE & DEPARTMENT
    role = Column(
        Enum(UserRole),
        default=UserRole.USER,
        nullable=False,
        index=True  # ← Index for fast role-based queries
    )

    department = Column(
        String(100),
        nullable=True,
        index=True  # ← Index for fast department-based queries
    )

    # 📧 EMAIL OTP FIELDS (USED ONLY FOR VERIFICATION)
    otp_secret = Column(String, nullable=True)                    # Secret for generating OTP
    otp_expires_at = Column(DateTime, nullable=True)              # When OTP expires
    failed_otp_attempts = Column(Integer, default=0)              # Count failed attempts
    otp_locked_until = Column(DateTime, nullable=True)            # Lock after too many failures

    # Time Stamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # HELPER METHODS
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN
    
    def is_department_manager(self) -> bool:
        return self.role == UserRole.DEPARTMENT_MANAGER
    
    def is_regular_user(self) -> bool:
        return self.role == UserRole.USER
    
    def can_manage_department(self, department: str) -> bool:
        # Admins can manage any department
        if self.is_admin():
            return True
        
        # Department managers can only manage their assigned department
        if self.is_department_manager() and self.department == department:
            return True
        
        # Everyone else cannot manage any department
        return False
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"