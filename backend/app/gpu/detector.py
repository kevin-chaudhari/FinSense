# GPU/CUDA Detector — FinSense AI
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class GPUInfo:
    """GPU capability report."""
    cuda_available: bool = False
    device_count: int = 0
    device_name: Optional[str] = None
    cuda_version: Optional[str] = None
    vram_gb: float = 0.0
    compute_capability: Optional[tuple[int, int]] = None
    faiss_gpu_available: bool = False
    torch_available: bool = False
    mixed_precision_supported: bool = False
    recommended_batch_size: int = 64


class GPUDetector:
    """
    Detects CUDA availability and GPU capabilities.

    Gracefully handles missing dependencies — always falls back to CPU.
    """

    _info: Optional[GPUInfo] = None

    def detect(self) -> GPUInfo:
        """Detect GPU capabilities (cached after first call)."""
        if self._info is not None:
            return self._info

        info = GPUInfo()

        # ── Check PyTorch CUDA ────────────────────────────────────────────────
        try:
            import torch

            info.torch_available = True

            if torch.cuda.is_available():
                info.cuda_available = True
                info.device_count = torch.cuda.device_count()
                info.device_name = torch.cuda.get_device_name(0)
                info.cuda_version = torch.version.cuda or "unknown"

                # VRAM
                props = torch.cuda.get_device_properties(0)
                info.vram_gb = props.total_memory / (1024 ** 3)
                info.compute_capability = (props.major, props.minor)

                # Mixed precision (Ampere+ → compute ≥ 8.0)
                info.mixed_precision_supported = props.major >= 7

                # Batch size recommendation based on VRAM
                if info.vram_gb >= 16:
                    info.recommended_batch_size = 256
                elif info.vram_gb >= 8:
                    info.recommended_batch_size = 128
                elif info.vram_gb >= 4:
                    info.recommended_batch_size = 64
                else:
                    info.recommended_batch_size = 32

                logger.info(
                    "GPU: %s | CUDA %s | %.1f GB VRAM | compute %d.%d",
                    info.device_name,
                    info.cuda_version,
                    info.vram_gb,
                    *info.compute_capability,
                )
            else:
                logger.info("PyTorch available but CUDA not detected → using CPU")

        except ImportError:
            logger.info("PyTorch not installed → CPU-only mode")

        # ── Check FAISS-GPU ───────────────────────────────────────────────────
        if info.cuda_available:
            try:
                import faiss

                if hasattr(faiss, "StandardGpuResources"):
                    info.faiss_gpu_available = True
                    logger.info("✅ faiss-gpu available")
                else:
                    logger.info("ℹ️  faiss-cpu installed (no GPU search)")
            except ImportError:
                logger.info("FAISS not installed")

        self._info = info
        return info

    @property
    def is_gpu_available(self) -> bool:
        return self.detect().cuda_available

    @property
    def device_name(self) -> str:
        info = self.detect()
        return info.device_name or "CPU"


# Singleton
gpu_detector = GPUDetector()
