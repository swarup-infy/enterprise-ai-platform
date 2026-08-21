"""
Document service.

Business logic for document upload, retrieval,
updates, deletion, and metadata management.
"""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.schemas.document import DocumentUpdate
from app.services.vector_store_service import VectorStoreService


class DocumentService:
    """Service for document operations."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.vector_store = VectorStoreService()

    # ==========================================================================
    # Create
    # ==========================================================================

    def create_document(
        self,
        *,
        owner_id: UUID,
        filename: str,
        original_filename: str,
        file_path: str,
        mime_type: str,
        file_size: int,
        checksum: str,
    ) -> Document:
        """Create a document record."""

        document = Document(
            owner_id=owner_id,
            filename=filename,
            original_filename=original_filename,
            file_path=file_path,
            mime_type=mime_type,
            file_size=file_size,
            checksum=checksum,
        )

        self.db.add(document)

        try:
            self.db.commit()
            self.db.refresh(document)
        except Exception:
            self.db.rollback()
            raise

        return document

    # ==========================================================================
    # Read
    # ==========================================================================

    def get_document(
        self,
        document_id: UUID,
    ) -> Document | None:
        """
        Get a document by ID.

        Intended for trusted internal operations such as background
        document processing.

        User-facing API operations must use
        get_document_for_owner() to enforce ownership isolation.
        """

        return self.db.get(
            Document,
            document_id,
        )

    def get_document_for_owner(
        self,
        *,
        document_id: UUID,
        owner_id: UUID,
    ) -> Document | None:
        """
        Get a document only when it belongs to the specified owner.

        This method must be used by user-facing document operations
        to enforce document ownership isolation.
        """

        stmt = (
            select(Document)
            .where(
                Document.id == document_id,
                Document.owner_id == owner_id,
            )
        )

        return self.db.scalar(stmt)

    def get_by_checksum(
        self,
        *,
        owner_id: UUID,
        checksum: str,
    ) -> Document | None:
        """
        Get a document by checksum for a specific owner.

        Checksum uniqueness is tenant scoped.

        A document belonging to another owner must never be returned.
        """

        stmt = (
            select(Document)
            .where(
                Document.owner_id == owner_id,
                Document.checksum == checksum,
            )
        )

        return self.db.scalar(stmt)

    def list_documents(
        self,
        owner_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Document]:
        """
        List documents belonging only to the specified owner.
        """

        stmt = (
            select(Document)
            .where(
                Document.owner_id == owner_id,
            )
            .order_by(
                Document.created_at.desc(),
            )
            .offset(skip)
            .limit(limit)
        )

        return list(
            self.db.scalars(stmt).all()
        )

    # ==========================================================================
    # Update
    # ==========================================================================

    def update_document(
        self,
        document: Document,
        data: DocumentUpdate,
    ) -> Document:
        """
        Update document metadata.

        Ownership authorization is handled by the API layer before this
        method is called.
        """

        updates = data.model_dump(
            exclude_unset=True,
        )

        for field, value in updates.items():
            setattr(
                document,
                field,
                value,
            )

        try:
            self.db.commit()
            self.db.refresh(document)
        except Exception:
            self.db.rollback()
            raise

        return document

    # ==========================================================================
    # Processing
    # ==========================================================================

    def mark_processed(
        self,
        document: Document,
        embedding_model: str,
        vector_collection: str,
        summary: str | None = None,
    ) -> Document:
        """
        Mark a document as successfully processed.
        """

        document.is_processed = True
        document.embedding_model = embedding_model
        document.vector_collection = vector_collection

        if summary:
            document.summary = summary

        try:
            self.db.commit()
            self.db.refresh(document)
        except Exception:
            self.db.rollback()
            raise

        return document

    # ==========================================================================
    # Delete
    # ==========================================================================

    def delete_document(
        self,
        document: Document,
        delete_file: bool = False,
    ) -> None:
        """
        Delete a document and all associated resources.

        Cleanup order:

        1. Remove associated vectors from ChromaDB.
        2. Remove the physical uploaded file.
        3. Remove the PostgreSQL document record.

        ChromaDB deletion is restricted by both document ID and owner ID.
        """

        document_id = str(document.id)
        owner_id = str(document.owner_id)

        # ----------------------------------------------------------------------
        # Remove vectors from ChromaDB.
        # ----------------------------------------------------------------------

        if document.vector_collection:
            self.vector_store.delete_document_vectors(
                collection_name=document.vector_collection,
                document_id=document_id,
                owner_id=owner_id,
            )

        # ----------------------------------------------------------------------
        # Remove physical uploaded file.
        # ----------------------------------------------------------------------

        if delete_file:
            path = Path(document.file_path)

            if path.exists():
                path.unlink(
                    missing_ok=True,
                )

        # ----------------------------------------------------------------------
        # Remove PostgreSQL document record.
        # ----------------------------------------------------------------------

        self.db.delete(document)

        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise


__all__ = [
    "DocumentService",
]