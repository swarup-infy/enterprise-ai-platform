"""
Base Agent.

Abstract base class for all AI agents.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.common.logging.logger import get_logger

logger = get_logger(__name__)


class BaseAgent(ABC):
    """
    Base class for every AI agent.
    """

    def __init__(
        self,
        name: str,
        description: str,
    ) -> None:
        self.name = name
        self.description = description

    # ==========================================================================
    # Main Entry Point
    # ==========================================================================

    @abstractmethod
    async def run(
        self,
        task: str,
        **kwargs: Any,
    ) -> Any:
        """
        Execute the agent.
        """

    # ==========================================================================
    # Helpers
    # ==========================================================================

    async def before_run(
        self,
        task: str,
    ) -> None:
        logger.info(
            "Agent started.",
            agent=self.name,
            task=task,
        )

    async def after_run(
        self,
        result: Any,
    ) -> None:
        logger.info(
            "Agent finished.",
            agent=self.name,
        )

    async def execute(
        self,
        task: str,
        **kwargs: Any,
    ) -> Any:
        """
        Wrapper around run().
        """

        await self.before_run(task)

        result = await self.run(
            task,
            **kwargs,
        )

        await self.after_run(result)

        return result

    # ==========================================================================
    # Representation
    # ==========================================================================

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(name='{self.name}')"
        )