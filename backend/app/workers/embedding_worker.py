"""
Embedding Worker.

Background worker responsible for generating embeddings
and indexing document chunks into the vector database.
"""

from __future__ import annotations

from app.common.logging.logger import get_logger
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.vector_store_service import VectorStoreService

logger = get_logger(__name__)


class EmbeddingWorker:
    """
    Background embedding worker.
    """

    def __init__(self) -> None:
        self.chunker = ChunkingService()
        self.embedder = EmbeddingService()
        self.vector_store = VectorStoreService()

    # ==========================================================================
    # Generate Embeddings
    # ==========================================================================

    async def process(
        self,
        *,
        document_id: str,
        text: str,
        collection_name: str = "documents",
    ) -> int:
        """
        Chunk text, generate embeddings and store them.
        """

        logger.info(
            "Embedding started.",
            document_id=document_id,
        )

        chunks = self.chunker.chunk(text)

        embeddings = self.embedder.embed_batch(
            [chunk.text for chunk in chunks]
        )

        ids = [
            f"{document_id}-{chunk.index}"
            for chunk in chunks
        ]

        metadatas = [
            {
                "document_id": document_id,
                "chunk": chunk.index,
            }
            for chunk in chunks
        ]

        self.vector_store.add(
            collection_name=collection_name,
            ids=ids,
            embeddings=embeddings,
            documents=[chunk.text for chunk in chunks],
            metadatas=metadatas,
        )

        logger.info(
            "Embedding completed.",
            document_id=document_id,
            chunks=len(chunks),
        )

        return len(chunks)

    # ==========================================================================
    # Health Check
    # ==========================================================================

    async def health_check(self) -> bool:
        """
        Verify embedding pipeline.
        """

        try:
            vector = self.embedder.embed("health check")

            return len(vector) > 0

        except Exception as exc:
            logger.exception(
                "Embedding worker health check failed.",
                error=str(exc),
            )

            return False


embedding_worker = EmbeddingWorker()