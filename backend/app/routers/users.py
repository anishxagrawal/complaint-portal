# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.user import (
    UserCreate, 
    UserResponse, 
    UserListResponse,
    UserRoleUpdate  # You'll need to create this schema
)
from app.services.user_service import UserService
from app.deps import get_db, get_current_user
from app.models.users import User

router = APIRouter(prefix="/users", tags=["Users"])


# ============================================
# CREATE USER (Admin only - checked in service)
# ============================================
@router.post("/", response_model=UserResponse, status_code=201)
def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),  # ← Just need authenticated user
    db: Session = Depends(get_db)
):
    """
    Create a new user (ADMIN only).
    
    Role check is done inside UserService.create()
    """
    # ✅ Service handles role checking internally
    return UserService.create(user_data, db, current_user)


# ============================================
# GET SINGLE USER (Role-aware - checked in service)
# ============================================
@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user by ID.
    
    Access control:
    - ADMIN: Can view any user
    - DEPT_MGR: Can view their department users
    - USER: Can only view themselves
    
    Role check is done inside UserService.get_by_id()
    """
    # ✅ Service handles role checking internally
    return UserService.get_by_id(user_id, db, current_user)


# ============================================
# LIST USERS (Role-aware - checked in service)
# ============================================
@router.get("/", response_model=UserListResponse)
def list_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List users (role-based filtering).
    
    Access control:
    - ADMIN: Sees all users
    - DEPT_MGR: Sees their department users
    - USER: Cannot list (403 error)
    
    Role check and filtering done inside UserService.list_all()
    """
    # ✅ Service handles role checking and filtering internally
    users = UserService.list_all(db, current_user)
    
    return {
        "count": len(users),
        "data": users
    }


# ============================================
# UPDATE USER ROLE (Admin only - checked in service)
# ============================================
@router.patch("/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    role_data: UserRoleUpdate,  # Schema: {role: str, department: Optional[str]}
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a user's role (ADMIN only).
    
    Role check is done inside UserService.update_user_role()
    """
    # ✅ Service handles role checking internally
    return UserService.update_user_role(
        target_user_id=user_id,
        new_role=role_data.role,
        new_department=role_data.department,
        db=db,
        admin_user=current_user
    )