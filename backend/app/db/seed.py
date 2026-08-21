"""
Database Seed.

Creates initial application data for local development.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User


def seed_admin_user(
    db: Session,
    *,
    email: str,
    username: str,
    password: str,
    full_name: str = "System Administrator",
) -> User:
    """
    Create the initial admin user if it does not exist.
    """

    existing = db.scalar(
        select(User).where(
            (User.email == email)
            | (User.username == username)
        )
    )

    if existing:
        return existing

    admin = User(
        email=email,
        username=username,
        full_name=full_name,
        password_hash=hash_password(password),
        role="admin",
        is_active=True,
        is_verified=True,
        is_superuser=True,
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    return admin


def seed_database(
    db: Session,
    *,
    admin_email: str,
    admin_username: str,
    admin_password: str,
) -> User:
    """
    Seed the database with required initial data.
    """

    return seed_admin_user(
        db,
        email=admin_email,
        username=admin_username,
        password=admin_password,
    )