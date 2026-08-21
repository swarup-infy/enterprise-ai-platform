"""
Document Search Tool.

Semantic document search using the platform's vector store.
"""

from __future__ import annotations

from typing import Any

from app.services.embedding_service import EmbeddingService
from app.services.vector_store_service import VectorStoreService
from app.tools.base_tool import BaseTool


class DocumentSearchTool(BaseTool):
    """
    Search indexed documents using vector similarity.
    """

    def __init__(self) -> None:
        super().__init__(
            name="document_search",
            description="Semantic search over uploaded documents.",
        )

        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStoreService()

    # ==========================================================================
    # Execute
    # ==========================================================================

    async def execute(
        self,
        query: str,
        collection_name: str = "documents",
        top_k: int = 5,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Perform semantic document search.
        """

        embedding = self.embedding_service.embed(query)

        results = self.vector_store.search(
            collection_name=collection_name,
            embedding=embedding,
            top_k=top_k,
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        output: list[dict[str, Any]] = []

        for doc, meta, distance in zip(
            documents,
            metadatas,
            distances,
        ):
            output.append(
                {
                    "document": doc,
                    "metadata": meta,
                    "score": 1 - distance,
                }
            )

        return output

    # ==========================================================================
    # Count Indexed Documents
    # ==========================================================================

    async def count(
        self,
        collection_name: str = "documents",
    ) -> int:
        """
        Return number of indexed vectors.
        """

        return self.vector_store.count(collection_name)
        