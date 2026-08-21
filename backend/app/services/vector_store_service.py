"""
Vector Store Service.

Provides a centralized, type-safe wrapper around ChromaDB for:

- Creating and retrieving collections.
- Adding document chunks and embeddings.
- Owner-isolated similarity search.
- Deleting specific vectors.
- Deleting all vectors belonging to a document.
- Counting vectors.

The service uses ChromaDB PersistentClient so vector data
survives application restarts.

Security:
    User-facing retrieval and deletion operations should always
    provide owner_id to enforce tenant/user isolation.
"""

from __future__ import annotations

from collections.abc import Sequence
from threading import Lock
from typing import Any

from chromadb import PersistentClient
from chromadb.api.models.Collection import Collection

from app.common.logging.logger import get_logger
from app.core.config import settings


logger = get_logger(__name__)


class VectorStoreService:
    """
    Centralized ChromaDB vector-store service.

    A single PersistentClient is shared by all instances created
    inside the application process.
    """

    _client: PersistentClient | None = None
    _client_lock = Lock()

    DEFAULT_COLLECTION = "documents"
    DISTANCE_METRIC = "cosine"

    # ==========================================================================
    # Initialization
    # ==========================================================================

    def __init__(self) -> None:
        """
        Initialize the shared ChromaDB client lazily.

        Thread-safe so multiple requests cannot initialize
        multiple PersistentClient instances simultaneously.
        """

        if VectorStoreService._client is None:
            with VectorStoreService._client_lock:
                if VectorStoreService._client is None:
                    VectorStoreService._client = PersistentClient(
                        path=str(settings.CHROMA_DB_DIR),
                    )

                    logger.info(
                        "ChromaDB client initialized.",
                        path=str(settings.CHROMA_DB_DIR),
                    )

    # ==========================================================================
    # Client
    # ==========================================================================

    @property
    def client(self) -> PersistentClient:
        """
        Return the shared ChromaDB client.
        """

        client = VectorStoreService._client

        if client is None:
            raise RuntimeError(
                "ChromaDB client has not been initialized."
            )

        return client

    # ==========================================================================
    # Collection
    # ==========================================================================

    @staticmethod
    def _normalize_collection_name(name: str) -> str:
        """
        Normalize and validate a collection name.
        """

        if not isinstance(name, str):
            raise TypeError(
                "Collection name must be a string."
            )

        normalized_name = name.strip()

        if not normalized_name:
            raise ValueError(
                "Collection name cannot be empty."
            )

        return normalized_name

    def get_collection(
        self,
        name: str = DEFAULT_COLLECTION,
    ) -> Collection:
        """
        Get an existing ChromaDB collection or create it.
        """

        normalized_name = self._normalize_collection_name(name)

        return self.client.get_or_create_collection(
            name=normalized_name,
            metadata={
                "hnsw:space": self.DISTANCE_METRIC,
            },
        )

    # ==========================================================================
    # Add
    # ==========================================================================

    def add(
        self,
        *,
        collection_name: str,
        ids: Sequence[str],
        embeddings: Sequence[Sequence[float]],
        documents: Sequence[str],
        metadatas: Sequence[dict[str, Any]],
    ) -> None:
        """
        Add document chunks and embeddings to ChromaDB.

        Every vector must have a unique ID.

        All supplied sequences must contain the same number
        of elements.
        """

        if not ids:
            return

        if not (
            len(ids)
            == len(embeddings)
            == len(documents)
            == len(metadatas)
        ):
            raise ValueError(
                "ids, embeddings, documents, and metadatas "
                "must contain the same number of items."
            )

        normalized_ids: list[str] = []

        for vector_id in ids:
            normalized_id = str(vector_id).strip()

            if not normalized_id:
                raise ValueError(
                    "Vector IDs cannot be empty."
                )

            normalized_ids.append(normalized_id)

        if len(set(normalized_ids)) != len(normalized_ids):
            raise ValueError(
                "Vector IDs must be unique within a single add operation."
            )

        normalized_documents: list[str] = []

        for document in documents:
            if not isinstance(document, str):
                raise TypeError(
                    "Vector documents must be strings."
                )

            normalized_documents.append(document)

        normalized_embeddings: list[list[float]] = []

        for embedding in embeddings:
            values = list(embedding)

            if not values:
                raise ValueError(
                    "Embeddings cannot be empty."
                )

            normalized_embeddings.append(
                [float(value) for value in values]
            )

        collection = self.get_collection(
            collection_name,
        )

        collection.add(
            ids=normalized_ids,
            embeddings=normalized_embeddings,
            documents=normalized_documents,
            metadatas=list(metadatas),
        )

        logger.info(
            "Vectors added to ChromaDB.",
            collection=collection_name,
            count=len(normalized_ids),
        )

    # ==========================================================================
    # Search
    # ==========================================================================

    def search(
        self,
        *,
        collection_name: str,
        embedding: Sequence[float],
        top_k: int = 5,
        owner_id: object | None = None,
    ) -> dict[str, Any]:
        """
        Perform similarity search.

        When owner_id is supplied, only vectors belonging to that
        owner are returned.

        owner_id may be a UUID or a string and is normalized to
        a string before being passed to ChromaDB.
        """

        if top_k < 1:
            raise ValueError(
                "top_k must be greater than or equal to 1."
            )

        query_embedding = list(embedding)

        if not query_embedding:
            raise ValueError(
                "Search embedding cannot be empty."
            )

        normalized_embedding = [
            float(value)
            for value in query_embedding
        ]

        collection = self.get_collection(
            collection_name,
        )

        # ----------------------------------------------------------------------
        # Owner isolation
        # ----------------------------------------------------------------------

        where: dict[str, Any] | None = None

        if owner_id is not None:
            normalized_owner_id = str(owner_id).strip()

            if not normalized_owner_id:
                raise ValueError(
                    "owner_id cannot be empty."
                )

            where = {
                "owner_id": normalized_owner_id,
            }

        # ----------------------------------------------------------------------
        # Query ChromaDB.
        #
        # ChromaDB handles the filtering before returning the requested
        # number of nearest results.
        # ----------------------------------------------------------------------

        results = collection.query(
            query_embeddings=[
                normalized_embedding,
            ],
            n_results=top_k,
            where=where,
        )

        logger.info(
            "Vector search completed.",
            collection=collection_name,
            top_k=top_k,
            owner_id=(
                str(owner_id)
                if owner_id is not None
                else None
            ),
        )

        return results

    # ==========================================================================
    # Delete
    # ==========================================================================

    def delete(
        self,
        *,
        collection_name: str,
        ids: Sequence[str],
    ) -> None:
        """
        Delete specific vectors from a collection.
        """

        if not ids:
            return

        normalized_ids = [
            str(vector_id).strip()
            for vector_id in ids
        ]

        if any(
            not vector_id
            for vector_id in normalized_ids
        ):
            raise ValueError(
                "Vector IDs cannot be empty."
            )

        collection = self.get_collection(
            collection_name,
        )

        collection.delete(
            ids=normalized_ids,
        )

        logger.info(
            "Vectors deleted from ChromaDB.",
            collection=collection_name,
            count=len(normalized_ids),
        )

    # ==========================================================================
    # Delete Document Vectors
    # ==========================================================================

    def delete_document_vectors(
        self,
        *,
        collection_name: str,
        document_id: object,
        owner_id: object | None = None,
    ) -> int:
        """
        Delete all vectors belonging to a specific document.

        Matching is performed using ChromaDB metadata.

        When owner_id is supplied, deletion is additionally restricted
        to vectors belonging to that owner.

        Returns:
            Number of deleted vectors.
        """

        normalized_document_id = str(
            document_id,
        ).strip()

        if not normalized_document_id:
            raise ValueError(
                "document_id cannot be empty."
            )

        normalized_owner_id: str | None = None

        if owner_id is not None:
            normalized_owner_id = str(
                owner_id,
            ).strip()

            if not normalized_owner_id:
                raise ValueError(
                    "owner_id cannot be empty."
                )

        collection = self.get_collection(
            collection_name,
        )

        # ----------------------------------------------------------------------
        # Build metadata filter.
        # ----------------------------------------------------------------------

        if normalized_owner_id is not None:
            where: dict[str, Any] = {
                "$and": [
                    {
                        "document_id": normalized_document_id,
                    },
                    {
                        "owner_id": normalized_owner_id,
                    },
                ],
            }
        else:
            where = {
                "document_id": normalized_document_id,
            }

        # ----------------------------------------------------------------------
        # Find matching vector IDs.
        # ----------------------------------------------------------------------

        result = collection.get(
            where=where,
        )

        ids = result.get("ids") or []

        if not ids:
            logger.info(
                "No document vectors found for deletion.",
                collection=collection_name,
                document_id=normalized_document_id,
                owner_id=normalized_owner_id,
            )

            return 0

        normalized_ids = [
            str(vector_id)
            for vector_id in ids
        ]

        # ----------------------------------------------------------------------
        # Delete matching vectors.
        # ----------------------------------------------------------------------

        collection.delete(
            ids=normalized_ids,
        )

        logger.info(
            "Document vectors deleted from ChromaDB.",
            collection=collection_name,
            document_id=normalized_document_id,
            owner_id=normalized_owner_id,
            count=len(normalized_ids),
        )

        return len(normalized_ids)

    # ==========================================================================
    # Count
    # ==========================================================================

    def count(
        self,
        collection_name: str = DEFAULT_COLLECTION,
    ) -> int:
        """
        Return the total number of vectors in a collection.
        """

        collection = self.get_collection(
            collection_name,
        )

        return collection.count()


__all__ = [
    "VectorStoreService",
]