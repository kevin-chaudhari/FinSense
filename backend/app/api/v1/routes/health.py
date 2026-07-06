"""
FinSense AI — Health Check Routes

GET /api/v1/health      — Basic health
GET /api/v1/health/gpu  — Detailed GPU status
GET /api/v1/health/ready — Readiness probe (K8s compatible)
"""

from __future__ import annotations

from fastapi import APIRouter

from app.config import settings
from app.gpu.accelerator import gpu_accelerator
from app.gpu.detector import gpu_detector
from app.models.schemas import GPUHealthResponse, HealthResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    response_model=HealthResponse,
    summary="Application health check",
)
async def health() -> HealthResponse:
    """Basic liveness check. Returns 200 if the server is running."""
    gpu_info = gpu_detector.detect()
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        gpu={
            "cuda_available": gpu_info.cuda_available,
            "device_name": gpu_info.device_name,
        },
    )


@router.get(
    "/gpu",
    response_model=GPUHealthResponse,
    summary="Detailed GPU/CUDA status",
)
async def gpu_health() -> GPUHealthResponse:
    """Return detailed GPU capabilities and CUDA status."""
    info = gpu_detector.detect()
    return GPUHealthResponse(
        cuda_available=info.cuda_available,
        device_name=info.device_name,
        vram_gb=round(info.vram_gb, 2),
        faiss_gpu=info.faiss_gpu_available,
        mixed_precision=info.mixed_precision_supported,
    )


@router.get(
    "/ready",
    summary="Readiness probe (Kubernetes compatible)",
)
async def readiness() -> dict:
    """
    Readiness check for Kubernetes / load balancers.
    Returns 200 only when the application is fully ready to serve requests.
    """
    from app.rag.embeddings import embedding_service
    ready = embedding_service._initialized
    return {
        "ready": ready,
        "embedding_service": "ready" if ready else "initializing",
    }
