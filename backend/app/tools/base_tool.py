"""
Base Tool.

Abstract base class for all tools used by AI agents.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """
    Base class for every tool.
    """

    def __init__(
        self,
        name: str,
        description: str,
    ) -> None:
        self.name = name
        self.description = description

    # ==========================================================================
    # Execute
    # ==========================================================================

    @abstractmethod
    async def execute(
        self,
        **kwargs: Any,
    ) -> Any:
        """
        Execute the tool.
        """

    # ==========================================================================
    # Validation
    # ==========================================================================

    async def validate(
        self,
        **kwargs: Any,
    ) -> bool:
        """
        Validate tool input.
        """

        return True

    # ==========================================================================
    # Metadata
    # ==========================================================================

    def metadata(self) -> dict[str, Any]:
        """
        Return tool metadata.
        """

        return {
            "name": self.name,
            "description": self.description,
        }

    # ==========================================================================
    # Representation
    # ==========================================================================

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(name='{self.name}')"
        )