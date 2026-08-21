"""
Memory Store.

Persistent memory storage abstraction for the Enterprise AI Platform.
Can later be backed by PostgreSQL, Redis, ChromaDB, or another vector DB.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseMemoryStore(ABC):
    """
    Abstract memory store interface.
    """

    @abstractmethod
    async def save(
        self,
        key: str,
        value: Any,
    ) -> None:
        ...

    @abstractmethod
    async def load(
        self,
        key: str,
    ) -> Any | None:
        ...

    @abstractmethod
    async def delete(
        self,
        key: str,
    ) -> bool:
        ...

    @abstractmethod
    async def exists(
        self,
        key: str,
    ) -> bool:
        ...

    @abstractmethod
    async def list_keys(self) -> list[str]:
        ...


# ==============================================================================
# In-Memory Store
# ==============================================================================


class InMemoryStore(BaseMemoryStore):
    """
    Simple in-memory implementation.
    """

    def __init__(self) -> None:
        self._store: dict[str, Any] = {}

    async def save(
        self,
        key: str,
        value: Any,
    ) -> None:
        self._store[key] = value

    async def load(
        self,
        key: str,
    ) -> Any | None:
        return self._store.get(key)

    async def delete(
        self,
        key: str,
    ) -> bool:
        return self._store.pop(key, None) is not None

    async def exists(
        self,
        key: str,
    ) -> bool:
        return key in self._store

    async def list_keys(self) -> list[str]:
        return sorted(self._store.keys())

    async def clear(self) -> None:
        self._store.clear()