from pydantic import BaseModel
from typing import Optional


class SendOTPRequest(BaseModel):
    """Schema for sending OTP to a phone number."""
    phone_number: str


class SendOTPResponse(BaseModel):
    """Schema for response after sending OTP."""
    message: str
    phone_number: str


class VerifyOTPRequest(BaseModel):
    """Schema for verifying OTP code."""
    phone_number: str
    otp_code: str


class VerifyOTPResponse(BaseModel):
    """Schema for response after verifying OTP."""
    access_token: str
    token_type: str


class Token(BaseModel):
    """JWT token with type."""
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Decoded token payload."""
    user_id: Optional[int] = None