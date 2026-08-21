"""
Enterprise Logging Handlers.

Improved production-oriented handler factories.
"""

from __future__ import annotations

import logging
import logging.handlers
import queue
from pathlib import Path
from typing import Final

from app.core.config import settings

LOG_DIR: Final[Path] = settings.LOG_DIR
LOG_DIR.mkdir(parents=True, exist_ok=True)

APP_LOG: Final[Path] = LOG_DIR / "application.log"
ERROR_LOG: Final[Path] = LOG_DIR / "error.log"

MAX_BYTES: Final[int] = getattr(settings, "LOG_MAX_BYTES", 20 * 1024 * 1024)
BACKUP_COUNT: Final[int] = getattr(settings, "LOG_BACKUP_COUNT", 10)

LOG_QUEUE: Final[queue.SimpleQueue[logging.LogRecord]] = queue.SimpleQueue()


def _configure_handler(handler: logging.Handler, level: int) -> logging.Handler:
    """Apply common configuration to a handler."""
    handler.setLevel(level)
    return handler


def create_queue_handler() -> logging.handlers.QueueHandler:
    return logging.handlers.QueueHandler(LOG_QUEUE)


def create_console_handler() -> logging.StreamHandler:
    level = logging.DEBUG if settings.DEBUG else logging.INFO
    return _configure_handler(logging.StreamHandler(), level)


def create_app_file_handler() -> logging.handlers.RotatingFileHandler:
    handler = logging.handlers.RotatingFileHandler(
        APP_LOG,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    return _configure_handler(handler, logging.INFO)


def create_error_file_handler() -> logging.handlers.RotatingFileHandler:
    handler = logging.handlers.RotatingFileHandler(
        ERROR_LOG,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    return _configure_handler(handler, logging.ERROR)


def create_queue_listener(
    *handlers: logging.Handler,
) -> logging.handlers.QueueListener:
    return logging.handlers.QueueListener(
        LOG_QUEUE,
        *handlers,
        respect_handler_level=True,
    )


def create_default_handlers() -> list[logging.Handler]:
    return [
        create_console_handler(),
        create_app_file_handler(),
        create_error_file_handler(),
    ]


def build_default_queue_listener() -> logging.handlers.QueueListener:
    return create_queue_listener(
        create_console_handler(),
        create_app_file_handler(),
        create_error_file_handler(),
    )


def configure_handler_levels(
    handlers: list[logging.Handler],
    level: int,
) -> None:
    for handler in handlers:
        handler.setLevel(level)


def start_queue_listener(
    listener: logging.handlers.QueueListener,
) -> None:
    listener.start()


def stop_queue_listener(
    listener: logging.handlers.QueueListener,
) -> None:
    try:
        listener.enqueue_sentinel()
    except Exception:
        pass
    listener.stop()


def shutdown_logging() -> None:
    logging.shutdown()


__all__ = [
    "create_queue_handler",
    "create_console_handler",
    "create_app_file_handler",
    "create_error_file_handler",
    "create_queue_listener",
    "create_default_handlers",
    "build_default_queue_listener",
    "configure_handler_levels",
    "start_queue_listener",
    "stop_queue_listener",
    "shutdown_logging",
]
