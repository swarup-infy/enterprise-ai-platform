"""
Embedding Service.

Generates dense vector embeddings for document chunks
using Sentence Transformers.

The embedding model is loaded once per application process
and shared across EmbeddingService instances.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from threading import Lock

from sentence_transformers import SentenceTransformer

from app.core.config import settings


class EmbeddingService:
    """
    Service responsible for generating text embeddings.

    A process-level singleton SentenceTransformer model is used
    so the model is loaded only once per application process.
    """

    DEFAULT_BATCH_SIZE = 32

    _model: SentenceTransformer | None = None
    _model_lock = Lock()

    def __init__(self) -> None:
        self._ensure_model_loaded()

    # ==========================================================================
    # Model
    # ==========================================================================

    @classmethod
    def _ensure_model_loaded(cls) -> None:
        """
        Load the embedding model exactly once per process.

        A lock prevents multiple threads from attempting to load
        the model simultaneously.
        """

        if cls._model is not None:
            return

        with cls._model_lock:
            if cls._model is not None:
                return

            model_name = settings.EMBEDDING_MODEL

            if not model_name:
                raise RuntimeError(
                    "EMBEDDING_MODEL is not configured."
                )

            cls._model = SentenceTransformer(
                model_name,
            )

    @property
    def model(self) -> SentenceTransformer:
        """
        Return the shared embedding model.
        """

        self._ensure_model_loaded()

        model = EmbeddingService._model

        if model is None:
            raise RuntimeError(
                "Embedding model failed to initialize."
            )

        return model

    # ==========================================================================
    # Single Embedding
    # ==========================================================================

    def embed(
        self,
        text: str,
    ) -> list[float]:
        """
        Generate an embedding for one text.

        Args:
            text: Text to embed.

        Returns:
            Normalized embedding vector.

        Raises:
            TypeError: If text is not a string.
            ValueError: If text is empty.
        """

        if not isinstance(text, str):
            raise TypeError(
                "text must be a string."
            )

        normalized_text = text.strip()

        if not normalized_text:
            raise ValueError(
                "Cannot generate an embedding for empty text."
            )

        embedding = self.model.encode(
            normalized_text,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        return [
            float(value)
            for value in embedding.tolist()
        ]

    # ==========================================================================
    # Batch Embedding
    # ==========================================================================

    def embed_batch(
        self,
        texts: Iterable[str],
        *,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.

        The method preserves a strict one-to-one relationship between
        input texts and returned embeddings.

        Empty or invalid text is rejected instead of silently removed.
        This is important for document chunk processing because the
        number of embeddings must match the number of chunks.

        Args:
            texts: Iterable containing text strings.
            batch_size: Number of texts processed per model batch.

        Returns:
            List of normalized embedding vectors.

        Raises:
            TypeError: If an input is not a string or batch_size is invalid.
            ValueError: If an input text is empty or no texts are supplied.
        """

        if not isinstance(batch_size, int):
            raise TypeError(
                "batch_size must be an integer."
            )

        if isinstance(batch_size, bool):
            raise TypeError(
                "batch_size must be an integer."
            )

        if batch_size <= 0:
            raise ValueError(
                "batch_size must be greater than 0."
            )

        text_list = list(texts)

        if not text_list:
            return []

        normalized_texts: list[str] = []

        for index, text in enumerate(text_list):
            if not isinstance(text, str):
                raise TypeError(
                    f"Text at index {index} must be a string."
                )

            normalized_text = text.strip()

            if not normalized_text:
                raise ValueError(
                    f"Text at index {index} cannot be empty."
                )

            normalized_texts.append(
                normalized_text
            )

        embeddings = self.model.encode(
            normalized_texts,
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        result = [
            [
                float(value)
                for value in embedding
            ]
            for embedding in embeddings.tolist()
        ]

        if len(result) != len(normalized_texts):
            raise RuntimeError(
                "Embedding count does not match input text count."
            )

        return result

    # ==========================================================================
    # Similarity
    # ==========================================================================

    def similarity(
        self,
        embedding_a: Sequence[float],
        embedding_b: Sequence[float],
    ) -> float:
        """
        Calculate cosine similarity between two normalized vectors.

        Since the service generates normalized embeddings, cosine
        similarity is equivalent to the dot product.

        Args:
            embedding_a: First embedding vector.
            embedding_b: Second embedding vector.

        Returns:
            Cosine similarity score.

        Raises:
            ValueError: If vectors are empty or have different dimensions.
        """

        if not embedding_a or not embedding_b:
            raise ValueError(
                "Embeddings cannot be empty."
            )

        if len(embedding_a) != len(embedding_b):
            raise ValueError(
                "Embedding dimensions must match."
            )

        try:
            values_a = [
                float(value)
                for value in embedding_a
            ]

            values_b = [
                float(value)
                for value in embedding_b
            ]
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Embeddings must contain numeric values."
            ) from exc

        return float(
            sum(
                a * b
                for a, b in zip(
                    values_a,
                    values_b,
                    strict=True,
                )
            )
        )

    # ==========================================================================
    # Model Information
    # ==========================================================================

    @staticmethod
    def model_name() -> str:
        """
        Return the configured embedding model name.
        """

        model_name = settings.EMBEDDING_MODEL

        if not model_name:
            raise RuntimeError(
                "EMBEDDING_MODEL is not configured."
            )

        return model_name


__all__ = [
    "EmbeddingService",
]