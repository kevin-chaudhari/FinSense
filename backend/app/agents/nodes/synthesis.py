"""
FinSense AI — Synthesis Node (pass-through)

The synthesis node finalizes the response.
Currently a pass-through that could be extended
to add confidence scoring, hallucination checks,
or response formatting.
"""

from __future__ import annotations

from app.core.logging import get_logger

logger = get_logger(__name__)


async def synthesis_node(state: dict) -> dict:
    """
    LangGraph node: finalize and validate the agent response.

    Currently validates that a final_response exists and
    performs basic quality checks.
    """
    response = state.get("final_response", "")

    if not response or not response.strip():
        response = (
            "I'm unable to generate a complete response right now. "
            "Please try rephrasing your question."
        )
        logger.warning("Synthesis: empty response detected, substituting fallback")

    # Basic response quality — truncate if excessively long
    if len(response) > 4000:
        response = response[:4000] + "\n\n*(Response truncated for readability)*"

    return {**state, "final_response": response.strip()}
