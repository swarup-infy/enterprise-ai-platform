"""
Task Scheduler.

Schedules and executes background jobs for the
Enterprise AI Platform.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from app.common.logging.logger import get_logger

logger = get_logger(__name__)


class TaskScheduler:
    """
    Lightweight asynchronous task scheduler.
    """

    def __init__(self) -> None:
        self._tasks: set[asyncio.Task[Any]] = set()

    # ==========================================================================
    # Schedule
    # ==========================================================================

    def schedule(
        self,
        coroutine: Awaitable[Any],
    ) -> asyncio.Task[Any]:
        """
        Schedule a coroutine.
        """

        task = asyncio.create_task(coroutine)

        self._tasks.add(task)

        task.add_done_callback(self._tasks.discard)

        logger.info(
            "Task scheduled.",
            task_id=id(task),
        )

        return task

    # ==========================================================================
    # Schedule Function
    # ==========================================================================

    def schedule_function(
        self,
        function: Callable[..., Awaitable[Any]],
        *args: Any,
        **kwargs: Any,
    ) -> asyncio.Task[Any]:
        """
        Schedule an async function.
        """

        return self.schedule(
            function(*args, **kwargs)
        )

    # ==========================================================================
    # Active Tasks
    # ==========================================================================

    def active_tasks(self) -> int:
        """
        Return number of active tasks.
        """

        return len(self._tasks)

    # ==========================================================================
    # Wait
    # ==========================================================================

    async def wait(self) -> None:
        """
        Wait for all scheduled tasks.
        """

        if self._tasks:
            await asyncio.gather(
                *self._tasks,
                return_exceptions=True,
            )

    # ==========================================================================
    # Cancel
    # ==========================================================================

    async def cancel_all(self) -> None:
        """
        Cancel every running task.
        """

        logger.info(
            "Cancelling all scheduled tasks.",
        )

        for task in list(self._tasks):
            task.cancel()

        await self.wait()

        self._tasks.clear()

        logger.info(
            "All scheduled tasks cancelled.",
        )


scheduler = TaskScheduler()