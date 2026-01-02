# app/deps.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError

from app.database import get_db
from app.core.security import verify_token
from app.models.users import User

# ============================================
# Swagger-native OAuth2 Bearer
# ============================================

# ✅ FIX 1: tokenUrl must point to login, not OTP
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/")

# ============================================
# AUTHENTICATION DEPENDENCY
# ============================================
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Extract and verify current user from JWT token.
    """
    try:
        payload = verify_token(token)
        sub: str = payload.get("sub")

        if sub is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        user_id: int = int(sub)

    # ✅ FIX 2: catch broader token-related failures safely
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


# ============================================
# AUTHORIZATION DEPENDENCIES
# ============================================
def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def get_current_manager(
    current_user: User = Depends(get_current_user)
) -> User:
    if not (current_user.is_admin() or current_user.is_department_manager()):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager or admin access required"
        )
    return current_user