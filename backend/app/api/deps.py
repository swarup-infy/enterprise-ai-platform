"""
Shared FastAPI dependencies.

Reusable dependencies used across API routes.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.database import get_db


# ==============================================================================
# Database Dependency
# ==============================================================================

DBSession = Annotated[Session, Depends(get_db)]


# ==============================================================================
# HTTP Bearer Authentication
# ==============================================================================

bearer_scheme = HTTPBearer(
    auto_error=True,
)


# ==============================================================================
# Current User
# ==============================================================================

async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(bearer_scheme),
    ],
) -> dict:
    """
    Decode and validate the JWT access token.

    Expects:

        Authorization: Bearer <access_token>
    """

    try:
        payload = decode_access_token(credentials.credentials)

    except (JWTError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return payload


CurrentUser = Annotated[
    dict,
    Depends(get_current_user),
]


# ==============================================================================
# Admin Dependency
# ==============================================================================

async def require_admin(
    current_user: CurrentUser,
) -> dict:
    """
    Ensure the authenticated user has administrator privileges.
    """

    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required.",
        )

    return current_user


AdminUser = Annotated[
    dict,
    Depends(require_admin),
]


# ==============================================================================
# Exports
# ==============================================================================

__all__ = [
    "DBSession",
    "CurrentUser",
    "AdminUser",
    "get_current_user",
    "require_admin",
]