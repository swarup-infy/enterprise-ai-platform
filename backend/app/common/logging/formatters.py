"""
Enterprise Logging Formatters.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import UTC, datetime
from typing import Any


def clean_event_message(message: str) -> str:
    return re.sub(r"\s+", " ", str(message).strip())


def remove_empty_fields(
    data: dict[str, Any],
) -> dict[str, Any]:
    return {
        key: value
        for key, value in data.items()
        if value is not None and value != ""
    }


def uppercase_level(level: str) -> str:
    """Return a normalized uppercase log level."""
    return str(level).upper()


class ConsoleFormatter(logging.Formatter):
    """Human-readable console formatter."""

    def format(self, record: logging.LogRecord) -> str:
        return (
            f"{datetime.now(UTC).isoformat()} | "
            f"{uppercase_level(record.levelname):<8} | "
            f"{record.name} | "
            f"{clean_event_message(record.getMessage())}"
        )


class JSONFormatter(logging.Formatter):
    """Structured JSON formatter."""

    def format(self, record: logging.LogRecord) -> str:
        data: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": uppercase_level(record.levelname),
            "logger": record.name,
            "message": clean_event_message(record.getMessage()),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            data["exception"] = self.formatException(
                record.exc_info
            )

        for key, value in record.__dict__.items():
            if key.startswith("_") or key in data:
                continue

            if key in {
                "args",
                "msg",
                "exc_info",
                "exc_text",
                "stack_info",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "process",
                "processName",
            }:
                continue

            try:
                json.dumps(value)
                data[key] = value
            except (TypeError, ValueError):
                data[key] = str(value)

        return json.dumps(
            remove_empty_fields(data),
            ensure_ascii=False,
            default=str,
        )


def add_application(
    formatter: logging.Formatter,
) -> logging.Formatter:
    return formatter


def add_host(
    formatter: logging.Formatter,
) -> logging.Formatter:
    return formatter


def add_process(
    formatter: logging.Formatter,
) -> logging.Formatter:
    return formatter


def add_thread(
    formatter: logging.Formatter,
) -> logging.Formatter:
    return formatter


def add_timestamp(
    formatter: logging.Formatter,
) -> logging.Formatter:
    return formatter


def get_console_formatter() -> logging.Formatter:
    return ConsoleFormatter()


def get_json_formatter() -> logging.Formatter:
    return JSONFormatter()


__all__ = [
    "clean_event_message",
    "remove_empty_fields",
    "uppercase_level",
    "ConsoleFormatter",
    "JSONFormatter",
    "add_application",
    "add_host",
    "add_process",
    "add_thread",
    "add_timestamp",
    "get_console_formatter",
    "get_json_formatter",
]