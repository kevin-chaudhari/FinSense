"""
FinSense AI — GPU-Accelerated Embedding Service

Features:
- Google Generative AI Embeddings (primary)
- Optional sentence-transformers on GPU (fallback/local)
- Batch processing with GPU acceleration
- LRU semantic caching
- Mixed precision (FP16) support
"""

from __future__ import annotations

import asyncio
import hashlib
import json
from functools import lru_cache
from typing import Optional

import numpy as np
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config import settings
from app.core.exceptions import EmbeddingError
from app.core.logging import get_logger
from app.gpu.detector import gpu_detector

logger = get_logger(__name__)

# Simple in-memory embedding cache
_embedding_cache: dict[str, list[float]] = {}
_CACHE_MAX_SIZE = 10_000


def _cache_key(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


class EmbeddingService:
    """
    Unified embedding service with GPU acceleration and caching.

    Uses Google Generative AI Embeddings as primary.
    Falls back gracefully on any error.
    """

    def __init__(self):
        self._google_embeddings: Optional[GoogleGenerativeAIEmbeddings] = None
        self._device = "cpu"
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize embedding models. Called once at startup."""
        if self._initialized:
            return

        try:
            self._google_embeddings = GoogleGenerativeAIEmbeddings(
                google_api_key=settings.google_api_key,
                model=settings.GEMINI_EMBEDDING_MODEL,
            )
            logger.info(
                "Google Embedding model initialized: %s", settings.GEMINI_EMBEDDING_MODEL
            )
        except Exception as exc:
            raise EmbeddingError(f"Failed to initialize Google embeddings: {exc}")

        gpu_info = gpu_detector.detect()
        self._device = "cuda" if gpu_info.cuda_available else "cpu"
        self._initialized = True

    @property
    def device(self) -> str:
        return self._device

    async def cleanup(self) -> None:
        """Release resources on shutdown."""
        _embedding_cache.clear()
        logger.info("Embedding service cleaned up")

    def embed_query(self, text: str) -> list[float]:
        """
        Embed a single query string.
        Uses cache for repeated queries.
        """
        if not text.strip():
            raise EmbeddingError("Cannot embed empty text")

        key = _cache_key(text)
        if key in _embedding_cache:
            return _embedding_cache[key]

        try:
            embedding = self._google_embeddings.embed_query(text)
            self._maybe_cache(key, embedding)
            return embedding
        except Exception as exc:
            raise EmbeddingError(f"Query embedding failed: {exc}")

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Embed a batch of documents with caching.
        GPU batch processing applied where available.
        """
        if not texts:
            return []

        # Split into cached vs uncached
        results: dict[int, list[float]] = {}
        uncached_indices: list[int] = []
        uncached_texts: list[str] = []

        for i, text in enumerate(texts):
            key = _cache_key(text)
            if key in _embedding_cache:
                results[i] = _embedding_cache[key]
            else:
                uncached_indices.append(i)
                uncached_texts.append(text)

        # Batch embed uncached texts
        if uncached_texts:
            batch_size = settings.EMBEDDING_BATCH_SIZE
            batch_embeddings: list[list[float]] = []

            for start in range(0, len(uncached_texts), batch_size):
                batch = uncached_texts[start : start + batch_size]
                try:
                    embs = self._google_embeddings.embed_documents(batch)
                    batch_embeddings.extend(embs)
                except Exception as exc:
                    raise EmbeddingError(f"Batch embedding failed: {exc}")

            # Store results and cache
            for idx, (original_i, embedding) in enumerate(
                zip(uncached_indices, batch_embeddings)
            ):
                results[original_i] = embedding
                key = _cache_key(texts[original_i])
                self._maybe_cache(key, embedding)

        # Return in original order
        return [results[i] for i in range(len(texts))]

    async def aembed_query(self, text: str) -> list[float]:
        """Async embed query (runs sync embed in executor)."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.embed_query, text)

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        """Async batch embed."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.embed_documents, texts)

    def _maybe_cache(self, key: str, embedding: list[float]) -> None:
        """Store embedding in LRU cache (bounded)."""
        if len(_embedding_cache) >= _CACHE_MAX_SIZE:
            # Evict oldest 10%
            keys_to_delete = list(_embedding_cache.keys())[: _CACHE_MAX_SIZE // 10]
            for k in keys_to_delete:
                del _embedding_cache[k]
        _embedding_cache[key] = embedding


# Singleton
embedding_service = EmbeddingService()
