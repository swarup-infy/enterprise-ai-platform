"""
Logging Middleware.

Logs every incoming HTTP request and outgoing response.
"""

from __future__ import annotations

import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.common.logging.logger import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Request/Response logging middleware.
    """

    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        start_time = time.perf_counter()

        logger.info(
            "Request started.",
            method=request.method,
            path=request.url.path,
            client=request.client.host if request.client else None,
        )

        try:
            response = await call_next(request)

        except Exception as exc:
            logger.exception(
                "Request failed.",
                method=request.method,
                path=request.url.path,
                error=str(exc),
            )
            raise

        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        logger.info(
            "Request completed.",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

        response.headers["X-Process-Time"] = f"{duration_ms} ms"

        return response