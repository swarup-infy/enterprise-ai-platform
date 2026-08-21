"""
Document schemas.

Pydantic schemas for document upload, retrieval,
updates, and API responses.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ==============================================================================
# Base
# ==============================================================================

class DocumentBase(BaseModel):
    """Shared document fields."""

    title: str | None = Field(
        default=None,
        max_length=255,
    )

    summary: str | None = None


# ==============================================================================
# Upload
# ==============================================================================

class DocumentUploadResponse(BaseModel):
    """Returned after a successful upload."""

    id: UUID
    filename: str
    message: str


# ==============================================================================
# Update
# ==============================================================================

class DocumentUpdate(DocumentBase):
    """Update document metadata."""


# ==============================================================================
# Response
# ==============================================================================

class DocumentResponse(DocumentBase):
    """Document response model."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID

    owner_id: UUID

    filename: str

    original_filename: str

    file_path: str

    mime_type: str

    file_size: int

    checksum: str

    embedding_model: str | None

    vector_collection: str | None

    is_processed: bool

    created_at: datetime

    updated_at: datetime


# ==============================================================================
# Search
# ==============================================================================

class DocumentSearchResult(BaseModel):
    """Semantic search result."""

    document_id: UUID

    filename: str

    score: float

    snippet: str


# ==============================================================================
# Delete
# ==============================================================================

class DocumentDeleteResponse(BaseModel):
    """Delete response."""

    message: str


# ==============================================================================
# Exports
# ==============================================================================

__all__ = [
    "DocumentBase",
    "DocumentUploadResponse",
    "DocumentUpdate",
    "DocumentResponse",
    "DocumentSearchResult",
    "DocumentDeleteResponse",
]
