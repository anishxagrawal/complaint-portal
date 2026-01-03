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
        OPEN → ASSIGNED → IN_PROGRESS → RESOLVED
          ↓
        REJECTED
    """
    OPEN = "open"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REJECTED = "rejected"


# Valid status transitions (current → [allowed next states])
STATUS_TRANSITIONS = {
    ComplaintStatus.OPEN: [
        ComplaintStatus.ASSIGNED,
        ComplaintStatus.REJECTED,
    ],
    ComplaintStatus.ASSIGNED: [
        ComplaintStatus.IN_PROGRESS,
        ComplaintStatus.REJECTED,
    ],
    ComplaintStatus.IN_PROGRESS: [
        ComplaintStatus.RESOLVED,
        ComplaintStatus.ASSIGNED,
    ],
    ComplaintStatus.RESOLVED: [],
    ComplaintStatus.REJECTED: [],
}


def is_valid_transition(current_status: str, new_status: str) -> bool:
    """
    Check if a status transition is valid.
    
    Args:
        current_status: Current complaint status (string)
        new_status: Desired new status (string)
        
    Returns:
        True if transition is allowed, False otherwise
        
    Example:
        is_valid_transition("open", "assigned")  # True
        is_valid_transition("open", "resolved")  # False
    """
    try:
        current = ComplaintStatus(current_status.lower())
        new = ComplaintStatus(new_status.lower())
    except ValueError:
        return False
    
    if current not in STATUS_TRANSITIONS:
        return False
    
    return new in STATUS_TRANSITIONS[current]


def get_valid_transitions(current_status: str) -> List[str]:
    """
    Get list of valid status transitions from current state.
    
    Args:
        current_status: Current complaint status
        
    Returns:
        List of allowed status strings
        
    Example:
        get_valid_transitions("open")
        # Returns: ["assigned", "rejected"]
    """
    try:
        current = ComplaintStatus(current_status.lower())
    except ValueError:
        return []
    
    if current not in STATUS_TRANSITIONS:
        return []
    
    return [status.value for status in STATUS_TRANSITIONS[current]]