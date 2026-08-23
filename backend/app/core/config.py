"""
Enterprise AI Platform configuration.

Centralizes application settings with strong validation,
environment-aware defaults, and production-safe behavior.
"""

from __future__ import annotations

from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Environment(str, Enum):
    """Supported runtime environments."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Validated application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid",
        validate_default=True,
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
    DEBUG: bool = False

    HOST: str = "0.0.0.0"
    PORT: int = Field(default=8000, ge=1, le=65535)

    API_V1_PREFIX: str = "/api/v1"

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = Field(default=5432, ge=1, le=65535)
    POSTGRES_DB: str = "enterprise_ai"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: SecretStr

    SQL_ECHO: bool = False

    # ------------------------------------------------------------------
    # Redis
    # ------------------------------------------------------------------

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = Field(default=6379, ge=1, le=65535)

    # ------------------------------------------------------------------
    # Kafka
    # ------------------------------------------------------------------

    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"

    # ------------------------------------------------------------------
    # LLM
    # ------------------------------------------------------------------

    LLM_PROVIDER: Literal["groq"] = "groq"

    GROQ_API_KEY: SecretStr
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    GROQ_TEMPERATURE: float = Field(
        default=0.2,
        ge=0.0,
        le=2.0,
    )

    GROQ_MAX_OUTPUT_TOKENS: int = Field(
        default=4096,
        ge=1,
        le=32768,
    )

    # ------------------------------------------------------------------
    # JWT
    # ------------------------------------------------------------------

    JWT_SECRET_KEY: SecretStr
    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        ge=1,
        le=1440,
    )

    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        ge=1,
        le=365,
    )

    # ------------------------------------------------------------------
    # Uploads
    # ------------------------------------------------------------------

    UPLOAD_DIR: Path = BASE_DIR / "uploads"

    MAX_UPLOAD_SIZE_MB: int = Field(
        default=50,
        ge=1,
        le=1024,
    )

    ALLOWED_DOCUMENT_TYPES: list[str] = [
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
    # Vector database
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

    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
    ]

    # ------------------------------------------------------------------
    # Feature flags
    # ------------------------------------------------------------------

    ENABLE_RAG: bool = True
    ENABLE_MEMORY: bool = True
    ENABLE_AGENT_TRACING: bool = True
    ENABLE_KAFKA: bool = False
    ENABLE_REDIS: bool = True
    ENABLE_OTEL: bool = False

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------

    @field_validator("API_V1_PREFIX")
    @classmethod
    def validate_api_prefix(cls, value: str) -> str:
        """Normalize API prefix."""
        value = value.strip()

        if not value:
            raise ValueError("API_V1_PREFIX cannot be empty.")

        if not value.startswith("/"):
            value = f"/{value}"

        return value.rstrip("/") or "/"

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        """Validate logging level."""
        normalized = value.strip().upper()

        allowed = {
            "CRITICAL",
            "ERROR",
            "WARNING",
            "INFO",
            "DEBUG",
        }

        if normalized not in allowed:
            raise ValueError(
                f"LOG_LEVEL must be one of: "
                f"{', '.join(sorted(allowed))}."
            )

        return normalized

    @field_validator("ALLOWED_ORIGINS")
    @classmethod
    def validate_origins(
        cls,
        value: list[str],
    ) -> list[str]:
        """Normalize and validate CORS origins."""
        cleaned = []

        for origin in value:
            normalized = origin.strip().rstrip("/")

            if normalized:
                cleaned.append(normalized)

        if not cleaned:
            raise ValueError(
                "ALLOWED_ORIGINS must contain at least one origin."
            )

        return list(dict.fromkeys(cleaned))

    @field_validator("ALLOWED_DOCUMENT_TYPES")
    @classmethod
    def validate_document_types(
        cls,
        value: list[str],
    ) -> list[str]:
        """Normalize allowed document extensions."""
        cleaned = []

        for extension in value:
            normalized = extension.strip().lower().lstrip(".")

            if normalized:
                cleaned.append(normalized)

        if not cleaned:
            raise ValueError(
                "ALLOWED_DOCUMENT_TYPES cannot be empty."
            )

        return list(dict.fromkeys(cleaned))

    # ------------------------------------------------------------------
    # Environment helpers
    # ------------------------------------------------------------------

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == Environment.DEVELOPMENT

    @property
    def is_testing(self) -> bool:
        return self.ENVIRONMENT == Environment.TESTING

    @property
    def is_staging(self) -> bool:
        return self.ENVIRONMENT == Environment.STAGING

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == Environment.PRODUCTION

    # ------------------------------------------------------------------
    # Computed URLs
    # ------------------------------------------------------------------

    @property
    def DATABASE_URL(self) -> str:
        """Build the SQLAlchemy PostgreSQL URL."""
        password = self.POSTGRES_PASSWORD.get_secret_value()

        return (
            "postgresql+psycopg://"
            f"{self.POSTGRES_USER}:"
            f"{password}@"
            f"{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )

    @property
    def REDIS_URL(self) -> str:
        """Build the Redis URL."""
        return (
            f"redis://{self.REDIS_HOST}:"
            f"{self.REDIS_PORT}"
        )

    @property
    def MAX_UPLOAD_SIZE_BYTES(self) -> int:
        """Return maximum upload size in bytes."""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @property
    def groq_api_key(self) -> str:
        """Return the Groq API key."""
        return self.GROQ_API_KEY.get_secret_value()

    @property
    def jwt_secret_key(self) -> str:
        """Return the JWT signing secret."""
        return self.JWT_SECRET_KEY.get_secret_value()

    # ------------------------------------------------------------------
    # Runtime validation
    # ------------------------------------------------------------------

    def validate_production_settings(self) -> None:
        """Enforce stronger settings in production."""
        if not self.is_production:
            return

        if self.DEBUG:
            raise ValueError(
                "DEBUG must be false in production."
            )

        if (
            self.POSTGRES_PASSWORD.get_secret_value()
            in {"change-me", "password", "postgres"}
        ):
            raise ValueError(
                "A strong POSTGRES_PASSWORD is required in production."
            )

        if len(self.jwt_secret_key) < 32:
            raise ValueError(
                "JWT_SECRET_KEY must be at least 32 characters "
                "in production."
            )

        if self.groq_api_key in {
            "",
            "your-groq-api-key",
        }:
            raise ValueError(
                "A valid GROQ_API_KEY is required in production."
            )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings instance."""
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

    settings.validate_production_settings()

    return settings


settings = get_settings()


__all__ = [
    "Environment",
    "Settings",
    "get_settings",
    "settings",
]