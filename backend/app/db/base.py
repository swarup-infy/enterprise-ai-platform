"""
Database model registry.

Imports every SQLAlchemy model so SQLAlchemy metadata
and Alembic can discover all database tables.
"""

from __future__ import annotations

from app.db.database import Base

# Import all models so they are registered in Base.metadata.
from app.models.document import Document
from app.models.user import User

target_metadata = Base.metadata

__all__ = [
    "Base",
    "User",
    "Document",
    "target_metadata",
]