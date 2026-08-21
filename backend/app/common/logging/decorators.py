"""
Logging Decorators.

Utilities for measuring function execution time and logging
function failures.
"""

from __future__ import annotations

import functools
import time
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar, cast

from .logger import get_logger

F = TypeVar("F", bound=Callable[..., Any])


def log_execution_time(func: F) -> F:
    """
    Log execution time for synchronous and asynchronous functions.
    """

    logger = get_logger(func.__module__)

    @functools.wraps(func)
    async def async_wrapper(
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        start = time.perf_counter()

        try:
            return await func(*args, **kwargs)
        except Exception:
            logger.exception(
                "Function execution failed.",
                function=func.__qualname__,
            )
            raise
        finally:
            elapsed_ms = (
                time.perf_counter() - start
            ) * 1000

            logger.info(
                "Function execution completed.",
                function=func.__qualname__,
                latency_ms=round(elapsed_ms, 2),
            )

    @functools.wraps(func)
    def sync_wrapper(
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        start = time.perf_counter()

        try:
            return func(*args, **kwargs)
        except Exception:
            logger.exception(
                "Function execution failed.",
                function=func.__qualname__,
            )
            raise
        finally:
            elapsed_ms = (
                time.perf_counter() - start
            ) * 1000

            logger.info(
                "Function execution completed.",
                function=func.__qualname__,
                latency_ms=round(elapsed_ms, 2),
            )

    import inspect

    if inspect.iscoroutinefunction(func):
        return cast(F, async_wrapper)

    return cast(F, sync_wrapper)


__all__ = [
    "log_execution_time",
]