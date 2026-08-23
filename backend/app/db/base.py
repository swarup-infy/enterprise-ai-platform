"""
Database model registry.

Imports every SQLAlchemy model so SQLAlchemy metadata and Alembic
can discover all application tables.
"""

from __future__ import annotations

from app.db.database import Base

from app.models.chat_history import ChatConversation, ChatMessage
from app.models.document import Document
from app.models.user import User


target_metadata = Base.metadata


__all__ = [
    "Base",
    "User",
    "Document",
    "ChatConversation",
    "ChatMessage",
    "target_metadata",
]