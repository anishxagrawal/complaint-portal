# app/middleware/error_handler.py
"""
Global error handling middleware.

Catches all exceptions and returns proper HTTP responses.
Logs errors for debugging.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from jose import JWTError
import logging

from app.core.exceptions import (
    ComplaintPortalException,
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
    ValidationError as CustomValidationError,
    DatabaseError,
    RateLimitError
)

# Get logger
logger = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Register all exception handlers with the FastAPI app.
    
    Call this in main.py:
        from app.middleware.error_handler import setup_exception_handlers
        setup_exception_handlers(app)
    """
    
    # ==========================================
    # Custom Business Logic Exceptions
    # ==========================================
    
    @app.exception_handler(ComplaintPortalException)
    async def complaint_portal_exception_handler(
        request: Request,
        exc: ComplaintPortalException
    ):
        """Handle all custom business exceptions"""
        logger.warning(
            f"Business error: {exc.detail} | "
            f"Path: {request.url.path} | "
            f"Status: {exc.status_code}"
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "error_code": exc.error_code,
                "path": str(request.url.path)
            }
        )
    
    # ==========================================
    # Not Found (404)
    # ==========================================
    
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        """Handle 404 errors"""
        logger.info(f"Not found: {exc.detail} | Path: {request.url.path}")
        
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "detail": exc.detail,
                "error_code": "NOT_FOUND",
                "path": str(request.url.path)
            }
        )
    
    # ==========================================
    # Unauthorized (401)
    # ==========================================
    
    @app.exception_handler(UnauthorizedError)
    async def unauthorized_handler(request: Request, exc: UnauthorizedError):
        """Handle authentication errors"""
        logger.warning(f"Unauthorized: {exc.detail} | Path: {request.url.path}")
        
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "detail": exc.detail,
                "error_code": "UNAUTHORIZED",
                "path": str(request.url.path)
            },
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # ==========================================
    # Forbidden (403)
    # ==========================================
    
    @app.exception_handler(ForbiddenError)
    async def forbidden_handler(request: Request, exc: ForbiddenError):
        """Handle permission errors"""
        logger.warning(f"Forbidden: {exc.detail} | Path: {request.url.path}")
        
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "detail": exc.detail,
                "error_code": "FORBIDDEN",
                "path": str(request.url.path)
            }
        )
    
    # ==========================================
    # Validation Errors (422)
    # ==========================================
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
    ):
        """Handle Pydantic validation errors"""
        logger.warning(
            f"Validation error: {exc.errors()} | "
            f"Path: {request.url.path}"
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Validation error",
                "error_code": "VALIDATION_ERROR",
                "errors": exc.errors(),
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(CustomValidationError)
    async def custom_validation_handler(
        request: Request,
        exc: CustomValidationError
    ):
        """Handle custom validation errors"""
        logger.warning(f"Custom validation: {exc.detail} | Path: {request.url.path}")
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": exc.detail,
                "error_code": "VALIDATION_ERROR",
                "path": str(request.url.path)
            }
        )
    
    # ==========================================
    # Rate Limit (429)
    # ==========================================
    
    @app.exception_handler(RateLimitError)
    async def rate_limit_handler(request: Request, exc: RateLimitError):
        """Handle rate limit errors"""
        logger.warning(
            f"Rate limit exceeded: {exc.detail} | "
            f"Path: {request.url.path}"
        )
        
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": exc.detail,
                "error_code": "RATE_LIMIT_EXCEEDED",
                "retry_after": exc.retry_after,
                "path": str(request.url.path)
            },
            headers={"Retry-After": str(exc.retry_after)}
        )
    
    # ==========================================
    # Database Errors (500)
    # ==========================================
    
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(
        request: Request,
        exc: SQLAlchemyError
    ):
        """Handle database errors"""
        logger.error(
            f"Database error: {str(exc)} | "
            f"Path: {request.url.path}",
            exc_info=True
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Database error occurred",
                "error_code": "DATABASE_ERROR",
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(DatabaseError)
    async def database_error_handler(request: Request, exc: DatabaseError):
        """Handle custom database errors"""
        logger.error(
            f"Custom DB error: {exc.detail} | "
            f"Path: {request.url.path}",
            exc_info=True
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": exc.detail,
                "error_code": "DATABASE_ERROR",
                "path": str(request.url.path)
            }
        )
    
    # ==========================================
    # JWT Errors (401)
    # ==========================================
    
    @app.exception_handler(JWTError)
    async def jwt_exception_handler(request: Request, exc: JWTError):
        """Handle JWT token errors"""
        logger.warning(
            f"JWT error: {str(exc)} | "
            f"Path: {request.url.path}"
        )
        
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "detail": "Invalid or expired token",
                "error_code": "INVALID_TOKEN",
                "path": str(request.url.path)
            },
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # ==========================================
    # Catch-All for Unexpected Errors (500)
    # ==========================================
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other unexpected exceptions"""
        logger.error(
            f"Unexpected error: {str(exc)} | "
            f"Type: {type(exc).__name__} | "
            f"Path: {request.url.path}",
            exc_info=True
        )
        
        # In production, don't expose internal error details
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "An unexpected error occurred",
                "error_code": "INTERNAL_SERVER_ERROR",
                "path": str(request.url.path)
            }
        )
    
    logger.info("✅ Exception handlers registered successfully")