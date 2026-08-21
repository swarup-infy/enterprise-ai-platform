"""
Document API.

Upload, retrieve, update, delete and list documents.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
    status,
)

from app.api.deps import CurrentUser, DBSession
from app.db.database import SessionLocal
from app.schemas.document import (
    DocumentDeleteResponse,
    DocumentResponse,
    DocumentUpdate,
    DocumentUploadResponse,
)
from app.services.document_service import DocumentService
from app.services.upload_service import UploadService
from app.workers.background_worker import background_worker
from app.workers.document_worker import document_worker


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


# ==============================================================================
# Helpers
# ==============================================================================


def _get_owner_id(current_user: dict) -> UUID:
    """
    Extract and validate the authenticated user's UUID.
    """

    subject = current_user.get("sub")

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return UUID(str(subject))
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


# ==============================================================================
# Background Processing
# ==============================================================================


async def _process_document_in_background(
    document_id: UUID,
) -> None:
    """
    Process a document using an independent database session.

    A new SQLAlchemy session is created because the request-scoped
    database session must not be reused after the HTTP request ends.
    """

    db = SessionLocal()

    try:
        document = DocumentService(db).get_document(
            document_id,
        )

        if document is None:
            raise RuntimeError(
                "Document not found during background processing: "
                f"{document_id}"
            )

        await document_worker.process_document(
            document=document,
            db=db,
        )

    except Exception:
        from app.common.logging.logger import get_logger

        logger = get_logger(__name__)

        logger.exception(
            "Background document processing failed.",
            document_id=str(document_id),
        )

    finally:
        db.close()


# ==============================================================================
# Upload
# ==============================================================================


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    db: DBSession = None,
    current_user: CurrentUser = None,
):
    """
    Upload a document and schedule background processing.

    Upload validation, checksum generation, duplicate detection,
    storage, and document creation are handled by UploadService.

    The document is associated with the authenticated user.
    """

    owner_id = _get_owner_id(current_user)

    service = UploadService(db)

    document = await service.upload_file(
        owner_id=owner_id,
        file=file,
    )

    # --------------------------------------------------------------------------
    # Schedule background processing only for a newly created document.
    #
    # If UploadService returns an existing document because the same owner
    # already uploaded the file, it should not be processed again.
    # --------------------------------------------------------------------------

    if not document.is_processed:
        background_worker.submit(
            _process_document_in_background(
                document.id,
            )
        )

    return DocumentUploadResponse(
        id=document.id,
        filename=document.filename,
        message="Document uploaded successfully.",
    )


# ==============================================================================
# Get Document
# ==============================================================================


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
async def get_document(
    document_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Retrieve a document belonging to the authenticated user.

    A document owned by another user is intentionally returned as
    not found to avoid leaking its existence.
    """

    owner_id = _get_owner_id(current_user)

    service = DocumentService(db)

    document = service.get_document_for_owner(
        document_id=document_id,
        owner_id=owner_id,
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    return document


# ==============================================================================
# List Documents
# ==============================================================================


@router.get(
    "/",
    response_model=list[DocumentResponse],
)
async def list_documents(
    db: DBSession,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 20,
):
    """
    List only documents belonging to the authenticated user.
    """

    if skip < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="skip must be greater than or equal to 0.",
        )

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="limit must be between 1 and 100.",
        )

    owner_id = _get_owner_id(current_user)

    service = DocumentService(db)

    return service.list_documents(
        owner_id=owner_id,
        skip=skip,
        limit=limit,
    )


# ==============================================================================
# Update
# ==============================================================================


@router.put(
    "/{document_id}",
    response_model=DocumentResponse,
)
async def update_document(
    document_id: UUID,
    data: DocumentUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Update metadata only for a document belonging to the
    authenticated user.
    """

    owner_id = _get_owner_id(current_user)

    service = DocumentService(db)

    document = service.get_document_for_owner(
        document_id=document_id,
        owner_id=owner_id,
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    return service.update_document(
        document,
        data,
    )


# ==============================================================================
# Delete
# ==============================================================================


@router.delete(
    "/{document_id}",
    response_model=DocumentDeleteResponse,
)
async def delete_document(
    document_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Delete only a document belonging to the authenticated user.

    The physical uploaded file is also removed.
    """

    owner_id = _get_owner_id(current_user)

    service = DocumentService(db)

    document = service.get_document_for_owner(
        document_id=document_id,
        owner_id=owner_id,
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    service.delete_document(
        document,
        delete_file=True,
    )

    return DocumentDeleteResponse(
        message="Document deleted successfully.",
    )


__all__ = [
    "router",
]