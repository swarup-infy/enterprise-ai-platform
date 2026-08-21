"""
Enterprise AI Platform Configuration.

This module centralizes all application configuration using
Pydantic Settings. Configuration is loaded from environment
variables and `.env` files.

Features
--------
- Strong typing
- Validation
- Cached singleton settings
- Computed properties
- Environment aware
- Production ready

Author:
    Enterprise Multi-Agent AI Platform
"""

from __future__ import annotations

from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


# ==============================================================================
# Paths
# ==============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent


# ==============================================================================
# Environment
# ==============================================================================


class Environment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


# ==============================================================================
# Settings
# ==============================================================================


class Settings(BaseSettings):
    """
    Application configuration.

    Values are automatically loaded from:

    1. Environment variables
    2. .env file

    Environment variables always override .env values.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------

    APP_NAME: str = "Enterprise Multi-Agent AI Platform"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = (
        "Production-grade Enterprise Multi-Agent AI Platform"
    )

    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = True

    # ------------------------------------------------------------------
    # Server
    # ------------------------------------------------------------------

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    API_V1_PREFIX: str = "/api/v1"

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "enterprise_ai"

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str

    SQL_ECHO: bool = False

    # ------------------------------------------------------------------
    # Redis
    # ------------------------------------------------------------------

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # ------------------------------------------------------------------
    # Kafka
    # ------------------------------------------------------------------

    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"

    # ------------------------------------------------------------------
    # Groq
    # ------------------------------------------------------------------
    
    LLM_PROVIDER: str = "groq"

    GROQ_API_KEY: str

    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    GROQ_TEMPERATURE: float = Field(
        default=0.2,
        ge=0.0,
        le=2.0,
    )

    GROQ_MAX_OUTPUT_TOKENS: int = 4096

    # ------------------------------------------------------------------
    # JWT
    # ------------------------------------------------------------------

    JWT_SECRET_KEY: str

    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ------------------------------------------------------------------
    # Upload
    # ------------------------------------------------------------------

    UPLOAD_DIR: Path = BASE_DIR / "uploads"

    MAX_UPLOAD_SIZE_MB: int = 50

    ALLOWED_DOCUMENT_TYPES: List[str] = [
        "pdf",
        "docx",
        "txt",
        "md",
        "csv",
        "xlsx",
        "xls",
        "pptx",
        "html",
    ]

    # ------------------------------------------------------------------
    # Vector Database
    # ------------------------------------------------------------------

    CHROMA_DB_DIR: Path = BASE_DIR / "vector_db"

    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    LOG_LEVEL: str = "INFO"

    LOG_DIR: Path = BASE_DIR / "logs"

    # ------------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------------

    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
    ]

    # ------------------------------------------------------------------
    # Feature Flags
    # ------------------------------------------------------------------

    ENABLE_RAG: bool = True

    ENABLE_MEMORY: bool = True

    ENABLE_AGENT_TRACING: bool = True

    ENABLE_KAFKA: bool = False

    ENABLE_REDIS: bool = True

    ENABLE_OTEL: bool = False

    # ------------------------------------------------------------------
    # Computed Fields
    # ------------------------------------------------------------------

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        """PostgreSQL connection URL."""

        return (
            f"postgresql+psycopg://"
            f"{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )

    @computed_field
    @property
    def REDIS_URL(self) -> str:
        """Redis connection URL."""

        return (
            f"redis://"
            f"{self.REDIS_HOST}:"
            f"{self.REDIS_PORT}"
        )

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == Environment.PRODUCTION

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == Environment.DEVELOPMENT

    @property
    def is_testing(self) -> bool:
        return self.ENVIRONMENT == Environment.TESTING


# ==============================================================================
# Singleton
# ==============================================================================


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return cached application settings.

    Returns
    -------
    Settings
        Singleton configuration instance.
    """

    settings = Settings()

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

    return settings


settings = get_settings()