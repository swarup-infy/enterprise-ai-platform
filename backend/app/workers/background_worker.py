"""
Background Worker.

Executes asynchronous background jobs for the
Enterprise AI Platform.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from app.common.logging.logger import get_logger

logger = get_logger(__name__)


class BackgroundWorker:
    """
    Simple asynchronous background task worker.
    """

    def __init__(self) -> None:
        self.tasks: set[asyncio.Task[Any]] = set()

    # ==========================================================================
    # Submit Task
    # ==========================================================================

    def submit(
        self,
        coroutine: Awaitable[Any],
    ) -> asyncio.Task[Any]:
        """
        Schedule a background coroutine.
        """

        task = asyncio.create_task(coroutine)

        self.tasks.add(task)

        task.add_done_callback(self.tasks.discard)

        logger.info(
            "Background task submitted.",
            task=str(task),
        )

        return task

    # ==========================================================================
    # Run Function
    # ==========================================================================

    def submit_function(
        self,
        function: Callable[..., Awaitable[Any]],
        *args: Any,
        **kwargs: Any,
    ) -> asyncio.Task[Any]:
        """
        Schedule an async function.
        """

        return self.submit(
            function(*args, **kwargs)
        )

    # ==========================================================================
    # Wait
    # ==========================================================================

    async def wait(self) -> None:
        """
        Wait for all tasks.
        """

        if self.tasks:
            await asyncio.gather(
                *self.tasks,
                return_exceptions=True,
            )

    # ==========================================================================
    # Cancel
    # ==========================================================================

    async def cancel_all(self) -> None:
        """
        Cancel every running task.
        """

        for task in self.tasks:
            task.cancel()

        await self.wait()

        logger.info(
            "All background tasks cancelled."
        )


background_worker = BackgroundWorker()