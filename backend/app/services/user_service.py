from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models.users import User
from app.schemas.user import UserCreate

class UserService:
    """Service layer for user operations"""
    
    @staticmethod
    def create(data: UserCreate, db: Session) -> User:
        """
        Create a new user
        - Check if email already exists
        - Save to database
        - Handle errors gracefully
        """
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == data.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists")
        
        # Try to create and save
        try:
            new_user = User(**data.dict())
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return new_user
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Failed to create user")
    
    @staticmethod
    def get_by_id(user_id: int, db: Session) -> User:
        """
        Get user by ID
        - Query database
        - Return 404 if not found
        """
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
    @staticmethod
    def list_all(db: Session) -> List[User]:
        """
        Get all users
        - Simple query
        - Return list
        """
        return db.query(User).all()