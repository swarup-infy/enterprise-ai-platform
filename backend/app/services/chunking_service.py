"""
Document Chunking Service.

Splits extracted document text into overlapping chunks for
embedding generation and RAG retrieval.

The service is intentionally deterministic and dependency-free.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TextChunk:
    """
    Represents one chunk of document text.

    Attributes:
        index: Zero-based chunk index.
        text: Chunk text.
        start: Start character offset in the normalized source text.
        end: End character offset in the normalized source text.
    """

    index: int
    text: str
    start: int
    end: int


class ChunkingService:
    """
    Split extracted document text into overlapping chunks.

    The default configuration creates approximately 1000-character
    chunks with 200 characters of overlap.
    """

    DEFAULT_CHUNK_SIZE = 1000
    DEFAULT_CHUNK_OVERLAP = 200

    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ) -> None:
        """
        Initialize the chunking service.

        Args:
            chunk_size: Maximum number of characters per chunk.
            chunk_overlap: Number of characters shared between
                consecutive chunks.

        Raises:
            TypeError: If configuration values are not integers.
            ValueError: If configuration values are invalid.
        """

        if not isinstance(chunk_size, int):
            raise TypeError(
                "chunk_size must be an integer."
            )

        if not isinstance(chunk_overlap, int):
            raise TypeError(
                "chunk_overlap must be an integer."
            )

        if isinstance(chunk_size, bool):
            raise TypeError(
                "chunk_size must be an integer."
            )

        if isinstance(chunk_overlap, bool):
            raise TypeError(
                "chunk_overlap must be an integer."
            )

        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than 0."
            )

        if chunk_overlap < 0:
            raise ValueError(
                "chunk_overlap cannot be negative."
            )

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size."
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    # ==========================================================================
    # Public API
    # ==========================================================================

    def chunk(
        self,
        text: str,
    ) -> list[TextChunk]:
        """
        Split text into overlapping chunks.

        Character offsets refer to the normalized input text.

        Args:
            text: Extracted document text.

        Returns:
            A list of TextChunk objects.

        Raises:
            TypeError: If text is not a string.
        """

        if not isinstance(text, str):
            raise TypeError(
                "text must be a string."
            )

        normalized_text = self._normalize(text)

        if not normalized_text:
            return []

        text_length = len(normalized_text)

        chunks: list[TextChunk] = []

        start = 0
        index = 0

        while start < text_length:
            end = min(
                start + self.chunk_size,
                text_length,
            )

            chunk_text = normalized_text[
                start:end
            ].strip()

            if chunk_text:
                chunks.append(
                    TextChunk(
                        index=index,
                        text=chunk_text,
                        start=start,
                        end=end,
                    )
                )

                index += 1

            # No more text remains.
            if end >= text_length:
                break

            next_start = end - self.chunk_overlap

            # Defensive guard against an invalid configuration
            # causing an infinite loop.
            if next_start <= start:
                next_start = end

            start = next_start

        return chunks

    # ==========================================================================
    # Normalization
    # ==========================================================================

    @staticmethod
    def _normalize(text: str) -> str:
        """
        Normalize extracted document text.

        Normalization:

        - Removes leading/trailing whitespace from each line.
        - Collapses repeated whitespace inside each line.
        - Removes empty lines.
        - Preserves line boundaries between meaningful lines.

        This keeps the text compact while retaining paragraph/line
        structure useful for downstream RAG processing.
        """

        if not text:
            return ""

        normalized_lines: list[str] = []

        for line in text.splitlines():
            normalized_line = " ".join(
                line.split()
            )

            if normalized_line:
                normalized_lines.append(
                    normalized_line
                )

        return "\n".join(
            normalized_lines
        ).strip()


__all__ = [
    "ChunkingService",
    "TextChunk",
] 