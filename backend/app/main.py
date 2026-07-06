"""
FinSense AI — FastAPI Application Entry Point

Production-grade FastAPI application with:
- Structured logging
- Global exception handlers
- CORS middleware
- Rate limiting
- Security headers
- Health monitoring
"""

from __future__ import annotations

import time
import uuid
from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.config import settings
from app.core.exceptions import FinSenseException
from app.core.logging import get_logger, setup_logging
from app.gpu.detector import gpu_detector
from app.rag.embeddings import embedding_service

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan — startup and shutdown events."""
    # ── Startup ─────────────────────────────────────────────────────────────
    setup_logging()
    logger.info("🚀 FinSense AI v%s starting up...", settings.APP_VERSION)

    # Detect GPU capabilities
    gpu_info = gpu_detector.detect()
    if gpu_info.cuda_available:
        logger.info(
            "✅ GPU detected: %s (CUDA %s, %.1f GB VRAM)",
            gpu_info.device_name,
            gpu_info.cuda_version,
            gpu_info.vram_gb,
        )
    else:
        logger.info("ℹ️  No GPU detected — running on CPU (full functionality maintained)")

    # Pre-warm embedding service
    try:
        await embedding_service.initialize()
        logger.info("✅ Embedding service initialized (%s)", embedding_service.device)
    except Exception as exc:
        logger.warning("⚠️  Embedding service init warning: %s", exc)

    logger.info("✅ FinSense AI is ready to serve requests")
    yield

    # ── Shutdown ─────────────────────────────────────────────────────────────
    logger.info("🛑 FinSense AI shutting down...")
    await embedding_service.cleanup()
    logger.info("Goodbye!")


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "FinSense AI — Production-grade AI-powered personal finance platform "
            "with LangGraph agents, FAISS vector search, GPU acceleration, "
            "and Google Gemini integration."
        ),
        docs_url="/api/docs" if not settings.is_production else None,
        redoc_url="/api/redoc" if not settings.is_production else None,
        openapi_url="/api/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # ── Middleware ─────────────────────────────────────────────────────────
    _add_middleware(app)

    # ── Routers ───────────────────────────────────────────────────────────
    app.include_router(api_router, prefix="/api/v1")

    # ── Exception Handlers ─────────────────────────────────────────────────
    _add_exception_handlers(app)

    # ── Request Logging Middleware ─────────────────────────────────────────
    @app.middleware("http")
    async def request_logging_middleware(request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        start = time.perf_counter()
        request.state.request_id = request_id

        response: Response = await call_next(request)

        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "%s %s → %d (%.1fms) [%s]",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            request_id,
        )

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration_ms:.1f}ms"
        return response

    # ── Security Headers Middleware ────────────────────────────────────────
    @app.middleware("http")
    async def security_headers_middleware(request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        return response

    return app


def _add_middleware(app: FastAPI) -> None:
    """Register all middleware in correct order."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID", "X-Response-Time"],
    )

    if settings.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"],  # Configure in production
        )


def _add_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers."""

    @app.exception_handler(FinSenseException)
    async def finsense_exception_handler(
        request: Request, exc: FinSenseException
    ) -> JSONResponse:
        logger.warning(
            "FinSenseException [%s]: %s",
            getattr(request.state, "request_id", "?"),
            exc.message,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error_code,
                "message": exc.message,
                "request_id": getattr(request.state, "request_id", None),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception(
            "Unhandled exception [%s]: %s",
            getattr(request.state, "request_id", "?"),
            str(exc),
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again.",
                "request_id": getattr(request.state, "request_id", None),
            },
        )


# ── Application Instance ───────────────────────────────────────────────────────
app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else 4,
        log_level="debug" if settings.DEBUG else "info",
    )
