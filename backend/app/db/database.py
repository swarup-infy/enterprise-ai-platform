"""
Database configuration.

Creates the SQLAlchemy engine, session factory,
and database dependency.
"""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


# ==============================================================================
# SQLAlchemy Base
# ==============================================================================


class Base(DeclarativeBase):
    """Base class for all ORM models."""


# ==============================================================================
# Engine
# ==============================================================================

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=3600,
    future=True,
)


# ==============================================================================
# Session Factory
# ==============================================================================

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=Session,
)


# ==============================================================================
# Dependency
# ==============================================================================

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI database dependency.

    Usage:
        db: Session = Depends(get_db)
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ==============================================================================
# Helpers
# ==============================================================================

def create_tables() -> None:
    """Create all registered tables."""
    Base.metadata.create_all(bind=engine)


def drop_tables() -> None:
    """Drop all registered tables."""
    Base.metadata.drop_all(bind=engine)


# ==============================================================================
# Exports
# ==============================================================================

__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
    "create_tables",
    "drop_tables",
]