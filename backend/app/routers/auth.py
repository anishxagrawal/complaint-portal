# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.schemas.auth import (
    SendOTPRequest,
    SendOTPResponse,
    VerifyOTPRequest,
    VerifyOTPResponse
)
from app.services.auth_service import (
    auth_service,
    OTPNotSentError,
    InvalidOTPError,
    AccountLockedError
)
from app.core.logging import get_logger

# ==========================================
# Setup
# ==========================================

router = APIRouter(prefix="/auth", tags=["authentication"])
logger = get_logger(__name__)
limiter = Limiter(key_func=get_remote_address)

# ==========================================
# SEND OTP (Rate Limited: 5 per minute)
# ==========================================

@router.post("/send-otp/", response_model=SendOTPResponse)
@limiter.limit("5/minute")  # ✅ NEW: Rate limit
async def send_otp(
    request: Request,  # ✅ NEW: Required for rate limiting
    otp_request: SendOTPRequest,
    db: Session = Depends(get_db)
):
    """
    Send OTP to user's phone number.
    
    **Rate Limit:** 5 requests per minute per IP
    
    Steps:
    1. User sends phone number
    2. System generates 6-digit OTP
    3. OTP stored in database with 5-minute expiration
    4. Returns confirmation
    
    Args:
        request: FastAPI request (for rate limiting)
        otp_request: Contains phone_number (validated by Pydantic)
        db: Database session
        
    Returns:
        SendOTPResponse with message and phone_number
        
    Errors:
        404: User not found
        429: Too many requests (rate limit)
        400: Account is locked (too many failed attempts)
        
    Example:
        POST /auth/send-otp/
        {
            "phone_number": "+919876543210"
        }
        
        Response:
        {
            "message": "OTP sent to +919876543210",
            "phone_number": "+919876543210"
        }
    """
    try:
        logger.info(f"OTP request for phone: {otp_request.phone_number}")
        
        result = auth_service.send_otp(db, otp_request.phone_number)
        
        logger.info(f"✅ OTP sent successfully to {otp_request.phone_number}")
        return result
        
    except ValueError as e:
        # User not found
        logger.warning(f"User not found: {otp_request.phone_number}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
        
    except AccountLockedError as e:
        logger.warning(f"Account locked: {otp_request.phone_number}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error(f"❌ OTP send failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP"
        )

# ==========================================
# VERIFY OTP (Rate Limited: 10 per minute)
# ==========================================

@router.post("/verify-otp/", response_model=VerifyOTPResponse)
@limiter.limit("10/minute")  # ✅ NEW: Rate limit
async def verify_otp(
    request: Request,  # ✅ NEW: Required for rate limiting
    verify_request: VerifyOTPRequest,
    db: Session = Depends(get_db)
):
    """
    Verify OTP and return JWT access token.
    
    **Rate Limit:** 10 requests per minute per IP
    
    Steps:
    1. User sends phone number and 6-digit OTP code
    2. System verifies OTP matches
    3. System checks OTP isn't expired
    4. System checks failed attempts (brute force protection)
    5. If valid: Create JWT token, return it
    
    Args:
        request: FastAPI request (for rate limiting)
        verify_request: Contains phone_number and otp_code
        db: Database session
        
    Returns:
        VerifyOTPResponse with access_token and token_type
        
    Errors:
        404: User not found
        401: OTP is invalid or expired
        429: Too many requests (rate limit or account locked)
        
    Example:
        POST /auth/verify-otp/
        {
            "phone_number": "+919876543210",
            "otp_code": "123456"
        }
        
        Response:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
    """
    try:
        logger.info(f"OTP verification attempt for: {verify_request.phone_number}")
        
        result = auth_service.verify_otp(
            db,
            verify_request.phone_number,
            verify_request.otp_code
        )
        
        logger.info(f"✅ OTP verified successfully for {verify_request.phone_number}")
        return result
        
    except ValueError as e:
        # User not found
        logger.warning(f"User not found: {verify_request.phone_number}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
        
    except (OTPNotSentError, InvalidOTPError) as e:
        logger.warning(f"Invalid OTP: {verify_request.phone_number}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
        
    except AccountLockedError as e:
        logger.warning(f"Account locked: {verify_request.phone_number}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error(f"❌ OTP verification failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify OTP"
        )