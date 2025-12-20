from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional


class ComplaintCreate(BaseModel):
    user_id: int = Field(..., gt=0)  # Greater than 0
    issue_type_id: int = Field(..., gt=0)  # Greater than 0
    description: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        examples=["Garbage overflowing on Main Street for 3 days"]
    )
    address: str = Field(
        ...,
        min_length=5,
        max_length=500,
        examples=["123 Main Street, New Delhi"]
    )
    
    @validator('description')
    def validate_description(cls, v):
        # Remove extra spaces
        v = v.strip()
        
        # Check not empty after stripping
        if not v:
            raise ValueError("Description cannot be empty or just spaces")
        
        return v
    
    @validator('address')
    def validate_address(cls, v):
        # Remove extra spaces
        v = v.strip()
        
        # Check not empty after stripping
        if not v:
            raise ValueError("Address cannot be empty or just spaces")
        
        return v


class ComplaintResponse(BaseModel):
    id: int
    user_id: int
    issue_type_id: int
    description: str
    address: str
    status: str
    urgency: str
    created_at: datetime
    
    class Config:
        from_attributes = True  # For SQLAlchemy compatibility