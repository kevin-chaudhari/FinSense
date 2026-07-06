"""
FinSense AI — Intent Classification Node

Classifies user query into:
  - "personal_budgeting"  → questions about user's own financial data
  - "financial_education" → general financial knowledge questions
  - "general"             → catch-all

Uses Gemini with structured output for reliable classification.
"""

from __future__ import annotations

import re

import google.generativeai as genai

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

genai.configure(api_key=settings.google_api_key)

_CLASSIFIER_PROMPT = """You are a financial query classifier. Classify the following question into exactly ONE category:

Categories:
- "personal_budgeting": Questions about the user's own spending, transactions, budget, expenses, savings, or financial history
- "financial_education": General questions about financial concepts, investment strategies, market information, or educational finance topics

Rules:
- Return ONLY the category name, nothing else
- If unsure, default to "financial_education"

Question: {question}

Category:"""


async def classify_intent(state: dict) -> dict:
    """
    LangGraph node: classify user intent.
    Updates state with 'intent' field.
    """
    query = state.get("query", "")

    if not query.strip():
        return {**state, "intent": "general"}

    try:
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        prompt = _CLASSIFIER_PROMPT.format(question=query)
        response = model.generate_content(prompt)

        if response and response.text:
            raw = response.text.strip().lower()
            # Normalize
            if "personal" in raw or "budget" in raw:
                intent = "personal_budgeting"
            elif "education" in raw or "general" in raw:
                intent = "financial_education"
            else:
                intent = "financial_education"
        else:
            intent = "financial_education"

        logger.debug("Classified query as '%s': %s", intent, query[:60])
        return {**state, "intent": intent}

    except Exception as exc:
        logger.warning("Classification failed: %s — defaulting to financial_education", exc)
        return {**state, "intent": "financial_education"}
