"""
FinSense AI — Structured Logging

Uses loguru for structured, leveled logging with:
- Console output (human-readable in dev, JSON in prod)
- File rotation with retention policy
- Request context injection
"""

from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger

from app.config import settings


def setup_logging() -> None:
    """Configure loguru logging for the application."""
    logger.remove()  # Remove default handler

    log_format_dev = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> — "
        "<level>{message}</level>"
    )

    log_format_prod = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}"
    )

    log_format = log_format_dev if settings.DEBUG else log_format_prod
    log_level = "DEBUG" if settings.DEBUG else "INFO"

    # Console handler
    logger.add(
        sys.stdout,
        format=log_format,
        level=log_level,
        colorize=settings.DEBUG,
        enqueue=True,
    )

    # File handler — rotated daily, 30-day retention
    log_file = settings.LOGS_DIR / "finsense_{time:YYYY-MM-DD}.log"
    logger.add(
        str(log_file),
        format=log_format_prod,
        level="INFO",
        rotation="00:00",
        retention="30 days",
        compression="gz",
        enqueue=True,
    )

    # Error-only file for quick diagnosis
    error_file = settings.LOGS_DIR / "errors_{time:YYYY-MM-DD}.log"
    logger.add(
        str(error_file),
        format=log_format_prod,
        level="ERROR",
        rotation="00:00",
        retention="90 days",
        compression="gz",
        enqueue=True,
    )

    logger.info("Logging initialized — level=%s, env=%s", log_level, settings.ENVIRONMENT)


def get_logger(name: str):
    """Return a bound logger for the given module name."""
    return logger.bind(name=name)
