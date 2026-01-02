# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
from datetime import datetime, timedelta

from app.database import get_db
from app.schemas.auth import (
    SignupRequest,
    SendOTPRequest,
    VerifyOTPRequest,
    LoginRequest,
    MessageResponse,
    Token
)
from app.services.auth_service import (
    auth_service,
    OTPNotSentError,
    InvalidOTPError,
    AccountLockedError
)
from app.models import User
from app.core.security import hash_password, verify_password, create_access_token
from app.core.logging import get_logger

# ==========================================
# Setup
# ==========================================

router = APIRouter(prefix="/auth", tags=["authentication"])
logger = get_logger(__name__)
limiter = Limiter(key_func=get_remote_address)

# ==========================================
# SIGNUP
# ==========================================

@router.post("/signup/", response_model=MessageResponse)
async def signup(
    signup_request: SignupRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    
    Steps:
    1. User sends email, password, and name
    2. System checks if email already exists
    3. Password is hashed and stored
    4. User created with is_verified = False
    5. User must verify email using /send-otp and /verify-otp
    
    Args:
        signup_request: Contains email, password, and name
        db: Database session
        
    Returns:
        MessageResponse with message and email
        
    Errors:
        409: Email already registered
        500: Server error
        
    Example:
        POST /auth/signup/
        {
            "email": "user@example.com",
            "password": "securepassword123",
            "name": "John Doe"
        }
        
        Response:
        {
            "message": "Account created. Please verify your email.",
            "email": "user@example.com"
        }
    """
    try:
        logger.info(f"Signup attempt for email: {signup_request.email}")
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == signup_request.email).first()
        if existing_user:
            logger.warning(f"Email already registered: {signup_request.email}")
            logger.warning(f"auth.signup.exists | email={signup_request.email}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = hash_password(signup_request.password)
        
        # Create new user
        new_user = User(
            email=signup_request.email,
            hashed_password=hashed_password,
            full_name=signup_request.name,
            is_verified=False
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"✅ User created successfully: {signup_request.email}")
        logger.info(f"auth.signup.success | email={signup_request.email}")
        
        return {
            "message": "Account created. Please verify your email.",
            "email": signup_request.email
        }
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"❌ Signup failed: {str(e)}", exc_info=True)
        logger.error(f"auth.signup.error | email={signup_request.email}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create account"
        )

# ==========================================
# SEND OTP (Rate Limited: 5 per minute)
# ==========================================

@router.post("/send-otp/", response_model=MessageResponse)
@limiter.limit("5/minute")  # ✅ NEW: Rate limit
async def send_otp(
    request: Request,  # ✅ NEW: Required for rate limiting
    otp_request: SendOTPRequest,
    db: Session = Depends(get_db)
):
    """
    Resend OTP to user's email for verification.
    
    **Rate Limit:** 5 requests per minute per IP
    
    Steps:
    1. User sends email
    2. System generates 6-digit OTP
    3. OTP stored in database with 5-minute expiration
    4. Returns confirmation
    
    Args:
        request: FastAPI request (for rate limiting)
        otp_request: Contains email (validated by Pydantic)
        db: Database session
        
    Returns:
        MessageResponse with message and email
        
    Errors:
        404: User not found
        429: Too many requests (rate limit)
        400: Account is locked (too many failed attempts)
        
    Example:
        POST /auth/send-otp/
        {
            "email": "user@example.com"
        }
        
        Response:
        {
            "message": "OTP sent to user@example.com",
            "email": "user@example.com"
        }
    """
    try:
        logger.info(f"OTP request for email: {otp_request.email}")
        
        result = auth_service.send_otp(db, otp_request.email)
        
        logger.info(f"✅ OTP sent successfully to {otp_request.email}")
        logger.info(f"auth.otp.sent | email={otp_request.email}")
        return result
        
    except ValueError as e:
        # User not found
        logger.warning(f"User not found: {otp_request.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
        
    except AccountLockedError as e:
        logger.warning(f"Account locked: {otp_request.email}")
        logger.warning(f"auth.otp.locked | email={otp_request.email}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error(f"❌ OTP send failed: {str(e)}", exc_info=True)
        logger.error(f"auth.otp.error | email={otp_request.email}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP"
        )

# ==========================================
# VERIFY OTP (Rate Limited: 10 per minute)
# ==========================================

@router.post("/verify-otp/", response_model=MessageResponse)
@limiter.limit("10/minute")  # ✅ NEW: Rate limit
async def verify_otp(
    request: Request,  # ✅ NEW: Required for rate limiting
    verify_request: VerifyOTPRequest,
    db: Session = Depends(get_db)
):
    """
    Verify OTP for email verification.
    
    **Rate Limit:** 10 requests per minute per IP
    
    Steps:
    1. User sends email and 6-digit OTP code
    2. System verifies OTP matches
    3. System checks OTP isn't expired
    4. System checks failed attempts (brute force protection)
    5. If valid: Mark email as verified
    
    Args:
        request: FastAPI request (for rate limiting)
        verify_request: Contains email and otp_code
        db: Database session
        
    Returns:
        MessageResponse with message and email
        
    Errors:
        404: User not found
        401: OTP is invalid or expired
        429: Too many requests (rate limit or account locked)
        
    Example:
        POST /auth/verify-otp/
        {
            "email": "user@example.com",
            "otp_code": "123456"
        }
        
        Response:
        {
            "message": "Email verified successfully",
            "email": "user@example.com"
        }
    """
    try:
        logger.info(f"OTP verification attempt for: {verify_request.email}")
        
        result = auth_service.verify_otp(
            db,
            verify_request.email,
            verify_request.otp_code
        )
        
        logger.info(f"✅ OTP verified successfully for {verify_request.email}")
        logger.info(f"auth.otp.verified | email={verify_request.email}")
        return result
        
    except ValueError as e:
        # User not found
        logger.warning(f"User not found: {verify_request.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
        
    except (OTPNotSentError, InvalidOTPError) as e:
        logger.warning(f"Invalid OTP: {verify_request.email}")
        logger.warning(f"auth.otp.failed | email={verify_request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
        
    except AccountLockedError as e:
        logger.warning(f"Account locked: {verify_request.email}")
        logger.warning(f"auth.otp.locked | email={verify_request.email}")
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

# ==========================================
# LOGIN (Rate Limited: 5 per minute)
# ==========================================

@router.post("/login/", response_model=Token)
@limiter.limit("5/minute")
async def login(
    request: Request,
    login_request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login with email and password.
    
    **Rate Limit:** 5 requests per minute per IP
    
    Steps:
    1. User sends email and password
    2. System looks up user by email
    3. System verifies email is verified
    4. System verifies password
    5. System generates JWT token
    
    Args:
        request: FastAPI request (for rate limiting)
        login_request: Contains email and password
        db: Database session
        
    Returns:
        Token with access_token and token_type
        
    Errors:
        401: Invalid credentials
        403: Email not verified
        429: Account locked or rate limit exceeded
        500: Server error
        
    Example:
        POST /auth/login/
        {
            "email": "user@example.com",
            "password": "securepassword123"
        }
        
        Response:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
    """
    try:
        logger.info(f"Login attempt for email: {login_request.email}")
        
        # Find user by email
        user = db.query(User).filter(User.email == login_request.email).first()
        
        if not user:
            logger.warning(f"User not found: {login_request.email}")
            logger.warning(f"auth.login.failed | email={login_request.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if account is locked
        if user.login_locked_until and datetime.utcnow() < user.login_locked_until:
            logger.warning(f"Account locked: {login_request.email}")
            logger.warning(f"auth.login.locked | email={login_request.email}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Account temporarily locked due to too many failed attempts"
            )
        
        # Check if email is verified
        if not user.is_verified:
            logger.warning(f"Email not verified: {login_request.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email not verified. Please verify your email first."
            )
        
        # Verify password
        if not verify_password(login_request.password, user.hashed_password):
            logger.warning(f"Invalid password for: {login_request.email}")
            logger.warning(f"auth.login.failed | email={login_request.email}")
            
            # Increment failed attempts
            user.failed_login_attempts += 1
            
            # Lock account after 5 failed attempts
            if user.failed_login_attempts >= 5:
                user.login_locked_until = datetime.utcnow() + timedelta(minutes=15)
                db.commit()
                logger.warning(f"auth.login.locked | email={login_request.email}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Account temporarily locked due to too many failed attempts"
                )
            
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Reset failed attempts on successful login
        user.failed_login_attempts = 0
        user.login_locked_until = None
        db.commit()
        
        # Create JWT token
        access_token = create_access_token(
            data={"user_id": user.id}
        )
        
        logger.info(f"✅ Login successful for {login_request.email}")
        logger.info(f"auth.login.success | email={login_request.email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"❌ Login failed: {str(e)}", exc_info=True)
        logger.error(f"auth.login.error | email={login_request.email}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )