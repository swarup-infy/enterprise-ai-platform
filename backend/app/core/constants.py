"""
Application constants.

Shared constants used throughout the Enterprise AI Platform.
"""

from __future__ import annotations

from enum import Enum

API_V1_PREFIX = "/api/v1"

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

DEFAULT_COLLECTION = "documents"

HEALTH_ENDPOINT = "/health"
METRICS_ENDPOINT = "/metrics"


class Environment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class AgentType(str, Enum):
    PLANNER = "planner"
    RESEARCH = "research"
    CODING = "coding"
    REVIEW = "review"
    MEMORY = "memory"


class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"


__all__ = [
    "API_V1_PREFIX",
    "DEFAULT_PAGE_SIZE",
    "MAX_PAGE_SIZE",
    "DEFAULT_EMBEDDING_MODEL",
    "DEFAULT_COLLECTION",
    "HEALTH_ENDPOINT",
    "METRICS_ENDPOINT",
    "Environment",
    "AgentType",
    "Role",
]