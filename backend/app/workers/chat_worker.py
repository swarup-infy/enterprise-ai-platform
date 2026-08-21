"""
Chat Worker.

Background worker responsible for handling chat requests
using the RAG pipeline.
"""

from __future__ import annotations

from app.common.logging.logger import get_logger
from app.graph.workflow import run_workflow
from app.services.rag_service import RAGService

logger = get_logger(__name__)


class ChatWorker:
    """
    Chat processing worker.
    """

    def __init__(self) -> None:
        self.rag = RAGService()

    # ==========================================================================
    # Chat
    # ==========================================================================

    async def chat(
        self,
        message: str,
    ) -> str:
        """
        Standard RAG chat.
        """

        logger.info(
            "Chat request received.",
            message_length=len(message),
        )

        response = await self.rag.chat(message)

        logger.info(
            "Chat request completed.",
        )

        return response

    # ==========================================================================
    # Multi-Agent Chat
    # ==========================================================================

    async def multi_agent_chat(
        self,
        message: str,
    ) -> dict:
        """
        Execute the LangGraph workflow.
        """

        logger.info(
            "Starting multi-agent workflow.",
        )

        result = await run_workflow(message)

        logger.info(
            "Workflow completed.",
        )

        return result


chat_worker = ChatWorker()