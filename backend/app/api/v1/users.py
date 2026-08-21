"""
User API.

CRUD endpoints for user management with role-based
authorization and user self-service access control.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.deps import AdminUser, CurrentUser, DBSession
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import UserService


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# ==============================================================================
# List Users
# ==============================================================================


@router.get(
    "/",
    response_model=list[UserResponse],
)
async def list_users(
    db: DBSession,
    _: AdminUser,
    skip: int = 0,
    limit: int = 20,
) -> list[UserResponse]:
    """
    List users.

    Administrator access is required.
    """

    if skip < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="skip must be greater than or equal to 0.",
        )

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="limit must be between 1 and 100.",
        )

    service = UserService(db)

    return service.list_users(
        skip=skip,
        limit=limit,
    )


# ==============================================================================
# Get User
# ==============================================================================


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
async def get_user(
    user_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> UserResponse:
    """
    Get a user profile.

    Administrators may retrieve any user.

    Regular users may retrieve only their own profile.
    """

    authenticated_user_id = current_user.get("sub")

    if not authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
        )

    try:
        authenticated_user_uuid = UUID(
            str(authenticated_user_id)
        )
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
        ) from exc

    is_admin = current_user.get("role") == "admin"

    if not is_admin and user_id != authenticated_user_uuid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own profile.",
        )

    service = UserService(db)

    user = service.get_user(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return user


# ==============================================================================
# Update User
# ==============================================================================


@router.put(
    "/{user_id}",
    response_model=UserResponse,
)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    db: DBSession,
    current_user: CurrentUser,
) -> UserResponse:
    """
    Update a user profile.

    Administrators may update any user.

    Regular users may update only their own profile.
    """

    authenticated_user_id = current_user.get("sub")

    if not authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
        )

    try:
        authenticated_user_uuid = UUID(
            str(authenticated_user_id)
        )
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
        ) from exc

    is_admin = current_user.get("role") == "admin"

    if not is_admin and user_id != authenticated_user_uuid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile.",
        )

    service = UserService(db)

    user = service.get_user(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return service.update_user(
        user,
        data,
    )


# ==============================================================================
# Delete User
# ==============================================================================


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: UUID,
    db: DBSession,
    _: AdminUser,
) -> None:
    """
    Delete a user.

    Administrator access is required.
    """

    service = UserService(db)

    user = service.get_user(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    service.delete_user(user)

    return None


__all__ = [
    "router",
]