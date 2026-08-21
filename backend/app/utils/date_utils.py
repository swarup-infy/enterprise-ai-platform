"""
Date Utilities.

Common date and time helper functions used across
the Enterprise AI Platform.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta


# ==============================================================================
# Current Time
# ==============================================================================


def utc_now() -> datetime:
    """
    Return current UTC time.
    """

    return datetime.now(UTC)


def local_now() -> datetime:
    """
    Return current local time.
    """

    return datetime.now()


# ==============================================================================
# Formatting
# ==============================================================================


def iso_now() -> str:
    """
    Current UTC timestamp in ISO 8601 format.
    """

    return utc_now().isoformat()


def to_iso(dt: datetime) -> str:
    """
    Convert datetime to ISO 8601.
    """

    return dt.astimezone(UTC).isoformat()


def from_iso(value: str) -> datetime:
    """
    Parse ISO 8601 datetime.
    """

    return datetime.fromisoformat(value)


# ==============================================================================
# Unix Timestamp
# ==============================================================================


def unix_timestamp(dt: datetime | None = None) -> int:
    """
    Return Unix timestamp.
    """

    dt = dt or utc_now()

    return int(dt.timestamp())


# ==============================================================================
# Time Difference
# ==============================================================================


def seconds_between(
    start: datetime,
    end: datetime,
) -> float:
    """
    Difference in seconds.
    """

    return (end - start).total_seconds()


def minutes_between(
    start: datetime,
    end: datetime,
) -> float:
    """
    Difference in minutes.
    """

    return seconds_between(start, end) / 60


def hours_between(
    start: datetime,
    end: datetime,
) -> float:
    """
    Difference in hours.
    """

    return seconds_between(start, end) / 3600


# ==============================================================================
# Date Arithmetic
# ==============================================================================


def add_days(
    dt: datetime,
    days: int,
) -> datetime:
    """
    Add days.
    """

    return dt + timedelta(days=days)


def add_hours(
    dt: datetime,
    hours: int,
) -> datetime:
    """
    Add hours.
    """

    return dt + timedelta(hours=hours)


def add_minutes(
    dt: datetime,
    minutes: int,
) -> datetime:
    """
    Add minutes.
    """

    return dt + timedelta(minutes=minutes)


# ==============================================================================
# Checks
# ==============================================================================


def is_expired(
    expires_at: datetime,
) -> bool:
    """
    Check whether a datetime has passed.
    """

    return utc_now() >= expires_at


def is_same_day(
    first: datetime,
    second: datetime,
) -> bool:
    """
    Check whether two datetimes are on the same day.
    """

    return first.date() == second.date()