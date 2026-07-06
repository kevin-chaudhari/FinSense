"""
FinSense AI — Transaction Domain Model
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional


class Transaction:
    """Immutable transaction domain object."""

    __slots__ = (
        "id",
        "user_id",
        "amount",
        "transaction_type",
        "category",
        "description",
        "date",
        "created_at",
    )

    def __init__(
        self,
        user_id: str,
        amount: float,
        transaction_type: str,
        category: str,
        description: str,
        date: datetime,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.amount = round(amount, 2)
        self.transaction_type = transaction_type
        self.category = category
        self.description = description
        self.date = date
        self.created_at = created_at or datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "amount": self.amount,
            "transaction_type": self.transaction_type,
            "category": self.category,
            "description": self.description,
            "date": self.date.isoformat(),
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        return cls(
            id=data.get("id") or str(uuid.uuid4()),
            user_id=data.get("user_id", ""),
            amount=float(data["amount"]),
            transaction_type=data["transaction_type"],
            category=data["category"],
            description=data["description"],
            date=_parse_dt(data["date"]),
            created_at=_parse_dt(data.get("created_at")) if data.get("created_at") else None,
        )

    def to_embedding_text(self) -> str:
        """Formatted text for embedding / RAG ingestion."""
        return (
            f"Transaction: ${self.amount:.2f} {self.transaction_type} | "
            f"Category: {self.category} | "
            f"Description: {self.description} | "
            f"Date: {self.date.strftime('%Y-%m-%d')}"
        )


def _parse_dt(value) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return datetime.now(timezone.utc)
    return datetime.now(timezone.utc)
