from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas.user import UserCreate, UserResponse, UserLogin, UserLoginResponse, UserListResponse
from app.services.user_service import UserService  # ✅ IMPORT SERVICE
from app.deps import get_db

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # ✅ Just call service, no logic here
    return UserService.create(user, db)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    # ✅ Just call service, no logic here
    return UserService.get_by_id(user_id, db)


@router.get("/", response_model=UserListResponse)
def list_users(db: Session = Depends(get_db)):
    users = UserService.list_all(db)
    # ✅ Return standardized format with count
    return {
        "count": len(users),
        "data": users
    }
