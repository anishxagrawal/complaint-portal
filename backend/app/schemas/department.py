from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional


class DepartmentCreate(BaseModel):

    name: str = Field(
        ...,  # Required
        min_length=3,
        max_length=255,
        examples=["Sanitation Department"]
    ) 

    @validator('name')
    def validate_name(cls, v):
        # Remove extra spaces
        v = v.strip()
            
        # Check not empty after stripping
        if not v:
            raise ValueError("Department name cannot be empty")
            
        # Optional: Check no special characters (only alphanumeric, spaces, hyphens)
        if not all(char.isalnum() or char.isspace() or char == '-' for char in v):
            raise ValueError("Department name can only contain letters, numbers, spaces, and hyphens")
            
        return v

class DepartmentResponse(BaseModel):
    id: int
    name: str
    is_active: bool

    class Config:
        from_attributes = True  # ✅ For SQLAlchemy compatibility