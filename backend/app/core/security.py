# app/core/security.py

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import pyotp
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ============================================
# PASSWORD FUNCTIONS (for future use)
# ============================================

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ============================================
# JWT TOKEN FUNCTIONS
# ============================================

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary with claims (e.g., {"user_id": 123})
        expires_delta: Custom expiration time
        
    Returns:
        Encoded JWT token as string
        
    Example:
        token = create_access_token({"user_id": 123})
        # Returns: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjN9..."
    """
    # Copy data to avoid modifying original
    to_encode = data.copy()

    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # Add expiration to token payload
    to_encode.update({"exp": expire})

    # Encode the token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload (dictionary with user_id, exp, etc)
        
    Raises:
        JWTError: If token is invalid, expired, or tampered
        
    Example:
        payload = verify_token("eyJhbGciOiJIUzI1NiIs...")
        user_id = payload.get("user_id")
    """
    try:
        # Decode and verify token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
    
        # Extract user_id from payload
        user_id = payload.get("user_id")
        
        # If no user_id, token is invalid
        if user_id is None:
            raise JWTError("No user_id in token")
        
        return payload
        
    except JWTError as e:
        # Token is invalid, expired, or tampered
        raise JWTError(f"Invalid token: {str(e)}")


# ============================================
# OTP HELPER FUNCTIONS
# ============================================

def generate_otp_secret() -> str:
    """
    Generate a random OTP secret.
    
    Returns:
        Base32 encoded secret string
        
    Example:
        secret = generate_otp_secret()
        # Returns: "JBSWY3DPEHPK3PXP"
    """
    return pyotp.random_base32()


def verify_otp(secret: str, otp_code: str) -> bool:
    """
    Verify if OTP code matches the secret.
    
    Args:
        secret: OTP secret stored in database
        otp_code: 6-digit code user provides
        
    Returns:
        True if code is valid, False otherwise
        
    Example:
        is_valid = verify_otp("JBSWY3DPEHPK3PXP", "123456")
    """
    totp = pyotp.TOTP(secret)
    # Verify with time window: current and previous 30-second window
    return totp.verify(otp_code, valid_window=1)


def get_otp_code(secret: str) -> str:
    """
    Get current OTP code from secret (for testing/debugging only).
    
    Args:
        secret: OTP secret
        
    Returns:
        Current 6-digit OTP code
    
    WARNING:
        Only use this in testing or admin functions.
        Normal users shouldn't have access to this.
    """
    totp = pyotp.TOTP(secret)
    return totp.now()