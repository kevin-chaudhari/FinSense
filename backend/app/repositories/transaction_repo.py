"""
FinSense AI — Transaction Repository

JSON-file-based repository (replaces flat eval() text files).
Each user's transactions stored in: data/users/<user_id>/transactions.json

Production upgrade path: swap for SQLAlchemy + PostgreSQL without changing service layer.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Optional

from app.config import settings
from app.core.exceptions import StorageError
from app.core.logging import get_logger
from app.models.transaction import Transaction

logger = get_logger(__name__)

_write_locks: dict[str, Lock] = {}


def _get_lock(user_id: str) -> Lock:
    if user_id not in _write_locks:
        _write_locks[user_id] = Lock()
    return _write_locks[user_id]


class TransactionRepository:
    """Per-user JSON-backed transaction store."""

    def __init__(self):
        self._base = settings.USER_DATA_DIR

    def _path(self, user_id: str) -> Path:
        safe_id = "".join(c for c in user_id if c.isalnum() or c in "-_")
        p = self._base / safe_id / "transactions.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def _read_all(self, user_id: str) -> list[dict]:
        path = self._path(user_id)
        if not path.exists():
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Failed to read transactions for '%s': %s", user_id, exc)
            return []

    def _write_all(self, user_id: str, transactions: list[dict]) -> None:
        path = self._path(user_id)
        tmp_path = path.with_suffix(".tmp")
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(transactions, f, default=str, indent=2)
            tmp_path.replace(path)  # Atomic replace
        except OSError as exc:
            raise StorageError(f"Failed to save transactions: {exc}")

    def create(self, user_id: str, transaction: Transaction) -> Transaction:
        """Persist a new transaction."""
        with _get_lock(user_id):
            transactions = self._read_all(user_id)
            transactions.append(transaction.to_dict())
            self._write_all(user_id, transactions)
        logger.debug("Created transaction %s for user '%s'", transaction.id, user_id)
        return transaction

    def list_all(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 50,
        category: Optional[str] = None,
        transaction_type: Optional[str] = None,
    ) -> tuple[list[Transaction], int]:
        """List paginated transactions for a user."""
        raw = self._read_all(user_id)

        # Filter
        if category:
            raw = [t for t in raw if t.get("category") == category]
        if transaction_type:
            raw = [t for t in raw if t.get("transaction_type") == transaction_type]

        total = len(raw)

        # Sort by date descending
        raw.sort(key=lambda t: t.get("date", ""), reverse=True)

        # Paginate
        start = (page - 1) * page_size
        page_data = raw[start : start + page_size]

        transactions = []
        for t in page_data:
            try:
                transactions.append(Transaction.from_dict(t))
            except Exception as exc:
                logger.warning("Skipping malformed transaction: %s", exc)

        return transactions, total

    def get_all_raw(self, user_id: str) -> list[dict]:
        """Return all raw transaction dicts (for analytics)."""
        return self._read_all(user_id)

    def count(self, user_id: str) -> int:
        return len(self._read_all(user_id))


# Singleton
transaction_repository = TransactionRepository()
