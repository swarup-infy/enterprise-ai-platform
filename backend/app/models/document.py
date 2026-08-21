"""
Document model.

Represents uploaded documents in the Enterprise AI Platform.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Document(Base):
    """
    Uploaded document.
    """

    __tablename__ = "documents"

    # ==========================================================================
    # Primary Key
    # ==========================================================================

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ==========================================================================
    # Owner
    # ==========================================================================

    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    owner = relationship(
        "User",
        backref="documents",
    )

    # ==========================================================================
    # Metadata
    # ==========================================================================

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    file_path: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
    )

    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    file_size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    # IMPORTANT:
    # Checksum is NOT globally unique.
    #
    # Database-level uniqueness is enforced by:
    #     (owner_id, checksum)
    #
    # This allows different tenants/users to upload identical files
    # while preventing duplicate files within the same tenant.
    checksum: Mapped[str] = mapped_column(
        String(64),
        index=True,
        nullable=False,
    )

    # ==========================================================================
    # AI Processing
    # ==========================================================================

    title: Mapped[str | None] = mapped_column(
        String(255),
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
    )

    embedding_model: Mapped[str | None] = mapped_column(
        String(100),
    )

    vector_collection: Mapped[str | None] = mapped_column(
        String(100),
    )

    is_processed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # ==========================================================================
    # Audit
    # ==========================================================================

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

    # ==========================================================================
    # Representation
    # ==========================================================================

    def __repr__(self) -> str:
        return (
            f"Document("
            f"id={self.id}, "
            f"filename='{self.filename}', "
            f"processed={self.is_processed}"
            f")"
        )


__all__ = ["Document"]