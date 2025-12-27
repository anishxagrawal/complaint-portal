from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from datetime import datetime
from app.database import Base
from app.enums import UserRole  

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    phone_number = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    residential_address = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)

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

    # OTP fields
    otp_secret = Column(String, nullable=True)                    # Secret for generating OTP
    otp_expires_at = Column(DateTime, nullable=True)              # When OTP expires
    failed_otp_attempts = Column(Integer, default=0)              # Count failed attempts
    otp_locked_until = Column(DateTime, nullable=True)            # When to unlock after too many attempts

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
        return f"<User(id={self.id}, email={self.email}, role={self.role}, department={self.department})>"

