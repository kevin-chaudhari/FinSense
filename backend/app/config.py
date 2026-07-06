"""
FinSense AI — Configuration Management

Pydantic Settings with full validation.
All values sourced from environment variables with strict typing.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support and validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ────────────────────────────────────────────────────────────
    APP_NAME: str = "FinSense AI"
    APP_VERSION: str = "2.0.0"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False

    # ── Security ───────────────────────────────────────────────────────────────
    SECRET_KEY: SecretStr = Field(..., min_length=32)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    BCRYPT_ROUNDS: int = 12

    # ── CORS ───────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"]
    )

    # ── Google / Gemini ────────────────────────────────────────────────────────
    GOOGLE_API_KEY: SecretStr = Field(...)
    GEMINI_MODEL: str = "gemini-1.5-flash-002"
    GEMINI_EMBEDDING_MODEL: str = "models/embedding-001"
    GEMINI_MAX_OUTPUT_TOKENS: int = 2048
    GEMINI_TEMPERATURE: float = Field(default=0.7, ge=0.0, le=2.0)

    # ── Storage ────────────────────────────────────────────────────────────────
    DATA_DIR: Path = Path("data")
    VECTOR_STORE_DIR: Path = Path("data/vector_stores")
    USER_DATA_DIR: Path = Path("data/users")
    LOGS_DIR: Path = Path("logs")

    # ── Rate Limiting ──────────────────────────────────────────────────────────
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 30
    RATE_LIMIT_AGENT_PER_MINUTE: int = 10

    # ── GPU / CUDA ─────────────────────────────────────────────────────────────
    ENABLE_GPU: bool = True
    GPU_DEVICE_ID: int = 0
    FAISS_USE_GPU: bool = True
    EMBEDDING_BATCH_SIZE: int = 64
    EMBEDDING_USE_GPU: bool = True
    MIXED_PRECISION: bool = True  # FP16 where supported

    # ── RAG Pipeline ───────────────────────────────────────────────────────────
    RAG_TOP_K: int = 10
    RAG_RERANK_TOP_K: int = 5
    RAG_CHUNK_SIZE: int = 512
    RAG_CHUNK_OVERLAP: int = 64
    BM25_WEIGHT: float = Field(default=0.3, ge=0.0, le=1.0)
    DENSE_WEIGHT: float = Field(default=0.7, ge=0.0, le=1.0)
    ENABLE_RERANKING: bool = True

    # ── Agent ──────────────────────────────────────────────────────────────────
    AGENT_MAX_ITERATIONS: int = 5
    AGENT_TIMEOUT_SECONDS: int = 60
    CONVERSATION_HISTORY_LIMIT: int = 20

    # ── Cookie ─────────────────────────────────────────────────────────────────
    COOKIE_SECURE: bool = Field(default=False)  # True in production (HTTPS)
    COOKIE_SAMESITE: str = "lax"

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: SecretStr) -> SecretStr:
        val = v.get_secret_value()
        if val in {"supersecret", "secret", "changeme", "password"}:
            raise ValueError("SECRET_KEY must not be a common insecure value")
        return v

    @model_validator(mode="after")
    def ensure_data_dirs(self) -> "Settings":
        for directory in [
            self.DATA_DIR,
            self.VECTOR_STORE_DIR,
            self.USER_DATA_DIR,
            self.LOGS_DIR,
        ]:
            directory.mkdir(parents=True, exist_ok=True)
        return self

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def google_api_key(self) -> str:
        return self.GOOGLE_API_KEY.get_secret_value()

    @property
    def secret_key(self) -> str:
        return self.SECRET_KEY.get_secret_value()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()


# Module-level singleton for convenience
settings = get_settings()
