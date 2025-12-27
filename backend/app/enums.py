from enum import Enum
from typing import List

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
    ],
}

def get_role_permissions(role: UserRole) -> List[Permission]:
    return ROLE_PERMISSIONS.get(role, [])

def has_permission(role: UserRole, permission: Permission) -> bool:
    return permission in get_role_permissions(role)
