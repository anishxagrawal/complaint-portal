# app/core/exceptions.py
"""
Custom exception classes for the Complaint Portal.

These provide better error handling and clearer error messages
than generic HTTPException.
"""

from fastapi import status
from typing import Optional


class ComplaintPortalException(Exception):
    """
    Base exception for all custom business logic errors.
    
    All custom exceptions should inherit from this.
    """
    def __init__(
        self,
        detail: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_ERROR"
    ):
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(detail)


# ==========================================
# 400-series (Client Errors)
# ==========================================

class NotFoundError(ComplaintPortalException):
    """
    Resource not found (404).
    
    Usage:
        raise NotFoundError("Complaint #123 not found")
    """
    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND"
        )


class UnauthorizedError(ComplaintPortalException):
    """
    Authentication required or token invalid (401).
    
    Usage:
        raise UnauthorizedError("Invalid or expired token")
    """
    def __init__(self, detail: str = "Authentication required"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED"
        )


class ForbiddenError(ComplaintPortalException):
    """
    User lacks permission to access resource (403).
    
    Usage:
        raise ForbiddenError("You can only access your own complaints")
    """
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN"
        )


class ValidationError(ComplaintPortalException):
    """
    Data validation failed (422).
    
    Usage:
        raise ValidationError("Phone number must be 10 digits")
    """
    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR"
        )


class ConflictError(ComplaintPortalException):
    """
    Resource conflict, duplicate entry (409).
    
    Usage:
        raise ConflictError("User with this phone number already exists")
    """
    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT"
        )


class RateLimitError(ComplaintPortalException):
    """
    Too many requests, rate limit exceeded (429).
    
    Usage:
        raise RateLimitError("Too many OTP requests", retry_after=60)
    """
    def __init__(self, detail: str = "Rate limit exceeded", retry_after: int = 60):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED"
        )
        self.retry_after = retry_after


# ==========================================
# 500-series (Server Errors)
# ==========================================

class DatabaseError(ComplaintPortalException):
    """
    Database operation failed (500).
    
    Usage:
        raise DatabaseError("Failed to save complaint to database")
    """
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR"
        )


class ExternalServiceError(ComplaintPortalException):
    """
    External service (SMS, AI) failed (503).
    
    Usage:
        raise ExternalServiceError("SMS service unavailable")
    """
    def __init__(self, detail: str = "External service unavailable"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="EXTERNAL_SERVICE_ERROR"
        )


# ==========================================
# Business Logic Exceptions
# ==========================================

class OTPError(ComplaintPortalException):
    """OTP-related errors"""
    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="OTP_ERROR"
        )


class ComplaintStatusError(ComplaintPortalException):
    """Invalid complaint status transition"""
    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_STATUS_TRANSITION"
        )


class AssignmentError(ComplaintPortalException):
    """Complaint assignment errors"""
    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="ASSIGNMENT_ERROR"
        )