"""
File Upload Service.

Handles secure file uploads, validation,
checksum generation, storage, and document creation.
"""

from __future__ import annotations

import hashlib
import shutil
import uuid
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.document import Document
from app.services.document_service import DocumentService


class UploadService:
    """Service responsible for secure file uploads."""

    CHUNK_SIZE = 1024 * 1024  # 1 MB

    def __init__(self, db: Session) -> None:
        self.db = db
        self.document_service = DocumentService(db)

        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.max_upload_size = (
            settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        )

        self.allowed_extensions = {
            f".{extension.lower().lstrip('.')}"
            for extension in settings.ALLOWED_DOCUMENT_TYPES
        }

    # ==========================================================================
    # Upload
    # ==========================================================================

    async def upload_file(
        self,
        *,
        owner_id: UUID,
        file: UploadFile,
    ) -> Document:
        """
        Validate and store an uploaded file.

        Validation includes:

        - Required filename.
        - Allowed file extension.
        - Maximum file size.
        - SHA-256 checksum generation.
        - Tenant-scoped duplicate detection.
        - Unique server-side filename.
        - Cleanup on failure.
        - Protection against concurrent duplicate uploads.
        """

        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required.",
            )

        original_filename = Path(file.filename).name

        if not original_filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid filename.",
            )

        extension = Path(original_filename).suffix.lower()

        if extension not in self.allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type.",
            )

        unique_name = f"{uuid.uuid4().hex}{extension}"
        destination = self.upload_dir / unique_name

        sha256 = hashlib.sha256()
        size = 0

        try:
            with destination.open("wb") as buffer:
                while chunk := await file.read(self.CHUNK_SIZE):
                    size += len(chunk)

                    if size > self.max_upload_size:
                        raise HTTPException(
                            status_code=(
                                status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
                            ),
                            detail=(
                                "File size exceeds the maximum allowed "
                                f"size of {settings.MAX_UPLOAD_SIZE_MB} MB."
                            ),
                        )

                    sha256.update(chunk)
                    buffer.write(chunk)

            checksum = sha256.hexdigest()

            # ------------------------------------------------------------------
            # Fast duplicate check.
            # ------------------------------------------------------------------

            existing = self.document_service.get_by_checksum(
                owner_id=owner_id,
                checksum=checksum,
            )

            if existing:
                destination.unlink(missing_ok=True)
                return existing

            # ------------------------------------------------------------------
            # Create document.
            #
            # The database has a UNIQUE(owner_id, checksum) constraint.
            # The IntegrityError handler below protects against two concurrent
            # uploads of the same file by the same owner.
            # ------------------------------------------------------------------

            try:
                document = self.document_service.create_document(
                    owner_id=owner_id,
                    filename=unique_name,
                    original_filename=original_filename,
                    file_path=str(destination),
                    mime_type=(
                        file.content_type
                        or "application/octet-stream"
                    ),
                    file_size=size,
                    checksum=checksum,
                )

            except IntegrityError:
                self.db.rollback()

                existing = self.document_service.get_by_checksum(
                    owner_id=owner_id,
                    checksum=checksum,
                )

                if existing:
                    destination.unlink(missing_ok=True)
                    return existing

                raise

            return document

        except HTTPException:
            destination.unlink(missing_ok=True)
            raise

        except Exception:
            destination.unlink(missing_ok=True)
            raise

        finally:
            await file.close()

    # ==========================================================================
    # Delete Physical File
    # ==========================================================================

    def delete_file(
        self,
        document: Document,
    ) -> None:
        """
        Delete the physical file associated with a document.
        """

        path = Path(document.file_path)

        if path.exists():
            path.unlink(missing_ok=True)

    # ==========================================================================
    # Copy File
    # ==========================================================================

    def copy_file(
        self,
        source: Path,
        destination: Path,
    ) -> None:
        """
        Copy a file from source to destination.
        """

        shutil.copy2(
            source,
            destination,
        )


__all__ = [
    "UploadService",
]