# app/middleware/permissions.py
from fastapi import Depends, HTTPException, status
from typing import Callable
from sqlalchemy.orm import Session

from app.deps import get_current_user
from app.models.users import User
from app.models.complaints import Complaint
from app.enums import Permission, has_permission, UserRole
from app.database import get_db
from app.core.logging import get_logger

logger = get_logger(__name__)

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
            logger.warning(
                f"authz.permission.denied | user_id={current_user.id} | role={current_user.role.value} | permission={permission.value}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission.value} required"
            )
        return current_user
    
    return permission_checker

def require_any_permission(*permissions: Permission) -> Callable:
    """
    Dependency factory that checks if current user has ANY of the required permissions.
    
    Usage:
        @router.get("/complaints/")
        def list_complaints(
            user: User = Depends(require_any_permission(
                Permission.VIEW_ALL_COMPLAINTS,
                Permission.VIEW_OWN_COMPLAINTS,
                Permission.VIEW_DEPARTMENT_COMPLAINTS
            ))
        ):
            # User has at least one of the permissions
            ...
    
    Args:
        *permissions: One or more required permissions
        
    Returns:
        Dependency function that validates permissions
        
    Raises:
        403: If user lacks all permissions
    """
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        for permission in permissions:
            if has_permission(current_user.role, permission):
                return current_user
        
        permission_names = ", ".join(p.value for p in permissions)
        logger.warning(
            f"authz.permission.denied | user_id={current_user.id} | role={current_user.role.value} | permissions=[{permission_names}]"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied: requires one of [{permission_names}]"
        )
    
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
    
    # Check if user can view all complaints
    if has_permission(current_user.role, Permission.VIEW_ALL_COMPLAINTS):
        return complaint
    
    # Check if user can view own complaints
    if has_permission(current_user.role, Permission.VIEW_OWN_COMPLAINTS):
        if complaint.submitted_by != current_user.id:
            logger.warning(
                f"authz.complaint.access.denied | user_id={current_user.id} | role={current_user.role.value} | complaint_id={complaint_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own complaints"
            )
        return complaint
    
    # Check if user can view department complaints
    if has_permission(current_user.role, Permission.VIEW_DEPARTMENT_COMPLAINTS):
        if complaint.department != current_user.department:
            logger.warning(
                f"authz.complaint.access.denied | user_id={current_user.id} | role={current_user.role.value} | complaint_id={complaint_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access complaints in your department"
            )
        return complaint
    
    # No permission matched
    logger.warning(
        f"authz.complaint.access.denied | user_id={current_user.id} | role={current_user.role.value} | complaint_id={complaint_id}"
    )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied"
    )