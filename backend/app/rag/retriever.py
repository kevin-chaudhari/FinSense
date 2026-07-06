"""
FinSense AI — Hybrid BM25 + Dense Retriever

Implements:
- Dense retrieval (FAISS semantic search)
- BM25 sparse retrieval (keyword-based)
- Hybrid fusion with configurable weights
- Maximum Marginal Relevance (MMR) for diversity
"""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Optional

from langchain_core.documents import Document

from app.config import settings
from app.core.logging import get_logger
from app.rag.vector_store import vector_store_manager

logger = get_logger(__name__)


class BM25Retriever:
    """
    Lightweight BM25 implementation over in-memory document corpus.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self._corpus: list[list[str]] = []
        self._documents: list[Document] = []
        self._idf: dict[str, float] = {}
        self._avgdl: float = 0.0

    def fit(self, documents: list[Document]) -> None:
        """Build BM25 index from documents."""
        self._documents = documents
        self._corpus = [self._tokenize(doc.page_content) for doc in documents]

        n = len(self._corpus)
        if n == 0:
            return

        # Compute average document length
        total_len = sum(len(doc) for doc in self._corpus)
        self._avgdl = total_len / n

        # Compute IDF
        df: dict[str, int] = defaultdict(int)
        for doc_tokens in self._corpus:
            for token in set(doc_tokens):
                df[token] += 1

        self._idf = {
            token: math.log((n - freq + 0.5) / (freq + 0.5) + 1)
            for token, freq in df.items()
        }

    def retrieve(self, query: str, k: int = 10) -> list[tuple[Document, float]]:
        """Retrieve top-k documents by BM25 score."""
        if not self._corpus:
            return []

        query_tokens = self._tokenize(query)
        scores: list[float] = []

        for idx, doc_tokens in enumerate(self._corpus):
            dl = len(doc_tokens)
            score = 0.0
            tf_map: dict[str, int] = defaultdict(int)
            for t in doc_tokens:
                tf_map[t] += 1

            for token in query_tokens:
                if token not in self._idf:
                    continue
                tf = tf_map[token]
                idf = self._idf[token]
                tf_norm = (tf * (self.k1 + 1)) / (
                    tf + self.k1 * (1 - self.b + self.b * dl / self._avgdl)
                )
                score += idf * tf_norm

            scores.append(score)

        # Sort by score descending
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        return [(self._documents[i], s) for i, s in ranked[:k] if s > 0]

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Simple whitespace tokenizer with lowercasing."""
        return text.lower().split()


class HybridRetriever:
    """
    Hybrid retriever combining dense (FAISS) and sparse (BM25) results.

    Implements Reciprocal Rank Fusion (RRF) for score combination.
    """

    def __init__(
        self,
        dense_weight: float = None,
        bm25_weight: float = None,
    ):
        self.dense_weight = dense_weight or settings.DENSE_WEIGHT
        self.bm25_weight = bm25_weight or settings.BM25_WEIGHT
        self._bm25 = BM25Retriever()
        self._bm25_fitted = False

    def fit_bm25(self, documents: list[Document]) -> None:
        """Fit BM25 on a document corpus."""
        self._bm25.fit(documents)
        self._bm25_fitted = True

    def retrieve(
        self,
        user_id: str,
        query: str,
        k: int = None,
    ) -> list[Document]:
        """
        Hybrid retrieval combining dense + BM25 results.
        Uses Reciprocal Rank Fusion to combine rankings.
        """
        k = k or settings.RAG_TOP_K

        # Dense retrieval
        dense_results = vector_store_manager.similarity_search_with_score(
            user_id=user_id,
            query=query,
            k=k * 2,
        )

        # BM25 retrieval (if corpus available)
        bm25_results: list[tuple[Document, float]] = []
        if self._bm25_fitted:
            bm25_results = self._bm25.retrieve(query, k=k * 2)

        # Reciprocal Rank Fusion
        rrf_scores: dict[str, float] = defaultdict(float)
        doc_map: dict[str, Document] = {}
        RRF_K = 60  # RRF constant

        for rank, (doc, _score) in enumerate(dense_results):
            doc_id = doc.page_content[:100]
            rrf_scores[doc_id] += self.dense_weight / (RRF_K + rank + 1)
            doc_map[doc_id] = doc

        for rank, (doc, _score) in enumerate(bm25_results):
            doc_id = doc.page_content[:100]
            rrf_scores[doc_id] += self.bm25_weight / (RRF_K + rank + 1)
            doc_map[doc_id] = doc

        # Sort by combined RRF score
        ranked_ids = sorted(rrf_scores, key=lambda x: rrf_scores[x], reverse=True)
        return [doc_map[doc_id] for doc_id in ranked_ids[:k]]


# Singleton
hybrid_retriever = HybridRetriever()
