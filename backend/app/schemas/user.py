from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    full_name: str
    phone_number: str
    email: EmailStr
    residential_address: str

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
