# app/middleware/permissions.py
from fastapi import Depends, HTTPException, status
from typing import Callable
from sqlalchemy.orm import Session

from app.deps import get_current_user
from app.models.users import User
from app.models.complaints import Complaint
from app.enums import Permission, has_permission, UserRole
from app.database import get_db

def require_permission(permission: Permission) -> Callable:
    """
    Dependency factory that checks if current user has required permission.
    
    Usage:
        @router.delete("/complaints/{id}")
        def delete_complaint(
            user: User = Depends(require_permission(Permission.DELETE_COMPLAINT))
        ):
            # Only ADMIN reaches here
            ...
    
    Args:
        permission: The required permission
        
    Returns:
        Dependency function that validates permission
        
    Raises:
        403: If user lacks permission
    """
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if not has_permission(current_user.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission.value} required"
            )
        return current_user
    
    return permission_checker

# app/middleware/permissions.py (continued)

def require_complaint_access(
    complaint_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Complaint:
    """
    Verify user can access this specific complaint.
    
    Rules:
    - ADMIN: Can access any complaint
    - USER: Can only access their own complaints
    - DEPARTMENT_MANAGER: Can access complaints in their department
    
    Usage:
        @router.get("/complaints/{complaint_id}")
        def get_complaint(
            complaint: Complaint = Depends(require_complaint_access)
        ):
            # complaint is already validated for access
            return complaint
    
    Args:
        complaint_id: The complaint to check
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Complaint object if access is allowed
        
    Raises:
        404: If complaint doesn't exist
        403: If user cannot access this complaint
    """
    # Fetch complaint
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint {complaint_id} not found"
        )
    
    # ADMIN can access anything
    if current_user.role == UserRole.ADMIN:
        return complaint
    
    # USER can only access their own
    if current_user.role == UserRole.USER:
        if complaint.submitted_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own complaints"
            )
        return complaint
    
    # DEPARTMENT_MANAGER can access their department's complaints
    if current_user.role == UserRole.DEPARTMENT_MANAGER:
        if complaint.department != current_user.department:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access complaints in your department"
            )
        return complaint
    
    # Fallback (shouldn't reach here)
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied"
    )