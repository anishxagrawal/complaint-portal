from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

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

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/send-otp/", response_model=SendOTPResponse)
def send_otp(request: SendOTPRequest, db: Session = Depends(get_db)):
    """
    Send OTP to user's phone number.
    
    Steps:
    1. User sends phone number
    2. System generates 6-digit OTP
    3. OTP stored in database with 5-minute expiration
    4. Returns confirmation
    
    Args:
        request: Contains phone_number (validated by Pydantic)
        db: Database session
        
    Returns:
        SendOTPResponse with message and phone_number
        
    Errors:
        404: User not found
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
        result = auth_service.send_otp(db, request.phone_number)
        return result
        
    except ValueError as e:
        # User not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
        
    except AccountLockedError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )

@router.post("/verify-otp/", response_model=VerifyOTPResponse)
def verify_otp(
    request: VerifyOTPRequest,
    db: Session = Depends(get_db)
):
    """
    Verify OTP and return JWT access token.
    
    Steps:
    1. User sends phone number and 6-digit OTP code
    2. System verifies OTP matches
    3. System checks OTP isn't expired
    4. System checks failed attempts (brute force protection)
    5. If valid: Create JWT token, return it
    
    Args:
        request: Contains phone_number and otp_code (validated by Pydantic)
        db: Database session
        
    Returns:
        VerifyOTPResponse with access_token and token_type
        
    Errors:
        404: User not found
        401: OTP is invalid or expired
        429: Account is locked (too many failed attempts)
        
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
        result = auth_service.verify_otp(
            db,
            request.phone_number,
            request.otp_code
        )
        return result
        
    except ValueError as e:
        # User not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
        
    except (OTPNotSentError, InvalidOTPError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
        
    except AccountLockedError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )