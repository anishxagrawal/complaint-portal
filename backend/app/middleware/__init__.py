# app/middleware/__init__.py
"""
Middleware package for request/response processing.

Contains:
- permissions.py: RBAC enforcement
- error_handler.py: Global error handling
"""

from app.middleware.permissions import require_permission, require_complaint_access
from app.middleware.error_handler import setup_exception_handlers

__all__ = [
    "require_permission",
    "require_complaint_access",
    "setup_exception_handlers"
]