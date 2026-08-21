"""
Authentication API.

Handles user registration, login, and profile retrieval.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentUser, DBSession
from app.core.security import create_access_token
from app.schemas.user import (
    LoginRequest,
    Token,
    UserCreate,
    UserResponse,
)
from app.services.user_service import UserService


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ==============================================================================
# Register
# ==============================================================================


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: UserCreate,
    db: DBSession,
) -> UserResponse:
    """
    Register a new user.

    Email and username are checked before creation for a better user
    experience. Database-level unique constraints remain the final
    protection against concurrent duplicate registrations.
    """

    service = UserService(db)

    # --------------------------------------------------------------------------
    # Friendly duplicate checks
    # --------------------------------------------------------------------------

    if service.get_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists.",
        )

    if service.get_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists.",
        )

    # --------------------------------------------------------------------------
    # Create user
    # --------------------------------------------------------------------------

    try:
        user = service.create_user(user_data)

    except IntegrityError as exc:
        db.rollback()

        # The pre-checks above are not sufficient under concurrent requests.
        # The database unique constraints are the authoritative protection.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username already exists.",
        ) from exc

    return user


# ==============================================================================
# Login
# ==============================================================================


@router.post(
    "/login",
    response_model=Token,
)
async def login(
    credentials: LoginRequest,
    db: DBSession,
) -> Token:
    """
    Authenticate a user and issue a JWT access token.
    """

    service = UserService(db)

    user = service.authenticate(
        credentials.email,
        credentials.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    token = create_access_token(
        subject=str(user.id),
        extra_claims={
            "role": user.role,
            "email": user.email,
        },
    )

    return Token(
        access_token=token,
        token_type="bearer",
    )


# ==============================================================================
# Current User
# ==============================================================================


@router.get(
    "/me",
    response_model=dict,
)
async def me(
    current_user: CurrentUser,
) -> dict:
    """
    Return the authenticated user's JWT claims.
    """

    return current_user


# ==============================================================================
# Logout
# ==============================================================================


@router.post(
    "/logout",
)
async def logout() -> dict[str, str]:
    """
    Logout endpoint for the stateless JWT authentication model.

    The backend does not currently maintain a token blacklist or
    server-side session store, so the access token cannot be revoked
    immediately on the server.

    The client must remove its stored access token.
    """

    return {
        "message": (
            "Logout acknowledged. "
            "Remove the access token on the client."
        ),
    }


__all__ = [
    "router",
]