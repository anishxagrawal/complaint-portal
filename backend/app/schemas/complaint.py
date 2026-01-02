#app/router/complaint.py

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
from typing import List


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
        from_attributes = True  # Tells Pydantic: "Convert SQLAlchemy model → JSON"

# ============================================
# NEW SCHEMAS (Add these for pagination)
# ============================================

class PaginationMetadata(BaseModel):

    page: int=Field(..., description="Current page number (1-indexed)")
    page_size: int=Field(..., description="Current page number (1-indexed)")
    total: int=Field(..., description="Total number of items across all pages")
    pages: int=Field(..., description="Total number of pages")
    has_next: int=Field(..., description="Whether there's a next page")
    has_prev: int=Field(..., description="Whether there's a previous page")

class PaginatedComplaintResponse(BaseModel):

    data: List[ComplaintResponse] = Field(..., description = "List of complaints for this page")
    pagination:  PaginationMetadata = Field(..., description = "Pagination Metadata")

# =====================================================
# COMPLAINT ASSIGNMENT SCHEMA (Admin/Manager operation)
# =====================================================
class ComplaintAssign(BaseModel):
    """
    Schema for assigning a complaint to a department.
    
    Used by ADMIN and DEPARTMENT_MANAGER to route complaints.
    - ADMIN can assign to any department
    - DEPT_MGR can only assign to their own department
    """
    department: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Department to assign the complaint to",
        examples=["Public Works", "Sanitation", "Water Supply"]
    )
    
    @validator('department')
    def validate_department(cls, v):
        """Clean and validate department name"""
        # Remove extra spaces
        v = v.strip()
        
        # Check not empty after stripping
        if not v:
            raise ValueError("Department cannot be empty or just spaces")
        
        # Ensure at least some alphabetic characters
        if not any(char.isalpha() for char in v):
            raise ValueError("Department must contain letters")
        
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "department": "Public Works"
            }
        }
