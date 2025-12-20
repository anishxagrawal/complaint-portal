from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas.user import UserCreate, UserResponse
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


@router.get("/", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db)):
    # ✅ Just call service, no logic here
    return UserService.list_all(db)
