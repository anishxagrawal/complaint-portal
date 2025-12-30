from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional, List
from app.enums import UserRole


# =====================================================
# BASE USER SCHEMA (shared fields)
# =====================================================
class UserBase(BaseModel):
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        examples=["John Doe"]
    )

    phone_number: str = Field(
        ...,
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

    @validator("full_name")
    def validate_full_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty")
        if not any(char.isalpha() for char in v):
            raise ValueError("Name must contain at least one letter")
        return v


# =====================================================
# USER CREATION SCHEMA
# NOTE:
# - role is included for admin-created users
# - public registration should override role in service
# =====================================================
class UserCreate(UserBase):
    role: UserRole = Field(
        default=UserRole.USER,
        description="User role in the system"
    )

    department: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Required if role is department_manager"
    )

    @validator("department", always=True)
    def validate_department(cls, v, values):
        role = values.get("role")

        # Department managers MUST have a department
        if role == UserRole.DEPARTMENT_MANAGER and not v:
            raise ValueError(
                "Department is required when role is 'department_manager'"
            )

        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Department cannot be empty")

        return v


# =====================================================
# USER RESPONSE SCHEMA (API output)
# =====================================================
class UserResponse(UserBase):
    id: int

    role: UserRole = Field(
        description="User role (admin / user / department_manager)"
    )

    department: Optional[str] = Field(
        default=None,
        description="Department managed by the user"
    )

    is_verified: bool

    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True  # Allows SQLAlchemy → Pydantic conversion


# =====================================================
# LOGIN REQUEST SCHEMA
# =====================================================
class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


# =====================================================
# LOGIN RESPONSE SCHEMA
# =====================================================
class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# =====================================================
# USER LIST RESPONSE (admin / manager use)
# =====================================================
class UserListResponse(BaseModel):
    count: int
    data: List[UserResponse]

# =====================================================
# USER ROLE UPDATE SCHEMA (Admin only operation)
# =====================================================
class UserRoleUpdate(BaseModel):
    """
    Schema for updating a user's role.
    
    Used by ADMIN to promote/change user roles.
    If setting role to DEPARTMENT_MANAGER, department is required.
    """
    role: UserRole = Field(
        ...,
        description="New role for the user"
    )
    
    department: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Required if new role is department_manager"
    )
    
    @validator("department", always=True)
    def validate_department_for_role(cls, v, values):
        """Ensure department is provided when role is DEPARTMENT_MANAGER"""
        role = values.get("role")
        
        # Department managers MUST have a department
        if role == UserRole.DEPARTMENT_MANAGER and not v:
            raise ValueError(
                "Department is required when role is 'department_manager'"
            )
        
        # Clean up department string if provided
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Department cannot be empty string")
        
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "department_manager",
                "department": "Public Works"
            }
        }