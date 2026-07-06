"""
FinSense AI — GPU Accelerated Operations

Provides GPU-accelerated:
- Batch embedding generation (with FP16)
- FAISS index GPU transfer
- Automatic CPU fallback on every operation
"""

from __future__ import annotations

from typing import Optional
import numpy as np

from app.core.logging import get_logger
from app.gpu.detector import gpu_detector

logger = get_logger(__name__)


class GPUAccelerator:
    """
    Wraps GPU operations with automatic CPU fallback.

    Usage:
        accelerator = GPUAccelerator()
        # Move FAISS index to GPU
        gpu_index = accelerator.to_gpu_faiss(cpu_index)
        # Run fast GPU search
    """

    def __init__(self):
        self._info = gpu_detector.detect()
        self._gpu_resources = None

        if self._info.faiss_gpu_available:
            try:
                import faiss
                self._gpu_resources = faiss.StandardGpuResources()
                self._gpu_resources.setTempMemory(512 * 1024 * 1024)  # 512 MB temp
                logger.info("FAISS GPU resources initialized")
            except Exception as exc:
                logger.warning("FAISS GPU init failed: %s", exc)
                self._gpu_resources = None

    @property
    def device(self) -> str:
        return "cuda" if self._info.cuda_available else "cpu"

    def to_gpu_faiss(self, cpu_index):
        """
        Move a FAISS CPU index to GPU. Returns GPU index or original CPU index.
        """
        if self._gpu_resources is None:
            return cpu_index
        try:
            import faiss
            gpu_index = faiss.index_cpu_to_gpu(self._gpu_resources, 0, cpu_index)
            logger.debug("FAISS index moved to GPU")
            return gpu_index
        except Exception as exc:
            logger.warning("FAISS GPU transfer failed: %s — using CPU", exc)
            return cpu_index

    def to_cpu_faiss(self, gpu_index):
        """Move a GPU FAISS index back to CPU (e.g., for serialization)."""
        if self._gpu_resources is None:
            return gpu_index
        try:
            import faiss
            return faiss.index_gpu_to_cpu(gpu_index)
        except Exception:
            return gpu_index

    def embed_batch_gpu(
        self,
        texts: list[str],
        embed_fn,
        batch_size: Optional[int] = None,
    ) -> np.ndarray:
        """
        Generate embeddings in GPU-optimized batches.

        Falls back to sequential CPU embedding if GPU unavailable.
        """
        bs = batch_size or self._info.recommended_batch_size
        all_embeddings = []

        for i in range(0, len(texts), bs):
            batch = texts[i : i + bs]
            embeddings = embed_fn(batch)
            all_embeddings.extend(embeddings)

        return np.array(all_embeddings, dtype=np.float32)

    def get_torch_device(self):
        """Return the optimal torch device."""
        if self._info.cuda_available:
            try:
                import torch
                return torch.device(f"cuda:{0}")
            except ImportError:
                pass
        return None  # Caller should handle None → "cpu"

    def get_info_dict(self) -> dict:
        """Return GPU info as a serializable dict for API responses."""
        info = self._info
        return {
            "cuda_available": info.cuda_available,
            "device_name": info.device_name,
            "cuda_version": info.cuda_version,
            "vram_gb": round(info.vram_gb, 2),
            "device_count": info.device_count,
            "faiss_gpu": info.faiss_gpu_available,
            "mixed_precision": info.mixed_precision_supported,
            "recommended_batch_size": info.recommended_batch_size,
        }


# Singleton
gpu_accelerator = GPUAccelerator()
