"""
FinSense AI — Transaction Routes

POST   /api/v1/transactions          — Add transaction
GET    /api/v1/transactions          — List transactions (paginated)
GET    /api/v1/transactions/summary  — Spending summary for analytics
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.core.logging import get_logger
from app.core.security import get_current_user_id
from app.models.schemas import (
    TransactionCreateRequest,
    TransactionListResponse,
    TransactionResponse,
)
from app.models.transaction import Transaction
from app.rag.vector_store import vector_store_manager
from app.repositories.transaction_repo import transaction_repository

logger = get_logger(__name__)
router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post(
    "",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new transaction",
)
async def create_transaction(
    body: TransactionCreateRequest,
    user_id: str = Depends(get_current_user_id),
) -> TransactionResponse:
    """
    Add a financial transaction for the authenticated user.

    - Persists to JSON store (safe, no eval())
    - Indexes in FAISS vector store for semantic search
    """
    transaction = Transaction(
        user_id=user_id,
        amount=body.amount,
        transaction_type=body.transaction_type,
        category=body.category,
        description=body.description,
        date=body.date,
    )

    # Persist to repository
    saved = transaction_repository.create(user_id, transaction)

    # Index in vector store for RAG
    try:
        embedding_text = transaction.to_embedding_text()
        vector_store_manager.add_texts(
            user_id=user_id,
            texts=[embedding_text],
            metadatas=[{
                "transaction_id": transaction.id,
                "category": transaction.category,
                "amount": transaction.amount,
                "type": transaction.transaction_type,
                "date": transaction.date.isoformat(),
            }],
        )
        logger.debug("Indexed transaction %s in vector store", transaction.id)
    except Exception as exc:
        # Non-fatal: transaction saved, just not indexed
        logger.warning("Vector store indexing failed (non-fatal): %s", exc)

    logger.info(
        "Transaction created: user=%s, type=%s, amount=%.2f, cat=%s",
        user_id, body.transaction_type, body.amount, body.category,
    )

    return TransactionResponse(
        id=saved.id,
        amount=saved.amount,
        transaction_type=saved.transaction_type,
        category=saved.category,
        description=saved.description,
        date=saved.date,
        created_at=saved.created_at,
        user_id=user_id,
    )


@router.get(
    "",
    response_model=TransactionListResponse,
    summary="List transactions with pagination",
)
async def list_transactions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    category: Optional[str] = Query(default=None),
    transaction_type: Optional[str] = Query(default=None, pattern="^(credit|debit)$"),
    user_id: str = Depends(get_current_user_id),
) -> TransactionListResponse:
    """List paginated transactions for the authenticated user."""
    transactions, total = transaction_repository.list_all(
        user_id=user_id,
        page=page,
        page_size=page_size,
        category=category,
        transaction_type=transaction_type,
    )

    return TransactionListResponse(
        transactions=[
            TransactionResponse(
                id=t.id,
                amount=t.amount,
                transaction_type=t.transaction_type,
                category=t.category,
                description=t.description,
                date=t.date,
                created_at=t.created_at,
                user_id=user_id,
            )
            for t in transactions
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/summary",
    summary="Get spending summary for analytics",
)
async def get_summary(
    user_id: str = Depends(get_current_user_id),
) -> dict:
    """
    Return aggregated spending summary for dashboard charts.

    Includes:
    - Total credits / debits / net
    - Category breakdown
    - Monthly trend (last 6 months)
    - Transaction count
    """
    raw = transaction_repository.get_all_raw(user_id)

    if not raw:
        return {
            "total_credit": 0.0,
            "total_debit": 0.0,
            "net": 0.0,
            "transaction_count": 0,
            "categories": {},
            "monthly_trend": {},
        }

    total_credit = sum(float(t["amount"]) for t in raw if t.get("transaction_type") == "credit")
    total_debit = sum(float(t["amount"]) for t in raw if t.get("transaction_type") == "debit")

    # Category breakdown
    categories: dict[str, dict] = {}
    for t in raw:
        cat = t.get("category", "Other")
        if cat not in categories:
            categories[cat] = {"credit": 0.0, "debit": 0.0, "count": 0}
        tx_type = t.get("transaction_type", "debit")
        categories[cat][tx_type] += float(t.get("amount", 0))
        categories[cat]["count"] += 1

    # Monthly trend
    monthly: dict[str, dict] = {}
    for t in raw:
        try:
            date_str = t.get("date", "")
            if date_str:
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                month_key = dt.strftime("%Y-%m")
                if month_key not in monthly:
                    monthly[month_key] = {"credit": 0.0, "debit": 0.0}
                tx_type = t.get("transaction_type", "debit")
                monthly[month_key][tx_type] += float(t.get("amount", 0))
        except Exception:
            continue

    # Sort monthly by date
    sorted_monthly = dict(sorted(monthly.items())[-6:])

    return {
        "total_credit": round(total_credit, 2),
        "total_debit": round(total_debit, 2),
        "net": round(total_credit - total_debit, 2),
        "transaction_count": len(raw),
        "categories": categories,
        "monthly_trend": sorted_monthly,
    }
