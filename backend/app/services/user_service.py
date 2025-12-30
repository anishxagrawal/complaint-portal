# app/services/user_service.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models.users import User
from app.schemas.user import UserCreate
from app.enums import UserRole
from app.utils.audit_logger import audit_logger

class UserService:
    """Service layer for user operations with role-based access control"""
    
    @staticmethod
    def create(data: UserCreate, db: Session, admin_user: User) -> User:
        """
        Create a new user (ADMIN ONLY)
        
        Role Logic:
        - Only ADMIN can create users
        - If creating DEPARTMENT_MANAGER, department field is required
        - Logs the action for audit trail
        """
        # ✅ ROLE CHECK: Only admins can create users
        if admin_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=403,
                detail="Only administrators can create users"
            )
        
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == data.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists")
        
        # ✅ VALIDATION: DEPARTMENT_MANAGER must have department
        if data.role == UserRole.DEPARTMENT_MANAGER and not data.department:
            raise HTTPException(
                status_code=400,
                detail="Department is required for department managers"
            )
        
        try:
            new_user = User(**data.dict())
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            # ✅ AUDIT LOG
            audit_logger.log_action(
                user_id=admin_user.id,
                action="CREATE",
                resource_type="USER",
                resource_id=new_user.id,
                details=f"Created user with role {data.role}"
            )
            
            return new_user
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Failed to create user")
    
    @staticmethod
    def get_by_id(user_id: int, db: Session, current_user: User) -> User:
        """
        Get user by ID (ROLE-AWARE)
        
        Role Logic:
        - ADMIN: Can view any user
        - USER: Can only view themselves
        - DEPARTMENT_MANAGER: Can view users in their department
        """
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # ✅ ROLE-BASED ACCESS CHECK
        if current_user.role == UserRole.ADMIN:
            # Admin can view anyone
            pass
        elif current_user.role == UserRole.DEPARTMENT_MANAGER:
            # Manager can view their department or themselves
            if user.department != current_user.department and user.id != current_user.id:
                raise HTTPException(
                    status_code=403,
                    detail="Can only view users in your department"
                )
        elif current_user.role == UserRole.USER:
            # User can only view themselves
            if user.id != current_user.id:
                raise HTTPException(
                    status_code=403,
                    detail="Can only view your own profile"
                )
        
        # ✅ AUDIT LOG
        audit_logger.log_action(
            user_id=current_user.id,
            action="READ",
            resource_type="USER",
            resource_id=user_id
        )
        
        return user
    
    @staticmethod
    def list_all(db: Session, current_user: User) -> List[User]:
        """
        Get users list (ROLE-AWARE)
        
        Role Logic:
        - ADMIN: Sees all users
        - DEPARTMENT_MANAGER: Sees only users in their department
        - USER: Cannot list users (403 error)
        """
        # ✅ ROLE CHECK: Users cannot list
        if current_user.role == UserRole.USER:
            raise HTTPException(
                status_code=403,
                detail="Users cannot list other users"
            )
        
        # ✅ ROLE-BASED FILTERING
        if current_user.role == UserRole.ADMIN:
            # Admin sees everyone
            users = db.query(User).all()
        elif current_user.role == UserRole.DEPARTMENT_MANAGER:
            # Manager sees only their department
            users = db.query(User).filter(
                User.department == current_user.department
            ).all()
        else:
            users = []
        
        # ✅ AUDIT LOG
        audit_logger.log_action(
            user_id=current_user.id,
            action="LIST",
            resource_type="USER",
            details=f"Listed {len(users)} users"
        )
        
        return users
    
    @staticmethod
    def update_user_role(
        target_user_id: int,
        new_role: UserRole,
        new_department: str,
        db: Session,
        admin_user: User
    ) -> User:
        """
        Update user's role (ADMIN ONLY)
        
        Role Logic:
        - Only ADMIN can change user roles
        - If setting DEPARTMENT_MANAGER role, department is required
        """
        # ✅ ROLE CHECK: Only admins can change roles
        if admin_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=403,
                detail="Only administrators can update user roles"
            )
        
        target_user = db.query(User).filter_by(id=target_user_id).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # ✅ VALIDATION: DEPARTMENT_MANAGER needs department
        if new_role == UserRole.DEPARTMENT_MANAGER and not new_department:
            raise HTTPException(
                status_code=400,
                detail="Department is required for department managers"
            )
        
        try:
            old_role = target_user.role
            target_user.role = new_role
            if new_department:
                target_user.department = new_department
            
            db.commit()
            db.refresh(target_user)
            
            # ✅ AUDIT LOG
            audit_logger.log_action(
                user_id=admin_user.id,
                action="UPDATE_ROLE",
                resource_type="USER",
                resource_id=target_user_id,
                details=f"Changed role from {old_role} to {new_role}"
            )
            
            return target_user
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Failed to update user role")

# Initialize service instance
user_service = UserService()