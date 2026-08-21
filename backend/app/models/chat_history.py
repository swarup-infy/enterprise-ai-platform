"""
Chat history models.

Stores chat conversations and individual messages for authenticated users.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class ChatConversation(Base):
    """
    Represents one chat conversation owned by a user.
    """

    __tablename__ = "chat_conversations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="New Chat",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    owner = relationship(
        "User",
        backref="chat_conversations",
    )

    messages = relationship(
        "ChatMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )

    def __repr__(self) -> str:
        return (
            f"ChatConversation("
            f"id={self.id}, "
            f"owner_id={self.owner_id}, "
            f"title='{self.title}'"
            f")"
        )


class ChatMessage(Base):
    """
    Represents one message inside a chat conversation.
    """

    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "chat_conversations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    conversation = relationship(
        "ChatConversation",
        back_populates="messages",
    )

    def __repr__(self) -> str:
        return (
            f"ChatMessage("
            f"id={self.id}, "
            f"conversation_id={self.conversation_id}, "
            f"role='{self.role}'"
            f")"
        )


__all__ = [
    "ChatConversation",
    "ChatMessage",
]