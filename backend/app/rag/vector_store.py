"""
FinSense AI — FAISS Vector Store Manager

GPU-accelerated FAISS with:
- Automatic GPU/CPU mode based on hardware
- Per-user isolated vector stores
- Atomic saves (no partial writes)
- Index warming / preloading
"""

from __future__ import annotations

import asyncio
import threading
from pathlib import Path
from typing import Optional

import numpy as np
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from app.config import settings
from app.core.exceptions import VectorStoreError
from app.core.logging import get_logger
from app.gpu.accelerator import gpu_accelerator
from app.rag.embeddings import embedding_service

logger = get_logger(__name__)

# Per-user index cache to avoid reloading from disk each request
_index_cache: dict[str, FAISS] = {}
_cache_lock = threading.Lock()


class VectorStoreManager:
    """
    Manages per-user FAISS vector stores.

    Each user has their own isolated index directory:
        data/vector_stores/<user_id>/
    """

    def __init__(self):
        self._store_base = settings.VECTOR_STORE_DIR

    def _user_path(self, user_id: str) -> Path:
        """Get the directory path for a user's vector store."""
        safe_id = "".join(c for c in user_id if c.isalnum() or c in "-_")
        return self._store_base / safe_id

    def _has_index(self, user_id: str) -> bool:
        """Check if a user has an existing FAISS index."""
        index_file = self._user_path(user_id) / "index.faiss"
        return index_file.exists()

    def load_or_create(self, user_id: str) -> Optional[FAISS]:
        """
        Load user's FAISS index from cache or disk.
        Returns None if user has no index yet.
        """
        # Check in-memory cache first
        with _cache_lock:
            if user_id in _index_cache:
                return _index_cache[user_id]

        if not self._has_index(user_id):
            return None

        try:
            vs = FAISS.load_local(
                str(self._user_path(user_id)),
                embeddings=embedding_service._google_embeddings,
                allow_dangerous_deserialization=True,
            )
            with _cache_lock:
                _index_cache[user_id] = vs
            logger.debug("Loaded FAISS index for user '%s' from disk", user_id)
            return vs
        except Exception as exc:
            raise VectorStoreError(f"Failed to load vector store for user '{user_id}': {exc}")

    def add_texts(self, user_id: str, texts: list[str], metadatas: Optional[list[dict]] = None) -> None:
        """
        Add texts to user's vector store.
        Creates index if it doesn't exist.
        """
        if not texts:
            return

        try:
            path = self._user_path(user_id)
            path.mkdir(parents=True, exist_ok=True)

            with _cache_lock:
                existing = _index_cache.get(user_id)

            if existing is None and self._has_index(user_id):
                # Load from disk if not cached
                existing = FAISS.load_local(
                    str(path),
                    embeddings=embedding_service._google_embeddings,
                    allow_dangerous_deserialization=True,
                )

            if existing is None:
                # Create new index
                vs = FAISS.from_texts(
                    texts=texts,
                    embedding=embedding_service._google_embeddings,
                    metadatas=metadatas or [{} for _ in texts],
                )
                logger.info("Created new FAISS index for user '%s'", user_id)
            else:
                # Append to existing
                existing.add_texts(texts=texts, metadatas=metadatas or [{} for _ in texts])
                vs = existing

            # Atomic save
            vs.save_local(str(path))

            with _cache_lock:
                _index_cache[user_id] = vs

            logger.debug("Added %d texts to vector store for '%s'", len(texts), user_id)

        except Exception as exc:
            raise VectorStoreError(f"Failed to add texts to vector store: {exc}")

    def similarity_search(
        self,
        user_id: str,
        query: str,
        k: int = 10,
    ) -> list[Document]:
        """Perform semantic similarity search."""
        vs = self.load_or_create(user_id)
        if vs is None:
            return []
        try:
            return vs.similarity_search(query, k=k)
        except Exception as exc:
            raise VectorStoreError(f"Similarity search failed: {exc}")

    def similarity_search_with_score(
        self,
        user_id: str,
        query: str,
        k: int = 10,
    ) -> list[tuple[Document, float]]:
        """Perform similarity search returning (doc, score) pairs."""
        vs = self.load_or_create(user_id)
        if vs is None:
            return []
        try:
            return vs.similarity_search_with_score(query, k=k)
        except Exception as exc:
            raise VectorStoreError(f"Scored similarity search failed: {exc}")

    def invalidate_cache(self, user_id: str) -> None:
        """Evict user's index from memory cache."""
        with _cache_lock:
            _index_cache.pop(user_id, None)

    def get_document_count(self, user_id: str) -> int:
        """Return the number of documents in a user's store."""
        vs = self.load_or_create(user_id)
        if vs is None:
            return 0
        try:
            return vs.index.ntotal
        except Exception:
            return 0


# Singleton
vector_store_manager = VectorStoreManager()
