"""
Document Worker.

Processes uploaded documents through the RAG ingestion pipeline:

1. Extract text.
2. Split text into chunks.
3. Generate embeddings.
4. Store chunks and embeddings in ChromaDB.
5. Mark the document as processed.

Each vector contains the document owner ID so that RAG retrieval
can enforce user-level data isolation.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.common.logging.logger import get_logger
from app.models.document import Document
from app.services.chunking_service import ChunkingService
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService
from app.services.extractor_service import ExtractorService
from app.services.vector_store_service import VectorStoreService


logger = get_logger(__name__)


class DocumentWorker:
    """Background document processing worker."""

    COLLECTION_NAME = "documents"

    def __init__(self) -> None:
        self.extractor = ExtractorService()
        self.chunker = ChunkingService()
        self.embedder = EmbeddingService()
        self.vector_store = VectorStoreService()

    # ==========================================================================
    # Process Document
    # ==========================================================================

    async def process_document(
        self,
        *,
        document: Document,
        db: Session,
    ) -> None:
        """
        Process one uploaded document.

        The document must already exist in PostgreSQL and contain
        a valid owner ID.

        Processing is considered successful only after vectors have
        been stored and the PostgreSQL document has been marked as
        processed.

        If vector storage succeeds but a later processing step fails,
        the vectors belonging to this document are removed so the
        document can be safely retried.
        """

        document_id = str(document.id)
        owner_id = str(document.owner_id)

        logger.info(
            "Starting document processing.",
            document_id=document_id,
            owner_id=owner_id,
        )

        vectors_written = False

        try:
            # ------------------------------------------------------------------
            # 1. Extract text
            # ------------------------------------------------------------------

            text = self.extractor.extract(
                document.file_path,
            )

            if not text or not text.strip():
                raise ValueError(
                    f"No text extracted from document {document_id}."
                )

            # ------------------------------------------------------------------
            # 2. Chunk text
            # ------------------------------------------------------------------

            chunks = self.chunker.chunk(text)

            if not chunks:
                raise ValueError(
                    f"No chunks generated for document {document_id}."
                )

            # ------------------------------------------------------------------
            # 3. Generate embeddings
            # ------------------------------------------------------------------

            chunk_texts = [
                chunk.text
                for chunk in chunks
            ]

            embeddings = self.embedder.embed_batch(
                chunk_texts,
            )

            if len(embeddings) != len(chunks):
                raise RuntimeError(
                    "Embedding count does not match chunk count."
                )

            # ------------------------------------------------------------------
            # 4. Build deterministic vector IDs
            # ------------------------------------------------------------------

            ids = [
                f"{document_id}-{chunk.index}"
                for chunk in chunks
            ]

            # ------------------------------------------------------------------
            # 5. Build tenant-isolated metadata
            # ------------------------------------------------------------------

            metadatas = [
                {
                    "document_id": document_id,
                    "owner_id": owner_id,
                    "chunk": chunk.index,
                    "filename": document.original_filename,
                }
                for chunk in chunks
            ]

            # ------------------------------------------------------------------
            # 6. Store vectors
            # ------------------------------------------------------------------

            self.vector_store.add(
                collection_name=self.COLLECTION_NAME,
                ids=ids,
                embeddings=embeddings,
                documents=chunk_texts,
                metadatas=metadatas,
            )

            vectors_written = True

            # ------------------------------------------------------------------
            # 7. Mark document as processed
            # ------------------------------------------------------------------

            DocumentService(db).mark_processed(
                document=document,
                embedding_model=self.embedder.model_name(),
                vector_collection=self.COLLECTION_NAME,
            )

            logger.info(
                "Document processed successfully.",
                document_id=document_id,
                owner_id=owner_id,
                chunks=len(chunks),
            )

        except Exception:
            logger.exception(
                "Document processing failed.",
                document_id=document_id,
                owner_id=owner_id,
            )

            # ------------------------------------------------------------------
            # Cleanup vectors created during this processing attempt.
            #
            # The document remains is_processed=False because
            # mark_processed() was not successfully completed.
            # ------------------------------------------------------------------

            if vectors_written:
                try:
                    self.vector_store.delete_document_vectors(
                        collection_name=self.COLLECTION_NAME,
                        document_id=document_id,
                        owner_id=owner_id,
                    )

                    logger.info(
                        "Cleaned up vectors after failed document processing.",
                        document_id=document_id,
                        owner_id=owner_id,
                    )

                except Exception:
                    logger.exception(
                        "Failed to clean up vectors after document "
                        "processing failure.",
                        document_id=document_id,
                        owner_id=owner_id,
                    )

            raise


# ==============================================================================
# Shared Worker Instance
# ==============================================================================

document_worker = DocumentWorker()


__all__ = [
    "DocumentWorker",
    "document_worker",
]