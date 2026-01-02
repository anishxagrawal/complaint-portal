#app/schemas/auth.py

from pydantic import BaseModel, EmailStr
from typing import Optional


class SignupRequest(BaseModel):
    """Schema for user signup."""
    email: EmailStr
    password: str
    name: str


class SendOTPRequest(BaseModel):
    """Schema for resending OTP to email for verification."""
    email: EmailStr


class VerifyOTPRequest(BaseModel):
    """Schema for verifying OTP code for email verification."""
    email: EmailStr
    otp_code: str


class LoginRequest(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class MessageResponse(BaseModel):
    """Generic response with message and email."""
    message: str
    email: str


class Token(BaseModel):
    """JWT token with type."""
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Decoded token payload."""
    user_id: Optional[int] = None