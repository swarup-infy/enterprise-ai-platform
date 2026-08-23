"""
Database configuration and session management.

Provides the SQLAlchemy declarative base, engine, session factory,
FastAPI dependency, and lightweight database health helpers.
"""

from __future__ import annotations

from collections.abc import Generator, Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""


def _create_engine() -> Engine:
    """Create the application database engine with safe pool settings."""
    engine_kwargs: dict[str, object] = {
        "echo": settings.SQL_ECHO if not settings.is_production else False,
        "pool_pre_ping": True,
        "pool_recycle": 1800,
        "pool_timeout": 30,
    }

    engine_kwargs.update(
        {
            "pool_size": 10,
            "max_overflow": 20,
        }
    )

    return create_engine(
        settings.DATABASE_URL,
        **engine_kwargs,
    )


engine = _create_engine()


SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """Yield a request-scoped SQLAlchemy session."""
    db = SessionLocal()

    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def session_scope() -> Iterator[Session]:
    """Provide a transaction-scoped session for service operations."""
    db = SessionLocal()

    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def check_database_connection() -> bool:
    """Return True when the database can execute a simple query."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def create_tables() -> None:
    """
    Create all registered tables.

    Intended for local development and tests.
    Production schema changes should use Alembic migrations.
    """
    Base.metadata.create_all(bind=engine)


def drop_tables() -> None:
    """
    Drop all registered tables.

    Use only in tests or controlled local development.
    """
    Base.metadata.drop_all(bind=engine)


def dispose_engine() -> None:
    """Dispose all pooled database connections."""
    engine.dispose()


__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
    "session_scope",
    "check_database_connection",
    "create_tables",
    "drop_tables",
    "dispose_engine",
]