"""
Application lifecycle management.

Provides a single FastAPI lifespan context for startup and shutdown
coordination across the Enterprise AI Platform.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from time import perf_counter
from typing import Any

from fastapi import FastAPI

from app.common.logging.logger import configure_logging, get_logger
from app.core.config import settings


logger = get_logger(__name__)


async def _startup(app: FastAPI) -> None:
    """
    Initialize application-level resources.

    Resource-specific initialization should be added here only when the
    corresponding service exposes an explicit startup contract.
    """

    started_at = perf_counter()

    app.state.startup_complete = False
    app.state.shutdown_started = False

    logger.info(
        "Starting Enterprise AI Platform.",
        environment=settings.ENVIRONMENT.value,
        version=settings.APP_VERSION,
    )

    # Keep startup deterministic and lightweight.
    #
    # Database connections are created lazily by SQLAlchemy.
    # Redis/vector/AI clients should be initialized here only when their
    # implementations expose explicit async-safe lifecycle hooks.

    settings.UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )
    settings.LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )
    settings.CHROMA_DB_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    app.state.startup_complete = True

    elapsed_ms = (perf_counter() - started_at) * 1000

    logger.info(
        "Application startup completed.",
        startup_ms=round(elapsed_ms, 2),
    )


async def _shutdown(app: FastAPI) -> None:
    """
    Release application-level resources.

    Individual resources should only be closed here when they are
    explicitly created and owned by the application lifecycle.
    """

    if getattr(app.state, "shutdown_started", False):
        return

    app.state.shutdown_started = True

    logger.info(
        "Shutting down Enterprise AI Platform."
    )

    # Future owned resources should be closed here in reverse startup order.
    #
    # Example:
    # await app.state.redis.close()
    # await app.state.some_client.aclose()

    app.state.startup_complete = False

    logger.info(
        "Application shutdown completed."
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Manage application startup and shutdown.

    Any startup failure prevents the application from becoming ready.
    Shutdown errors are logged and re-raised so deployment systems can
    observe lifecycle failures.
    """

    configure_logging()

    try:
        await _startup(app)

        yield

    except BaseException:
        logger.exception(
            "Application lifecycle failed."
        )
        raise

    finally:
        try:
            await _shutdown(app)
        except BaseException:
            logger.exception(
                "Application shutdown failed."
            )
            raise


__all__ = [
    "lifespan",
]