# backend/app/enums.py

from enum import Enum
from typing import List

# ==========================================
# USER ROLES & PERMISSIONS (Existing)
# ==========================================

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    DEPARTMENT_MANAGER = "department_manager"


class Permission(str, Enum):
    VIEW_ALL_COMPLAINTS = "view_all_complaints"
    VIEW_OWN_COMPLAINTS = "view_own_complaints"
    VIEW_DEPARTMENT_COMPLAINTS = "view_department_complaints"
    CREATE_COMPLAINT = "create_complaint"
    UPDATE_COMPLAINT = "update_complaint"
    DELETE_COMPLAINT = "delete_complaint"
    ASSIGN_COMPLAINT = "assign_complaint"
    MANAGE_USERS = "manage_users"
    VIEW_USERS = "view_users"
    CHANGE_COMPLAINT_STATUS = "change_complaint_status"  # ✅ NEW


ROLE_PERMISSIONS = {
    UserRole.ADMIN: list(Permission),
    UserRole.USER: [
        Permission.VIEW_OWN_COMPLAINTS,
        Permission.CREATE_COMPLAINT,
        Permission.UPDATE_COMPLAINT,
    ],
    UserRole.DEPARTMENT_MANAGER: [
        Permission.VIEW_DEPARTMENT_COMPLAINTS,
        Permission.CREATE_COMPLAINT,
        Permission.UPDATE_COMPLAINT,
        Permission.ASSIGN_COMPLAINT,
        Permission.VIEW_USERS,
        Permission.CHANGE_COMPLAINT_STATUS,  # ✅ NEW
    ],
}


def get_role_permissions(role: UserRole) -> List[Permission]:
    """Get all permissions for a role"""
    return ROLE_PERMISSIONS.get(role, [])


def has_permission(role: UserRole, permission: Permission) -> bool:
    """Check if a role has a specific permission"""
    return permission in get_role_permissions(role)


# ==========================================
# COMPLAINT STATUS WORKFLOW (NEW)
# ==========================================

class ComplaintStatus(str, Enum):
    """
    Valid complaint statuses in the workflow.
    
    Workflow:
        PENDING → ASSIGNED → IN_PROGRESS → RESOLVED → CLOSED
           ↓
        REJECTED
    """
    PENDING = "pending"           # Just submitted, awaiting assignment
    ASSIGNED = "assigned"         # Assigned to department/officer
    IN_PROGRESS = "in_progress"   # Officer is working on it
    RESOLVED = "resolved"         # Issue fixed, awaiting confirmation
    CLOSED = "closed"             # Confirmed resolved or auto-closed
    REJECTED = "rejected"         # Invalid/duplicate complaint


# Valid status transitions (current → new: [allowed_roles])
STATUS_TRANSITIONS = {
    ComplaintStatus.PENDING: {
        ComplaintStatus.ASSIGNED: [UserRole.ADMIN, UserRole.DEPARTMENT_MANAGER],
        ComplaintStatus.REJECTED: [UserRole.ADMIN, UserRole.DEPARTMENT_MANAGER],
    },
    ComplaintStatus.ASSIGNED: {
        ComplaintStatus.IN_PROGRESS: [UserRole.ADMIN, UserRole.DEPARTMENT_MANAGER],
        ComplaintStatus.REJECTED: [UserRole.ADMIN, UserRole.DEPARTMENT_MANAGER],
    },
    ComplaintStatus.IN_PROGRESS: {
        ComplaintStatus.RESOLVED: [UserRole.ADMIN, UserRole.DEPARTMENT_MANAGER],
        ComplaintStatus.ASSIGNED: [UserRole.ADMIN, UserRole.DEPARTMENT_MANAGER],  # Reassign
    },
    ComplaintStatus.RESOLVED: {
        ComplaintStatus.CLOSED: [UserRole.ADMIN, UserRole.DEPARTMENT_MANAGER, UserRole.USER],
        ComplaintStatus.IN_PROGRESS: [UserRole.ADMIN, UserRole.DEPARTMENT_MANAGER],  # Reopen
    },
    ComplaintStatus.CLOSED: {
        # Closed is final state
    },
    ComplaintStatus.REJECTED: {
        # Rejected is final state
    },
}


def can_transition_status(
    current_status: str,
    new_status: str,
    user_role: UserRole
) -> bool:
    """
    Check if a status transition is valid for a user role.
    
    Args:
        current_status: Current complaint status (string)
        new_status: Desired new status (string)
        user_role: Role of user making the change
        
    Returns:
        True if transition is allowed, False otherwise
        
    Example:
        can_transition_status("pending", "assigned", UserRole.ADMIN)  # True
        can_transition_status("pending", "closed", UserRole.USER)     # False
    """
    try:
        current = ComplaintStatus(current_status.lower())
        new = ComplaintStatus(new_status.lower())
    except ValueError:
        return False  # Invalid status string
    
    if current not in STATUS_TRANSITIONS:
        return False
    
    allowed_transitions = STATUS_TRANSITIONS[current]
    
    if new not in allowed_transitions:
        return False
    
    allowed_roles = allowed_transitions[new]
    
    return user_role in allowed_roles


def get_allowed_transitions(current_status: str, user_role: UserRole) -> List[str]:
    """
    Get list of allowed status transitions for current user.
    
    Args:
        current_status: Current complaint status
        user_role: User's role
        
    Returns:
        List of allowed status strings
        
    Example:
        get_allowed_transitions("pending", UserRole.ADMIN)
        # Returns: ["assigned", "rejected"]
    """
    try:
        current = ComplaintStatus(current_status.lower())
    except ValueError:
        return []
    
    if current not in STATUS_TRANSITIONS:
        return []
    
    allowed_transitions = STATUS_TRANSITIONS[current]
    result = []
    
    for new_status, allowed_roles in allowed_transitions.items():
        if user_role in allowed_roles:
            result.append(new_status.value)
    
    return result