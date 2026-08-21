"""
Logging configuration for the Enterprise Multi-Agent AI Platform.
"""

from __future__ import annotations

import logging
import logging.config
import sys

import structlog

from app.core.config import settings


def configure_logging() -> None:
    """
    Configure standard-library logging and Structlog.

    This function is intentionally safe to call multiple times.
    """

    timestamper = structlog.processors.TimeStamper(
        fmt="iso",
        utc=True,
    )

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if settings.DEBUG:
        renderer = structlog.dev.ConsoleRenderer()
    else:
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=renderer,
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(
        getattr(
            logging,
            settings.LOG_LEVEL.upper(),
            logging.INFO,
        )
    )

    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.SQL_ECHO else logging.WARNING
    )