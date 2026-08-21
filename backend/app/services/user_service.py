"""
User service.

Business logic for user management, authentication,
and user persistence.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """Service for user-related operations."""

    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    # ==========================================================================
    # Create
    # ==========================================================================

    def create_user(
        self,
        data: UserCreate,
    ) -> User:
        """
        Create a new user.

        Passwords are hashed before persistence.
        """

        user = User(
            full_name=data.full_name,
            username=data.username.strip(),
            email=data.email.strip().lower(),
            password_hash=hash_password(
                data.password
            ),
        )

        self.db.add(user)

        try:
            self.db.commit()
            self.db.refresh(user)

        except IntegrityError:
            self.db.rollback()
            raise

        except Exception:
            self.db.rollback()
            raise

        return user

    # ==========================================================================
    # Read
    # ==========================================================================

    def get_user(
        self,
        user_id: UUID,
    ) -> User | None:
        """
        Get a user by ID.
        """

        return self.db.get(
            User,
            user_id,
        )

    def get_by_email(
        self,
        email: str,
    ) -> User | None:
        """
        Get a user by normalized email address.
        """

        if not isinstance(email, str):
            raise TypeError(
                "email must be a string."
            )

        normalized_email = email.strip().lower()

        if not normalized_email:
            return None

        stmt = (
            select(User)
            .where(
                User.email == normalized_email,
            )
        )

        return self.db.scalar(stmt)

    def get_by_username(
        self,
        username: str,
    ) -> User | None:
        """
        Get a user by normalized username.
        """

        if not isinstance(username, str):
            raise TypeError(
                "username must be a string."
            )

        normalized_username = username.strip()

        if not normalized_username:
            return None

        stmt = (
            select(User)
            .where(
                User.username == normalized_username,
            )
        )

        return self.db.scalar(stmt)

    def list_users(
        self,
        skip: int = 0,
        limit: int = DEFAULT_PAGE_SIZE,
    ) -> list[User]:
        """
        Return paginated users.
        """

        if skip < 0:
            raise ValueError(
                "skip must be greater than or equal to 0."
            )

        if (
            limit < 1
            or limit > self.MAX_PAGE_SIZE
        ):
            raise ValueError(
                f"limit must be between 1 and "
                f"{self.MAX_PAGE_SIZE}."
            )

        stmt = (
            select(User)
            .order_by(
                User.created_at.desc(),
            )
            .offset(skip)
            .limit(limit)
        )

        return list(
            self.db.scalars(stmt).all()
        )

    # ==========================================================================
    # Update
    # ==========================================================================

    def update_user(
        self,
        user: User,
        data: UserUpdate,
    ) -> User:
        """
        Update an existing user.

        Password updates are automatically hashed.
        """

        updates = data.model_dump(
            exclude_unset=True,
        )

        if not updates:
            return user

        # ----------------------------------------------------------------------
        # Password
        # ----------------------------------------------------------------------

        if "password" in updates:
            password = updates.pop(
                "password"
            )

            if password:
                updates["password_hash"] = (
                    hash_password(password)
                )

        # ----------------------------------------------------------------------
        # Normalize user-controlled fields.
        # ----------------------------------------------------------------------

        if "email" in updates:
            email = updates["email"]

            if isinstance(email, str):
                normalized_email = (
                    email.strip().lower()
                )

                if not normalized_email:
                    raise ValueError(
                        "email cannot be empty."
                    )

                updates["email"] = normalized_email

        if "username" in updates:
            username = updates["username"]

            if isinstance(username, str):
                normalized_username = (
                    username.strip()
                )

                if not normalized_username:
                    raise ValueError(
                        "username cannot be empty."
                    )

                updates["username"] = (
                    normalized_username
                )

        # ----------------------------------------------------------------------
        # Apply updates.
        # ----------------------------------------------------------------------

        for field, value in updates.items():
            setattr(
                user,
                field,
                value,
            )

        try:
            self.db.commit()
            self.db.refresh(user)

        except IntegrityError:
            self.db.rollback()
            raise

        except Exception:
            self.db.rollback()
            raise

        return user

    # ==========================================================================
    # Delete
    # ==========================================================================

    def delete_user(
        self,
        user: User,
    ) -> None:
        """
        Delete a user.

        Database-level relationships/foreign keys determine how
        associated records are handled.
        """

        self.db.delete(user)

        try:
            self.db.commit()

        except Exception:
            self.db.rollback()
            raise

    # ==========================================================================
    # Authentication
    # ==========================================================================

    def authenticate(
        self,
        email: str,
        password: str,
    ) -> User | None:
        """
        Authenticate a user using email and password.

        Returns:
            User when credentials are valid.
            None when credentials are invalid.
        """

        if not isinstance(email, str):
            return None

        if not isinstance(password, str):
            return None

        normalized_email = email.strip().lower()

        if not normalized_email or not password:
            return None

        user = self.get_by_email(
            normalized_email
        )

        if user is None:
            return None

        if not verify_password(
            password,
            user.password_hash,
        ):
            return None

        return user


__all__ = [
    "UserService",
]