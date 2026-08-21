"""
Memory Service.

Long-term memory management for the Enterprise AI Platform.
Supports storing, retrieving, updating and deleting memories.
"""

from __future__ import annotations

from uuid import uuid4


class MemoryService:
    """
    Simple in-memory implementation.

    Replace with PostgreSQL + Vector DB later.
    """

    def __init__(self) -> None:
        self._memory: dict[str, dict] = {}

    # ==========================================================================
    # Create
    # ==========================================================================

    def add(
        self,
        content: str,
        metadata: dict | None = None,
    ) -> str:
        """
        Store a memory.
        """

        memory_id = str(uuid4())

        self._memory[memory_id] = {
            "id": memory_id,
            "content": content,
            "metadata": metadata or {},
        }

        return memory_id

    # ==========================================================================
    # Read
    # ==========================================================================

    def get(
        self,
        memory_id: str,
    ) -> dict | None:
        """
        Retrieve memory by ID.
        """

        return self._memory.get(memory_id)

    def list(self) -> list[dict]:
        """
        Return all memories.
        """

        return list(self._memory.values())

    # ==========================================================================
    # Update
    # ==========================================================================

    def update(
        self,
        memory_id: str,
        content: str,
    ) -> bool:
        """
        Update a memory.
        """

        if memory_id not in self._memory:
            return False

        self._memory[memory_id]["content"] = content

        return True

    # ==========================================================================
    # Delete
    # ==========================================================================

    def delete(
        self,
        memory_id: str,
    ) -> bool:
        """
        Delete a memory.
        """

        return self._memory.pop(memory_id, None) is not None

    # ==========================================================================
    # Search
    # ==========================================================================

    def search(
        self,
        query: str,
    ) -> list[dict]:
        """
        Simple keyword search.
        """

        query = query.lower()

        return [
            memory
            for memory in self._memory.values()
            if query in memory["content"].lower()
        ]

    # ==========================================================================
    # Clear
    # ==========================================================================

    def clear(self) -> None:
        """
        Remove all memories.
        """

        self._memory.clear()