from pydantic import BaseModel, Field, validator
from typing import Optional


class IssueTypeCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        examples=["Garbage and Waste"]
    )
    department_id: int = Field(..., gt=0)  # Must be > 0
    
    @validator('name')
    def validate_name(cls, v):
        # Remove extra spaces
        v = v.strip()
        
        # Check not empty after stripping
        if not v:
            raise ValueError("Issue type name cannot be empty or just spaces")
        
        return v


class IssueTypeResponse(BaseModel):
    id: int
    name: str
    department_id: int
    is_active: bool
    
    class Config:
        from_attributes = True  # For SQLAlchemy compatibility