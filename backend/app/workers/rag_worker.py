"""
RAG Worker.

Background worker responsible for Retrieval-Augmented
Generation (RAG) queries.
"""

from __future__ import annotations

from app.common.logging.logger import get_logger
from app.services.rag_service import RAGService

logger = get_logger(__name__)


class RAGWorker:
    """
    Worker responsible for executing RAG requests.
    """

    def __init__(self) -> None:
        self.rag = RAGService()

    # ==========================================================================
    # Query
    # ==========================================================================

    async def query(
        self,
        question: str,
        collection_name: str = "documents",
        top_k: int = 5,
    ) -> str:
        """
        Execute a Retrieval-Augmented Generation query.
        """

        logger.info(
            "RAG query started.",
            collection=collection_name,
        )

        answer = await self.rag.ask(
            query=question,
            collection_name=collection_name,
            top_k=top_k,
        )

        logger.info(
            "RAG query completed.",
        )

        return answer

    # ==========================================================================
    # Health Check
    # ==========================================================================

    async def health_check(self) -> bool:
        """
        Verify the RAG pipeline.
        """

        try:
            await self.rag.ask(
                query="Health check",
                top_k=1,
            )

            return True

        except Exception as exc:
            logger.exception(
                "RAG health check failed.",
                error=str(exc),
            )

            return False


rag_worker = RAGWorker()