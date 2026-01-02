#app/services/auth_services.py

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import User
from app.core.config import settings
from app.core.security import (
    create_access_token,
    verify_otp,
    generate_otp_secret,
    get_otp_code
)


class OTPNotSentError(Exception):
    """Raised when OTP was never sent or already expired."""
    pass


class InvalidOTPError(Exception):
    """Raised when OTP code is incorrect."""
    pass


class AccountLockedError(Exception):
    """Raised when too many failed attempts."""
    pass


class AuthService:
    """Service for authentication: OTP, tokens, etc."""
    
    def send_otp(self, db: Session, phone_number: str) -> dict:
        """Send OTP to user's phone."""
        # Find user by phone
        user = db.query(User).filter(User.phone_number == phone_number).first()
        
        if not user:
            raise ValueError(f"User with phone {phone_number} not found")
        
        # Check if account is locked (too many failed attempts)
        if user.otp_locked_until and datetime.utcnow() < user.otp_locked_until:
            raise AccountLockedError(
                f"Account locked. Try again at {user.otp_locked_until}"
            )
        
        # Generate new OTP secret
        otp_secret = generate_otp_secret()

        # ✅ Generate OTP code from secret
        otp_code = get_otp_code(otp_secret)

        # ✅ Print OTP in terminal (DEV ONLY)
        print(f"DEBUG OTP for {phone_number}: {otp_code}")
        
        # Set expiration: 5 minutes from now
        otp_expires_at = datetime.utcnow() + timedelta(
            minutes=settings.OTP_EXPIRE_MINUTES
        )
        
        # Store in database
        user.otp_secret = otp_secret
        user.otp_expires_at = otp_expires_at
        user.failed_otp_attempts = 0  # Reset failed attempts
        user.otp_locked_until = None
        
        db.commit()
        
        return {
            "message": f"OTP sent to {phone_number}",
            "phone_number": phone_number
        }
    
    
    def verify_otp(self, db: Session, phone_number: str, otp_code: str) -> dict:
        """Verify OTP and return JWT token."""
        # Find user by phone
        user = db.query(User).filter(User.phone_number == phone_number).first()
        
        if not user:
            raise ValueError(f"User with phone {phone_number} not found")
        
        # Check if account is locked
        if user.otp_locked_until and datetime.utcnow() < user.otp_locked_until:
            raise AccountLockedError(
                f"Account locked. Try again at {user.otp_locked_until}"
            )
        
        # Check if OTP was sent
        if not user.otp_secret:
            raise OTPNotSentError("No OTP sent. Request OTP first.")
        
        # Check if OTP is expired
        if datetime.utcnow() > user.otp_expires_at:
            raise OTPNotSentError("OTP expired. Request new OTP.")
        
        # Verify OTP code
        if not verify_otp(user.otp_secret, otp_code):
            # Increment failed attempts
            user.failed_otp_attempts += 1
            
            # Lock account after 5 failed attempts
            if user.failed_otp_attempts >= 5:
                user.otp_locked_until = datetime.utcnow() + timedelta(minutes=15)
                db.commit()
                raise AccountLockedError(
                    "Too many failed attempts. Account locked for 15 minutes."
                )
            
            db.commit()
            raise InvalidOTPError(
                f"Invalid OTP. {5 - user.failed_otp_attempts} attempts remaining."
            )
        
        # OTP is valid! Clear OTP data
        user.otp_secret = None
        user.otp_expires_at = None
        user.failed_otp_attempts = 0
        user.otp_locked_until = None
        user.is_verified = True  # Mark as verified
        db.commit()
        
        # Create JWT token
        access_token = create_access_token(
            data={"user_id": user.id}
        )
        
        return {
            "access_token": access_token,
            "token_type": "Bearer"
        }


# Create singleton instance
auth_service = AuthService()