"""
Database session management.

Provides SQLAlchemy sessions for FastAPI dependencies,
services, background workers, and scripts.
"""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy.orm import Session

from app.db.database import SessionLocal


# ==============================================================================
# FastAPI Database Dependency
# ==============================================================================


def get_db() -> Generator[Session, None, None]:
    """
    Provide a database session for FastAPI requests.

    The session is automatically closed after the request.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ==============================================================================
# Context Manager
# ==============================================================================


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """
    Provide a transactional database session.

    Example:
        with session_scope() as db:
            db.add(user)
    """

    session = SessionLocal()

    try:
        yield session
        session.commit()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


# ==============================================================================
# Session Factory
# ==============================================================================


def get_session() -> Session:
    """
    Return a new SQLAlchemy session.

    Intended for CLI tools, workers, scheduled jobs, and scripts.
    """

    return SessionLocal()


# ==============================================================================
# Session Cleanup
# ==============================================================================


def close_session(session: Session) -> None:
    """
    Safely close a SQLAlchemy session.
    """

    session.close()


__all__ = [
    "get_db",
    "session_scope",
    "get_session",
    "close_session",
]