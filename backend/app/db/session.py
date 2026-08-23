"""
Database session compatibility layer.

The canonical SQLAlchemy session implementation lives in
``app.db.database``. This module re-exports the public session
helpers so existing imports remain stable.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.database import (
    SessionLocal,
    close_session,
    get_db,
    get_session,
    session_scope,
)

__all__ = [
    "Session",
    "SessionLocal",
    "get_db",
    "session_scope",
    "get_session",
    "close_session",
]