"""
Enterprise logging middleware.

FastAPI middleware that binds request-scoped logging context.
"""

from __future__ import annotations

import time
import uuid

import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.common.logging.context import (
    bind_request_id,
    clear_context,
)

logger = structlog.get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Attach request context and log request lifecycle."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get(
            "X-Request-ID",
            str(uuid.uuid4()),
        )

        bind_request_id(request_id)

        start = time.perf_counter()

        try:
            response = await call_next(request)

        except Exception:
            logger.exception(
                "Unhandled request exception",
                method=request.method,
                path=request.url.path,
            )
            clear_context()
            raise

        latency_ms = round(
            (time.perf_counter() - start) * 1000,
            2,
        )

        response.headers["X-Request-ID"] = request_id

        logger.info(
            "HTTP request completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            latency_ms=latency_ms,
        )

        clear_context()

        return response


__all__ = ["LoggingMiddleware"]