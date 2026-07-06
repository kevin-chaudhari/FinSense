"""
FinSense AI — Financial Education Node

Handles general financial education queries without
requiring user-specific data. Uses Gemini with a
comprehensive financial expert system prompt.
"""

from __future__ import annotations

import google.generativeai as genai

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

genai.configure(api_key=settings.google_api_key)

_EDUCATION_SYSTEM = """You are FinSense, a world-class financial education AI with expertise in:
- Personal finance fundamentals
- Investment strategies (stocks, bonds, ETFs, real estate)
- Budgeting methodologies (50/30/20, zero-based, envelope)
- Debt management and elimination strategies
- Tax optimization strategies
- Retirement planning (401k, IRA, Roth)
- Emergency fund principles
- Credit score optimization
- Financial independence / FIRE movement
- Cryptocurrency and digital assets (with risk warnings)
- Insurance and risk management
- Global markets and macroeconomics

Communication style:
- Clear, jargon-free explanations with definitions for technical terms
- Practical, actionable advice
- Include relevant examples and numbers
- Mention risks alongside opportunities
- Cite general best practices (not specific investment advice)
- Encourage consultation with certified financial advisors for major decisions"""

_EDUCATION_PROMPT = """CONVERSATION HISTORY:
{history}

USER QUESTION: {question}

Please provide a comprehensive, educational response:"""


async def financial_education_node(state: dict) -> dict:
    """
    LangGraph node: answer general financial education queries.
    """
    query = state.get("query", "")
    messages = state.get("messages", [])

    # Build conversation history context
    history_text = ""
    for msg in messages[-6:]:
        role = "User" if "Human" in type(msg).__name__ else "Assistant"
        history_text += f"{role}: {msg.content}\n"

    try:
        model = genai.GenerativeModel(
            settings.GEMINI_MODEL,
            system_instruction=_EDUCATION_SYSTEM,
            generation_config=genai.GenerationConfig(
                max_output_tokens=settings.GEMINI_MAX_OUTPUT_TOKENS,
                temperature=0.5,  # More deterministic for educational content
            ),
        )
        prompt = _EDUCATION_PROMPT.format(
            history=history_text or "No prior conversation.",
            question=query,
        )
        response = model.generate_content(prompt)
        answer = response.text if response and response.text else "I couldn't generate a response."

    except Exception as exc:
        logger.error("Education LLM call failed: %s", exc)
        answer = "I encountered an error. Please try again."

    return {
        **state,
        "sources": ["Financial education knowledge base"],
        "final_response": answer,
    }
