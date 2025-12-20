from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):

    full_name: str = Field(
        ...,  # Required
        min_length=2,
        max_length=255,
        examples=["John Doe"]
    )  

    phone_number: str = Field(
        ..., # Required
        pattern=r"^\+91[6-9]\d{9}$",
        examples=["+919876543210"]
    )

    email: EmailStr

    residential_address: str = Field(
        ...,
        min_length=5,
        max_length=500,
        examples=["123 Main Street, New Delhi"] 
    )

    @validator('full_name')
    def validate_full_name(cls, v):
        # Remove extra spaces
        v = v.strip()
            
        # Check not empty after stripping
        if not v:
            raise ValueError("Name cannot be empty or just spaces")
            
        # Check has at least one letter
        if not any(char.isalpha() for char in v):
            raise ValueError("Name must contain at least one letter")
            
        return v

class UserCreate(UserBase):
    """
    Data required to create a user
    """
    pass

class UserResponse(UserBase):
    """
    Data returned by the API
    """
    id: int
    role: str
    is_verified: bool
    created_at: datetime
