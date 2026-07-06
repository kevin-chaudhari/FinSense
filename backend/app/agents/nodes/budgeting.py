"""
FinSense AI — Personal Budgeting Node

Handles queries about the user's own financial data.
Uses RAG (hybrid retrieval) to ground responses in actual transaction data.
"""

from __future__ import annotations

import json

import google.generativeai as genai
from langchain_core.documents import Document

from app.config import settings
from app.core.logging import get_logger
from app.gpu.detector import gpu_detector
from app.rag.retriever import hybrid_retriever
from app.rag.vector_store import vector_store_manager
from app.repositories.transaction_repo import transaction_repository

logger = get_logger(__name__)

genai.configure(api_key=settings.google_api_key)

_BUDGETING_PROMPT = """You are FinSense, an expert personal finance AI assistant.

USER'S FINANCIAL DATA:
{context}

CONVERSATION HISTORY:
{history}

USER QUESTION: {question}

Instructions:
- Answer using the user's actual financial data provided above
- Be specific with amounts and dates when relevant
- Identify spending patterns, anomalies, or savings opportunities
- If data is insufficient, say so clearly
- Format monetary values with $ and 2 decimal places
- Be encouraging but honest about financial health

Answer:"""


async def personal_budgeting_node(state: dict) -> dict:
    """
    LangGraph node: answer personal budgeting queries.

    Retrieves user-specific financial context via hybrid RAG,
    then generates a grounded response.
    """
    user_id = state.get("user_id", "")
    query = state.get("query", "")
    messages = state.get("messages", [])

    # Check GPU
    gpu_info = gpu_detector.detect()
    gpu_used = gpu_info.cuda_available

    # ── RAG: Retrieve relevant transactions ───────────────────────────────────
    sources: list[str] = []
    context_parts: list[str] = []

    try:
        # Get all transactions for comprehensive context
        transactions, total = transaction_repository.list_all(user_id, page=1, page_size=200)

        if transactions:
            # Build a structured summary for the LLM
            total_credit = sum(t.amount for t in transactions if t.transaction_type == "credit")
            total_debit = sum(t.amount for t in transactions if t.transaction_type == "debit")
            net = total_credit - total_debit

            # Category breakdown
            category_totals: dict[str, float] = {}
            for t in transactions:
                category_totals[t.category] = category_totals.get(t.category, 0) + t.amount

            summary_lines = [
                f"Total Transactions: {total}",
                f"Total Income (credits): ${total_credit:.2f}",
                f"Total Expenses (debits): ${total_debit:.2f}",
                f"Net Balance: ${net:.2f}",
                "",
                "Category Breakdown:",
            ]
            for cat, amt in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
                summary_lines.append(f"  - {cat}: ${amt:.2f}")

            summary_lines.append("")
            summary_lines.append("Recent Transactions (last 10):")
            for t in transactions[:10]:
                summary_lines.append(
                    f"  - {t.date.strftime('%Y-%m-%d')} | {t.transaction_type.upper()} "
                    f"${t.amount:.2f} | {t.category} | {t.description}"
                )
            context_parts.append("\n".join(summary_lines))
            sources.append(f"{total} transactions retrieved")

        # Semantic search for specific relevant transactions
        relevant_docs = vector_store_manager.similarity_search(user_id, query, k=5)
        if relevant_docs:
            context_parts.append("\nMost Relevant Transactions:")
            for doc in relevant_docs:
                context_parts.append(f"  {doc.page_content}")
                sources.append(doc.page_content[:80])

    except Exception as exc:
        logger.warning("RAG retrieval failed: %s", exc)
        context_parts.append("No transaction data available.")

    context = "\n".join(context_parts) if context_parts else "No financial data found for this user."

    # ── Conversation history ──────────────────────────────────────────────────
    history_text = ""
    for msg in messages[-6:]:  # Last 3 turns
        role = "User" if hasattr(msg, "content") and "Human" in type(msg).__name__ else "Assistant"
        history_text += f"{role}: {msg.content}\n"

    # ── Generate response ─────────────────────────────────────────────────────
    try:
        model = genai.GenerativeModel(
            settings.GEMINI_MODEL,
            generation_config=genai.GenerationConfig(
                max_output_tokens=settings.GEMINI_MAX_OUTPUT_TOKENS,
                temperature=settings.GEMINI_TEMPERATURE,
            ),
        )
        prompt = _BUDGETING_PROMPT.format(
            context=context,
            history=history_text or "No prior conversation.",
            question=query,
        )
        response = model.generate_content(prompt)
        answer = response.text if response and response.text else "I couldn't generate a response."
    except Exception as exc:
        logger.error("Budgeting LLM call failed: %s", exc)
        answer = f"I encountered an error analyzing your budget. Please try again."

    return {
        **state,
        "context": context,
        "sources": sources,
        "final_response": answer,
        "gpu_accelerated": gpu_used,
    }
