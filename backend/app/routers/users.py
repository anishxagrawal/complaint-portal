from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas.user import UserCreate, UserResponse, UserLogin, UserLoginResponse, UserListResponse
from app.services.user_service import UserService  # ✅ IMPORT SERVICE
from app.deps import get_db, get_current_user, get_current_admin, get_current_manager
from app.models.users import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse, status_code=201)
def create_user(
    user: UserCreate,
    current_user: User = Depends(get_current_admin),  # ← ADDED
    db: Session = Depends(get_db)
):
    # ✅ Only admins reach here
    # Non-admins get 403 automatically
    return UserService.create(user, db)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),  # ← ADDED
    db: Session = Depends(get_db)
):
    # ✅ Only authenticated users reach here
    
    # ✅ NEW: Check permissions
    # - Admins can view anyone
    # - Users can only view themselves
    if not (current_user.is_admin() or current_user.id == user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only view your own profile or need admin access"
        )
    
    return UserService.get_by_id(user_id, db)


@router.get("/", response_model=UserListResponse)
def list_users(
    current_user: User = Depends(get_current_manager),  # ← CHANGED
    db: Session = Depends(get_db)
):
    # ✅ Only managers and admins reach here
    # Users get 403 automatically
    
    # ✅ NEW: Role-based filtering
    if current_user.is_admin():
        # Admin sees ALL users
        users = UserService.list_all(db)
    else:
        # Manager sees only their department users
        users = db.query(User).filter(
            User.department == current_user.department
        ).all()
    
    return {
        "count": len(users),
        "data": users
    }