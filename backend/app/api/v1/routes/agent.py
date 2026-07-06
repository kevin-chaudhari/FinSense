"""
FinSense AI — Agent Routes

POST /api/v1/agent/query  — Execute LangGraph agent (JSON or SSE streaming)
"""

from __future__ import annotations

import json
import time
from typing import AsyncIterator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.agents.graph import run_agent
from app.config import settings
from app.core.logging import get_logger
from app.core.security import get_current_user_id, sanitize_user_input
from app.models.schemas import AgentQueryRequest, AgentQueryResponse

logger = get_logger(__name__)
router = APIRouter(prefix="/agent", tags=["AI Agent"])


@router.post(
    "/query",
    summary="Query the FinSense AI agent",
    description=(
        "Submit a natural language financial question to the LangGraph agent. "
        "Supports optional SSE streaming (`stream: true`)."
    ),
)
async def agent_query(
    body: AgentQueryRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Execute the LangGraph agent pipeline.

    The agent:
    1. Classifies the intent (personal budgeting vs financial education)
    2. Routes to the appropriate node
    3. Retrieves relevant context via hybrid RAG (for budgeting queries)
    4. Generates a grounded response with Gemini
    5. Synthesizes and returns the final answer

    Set `stream: true` for Server-Sent Events (SSE) streaming response.
    """
    # Sanitize input
    clean_question = sanitize_user_input(body.question)
    if not clean_question:
        return AgentQueryResponse(
            response="Please provide a valid question.",
            gpu_accelerated=False,
        )

    if body.stream:
        return StreamingResponse(
            _stream_agent_response(user_id, clean_question, body.conversation_id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    # Non-streaming
    result = await run_agent(
        user_id=user_id,
        question=clean_question,
        conversation_id=body.conversation_id,
    )

    return AgentQueryResponse(
        response=result["response"],
        intent=result.get("intent"),
        conversation_id=result.get("conversation_id"),
        sources=result.get("sources", []),
        execution_time_ms=result.get("execution_time_ms"),
        gpu_accelerated=result.get("gpu_accelerated", False),
    )


async def _stream_agent_response(
    user_id: str,
    question: str,
    conversation_id: str | None,
) -> AsyncIterator[str]:
    """
    SSE stream generator.

    Sends events:
    - data: {"type": "start"}
    - data: {"type": "token", "content": "..."}
    - data: {"type": "done", "intent": "...", "execution_time_ms": ...}
    - data: {"type": "error", "message": "..."}
    """
    try:
        yield f"data: {json.dumps({'type': 'start'})}\n\n"

        start = time.perf_counter()

        # Run the agent (full response for now — true token streaming
        # requires Gemini streaming API integration)
        result = await run_agent(
            user_id=user_id,
            question=question,
            conversation_id=conversation_id,
        )

        response_text = result["response"]
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Simulate word-by-word streaming for better UX
        words = response_text.split(" ")
        for i, word in enumerate(words):
            chunk = word + (" " if i < len(words) - 1 else "")
            yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"

        yield f"data: {json.dumps({'type': 'done', 'intent': result.get('intent'), 'conversation_id': result.get('conversation_id'), 'execution_time_ms': round(elapsed_ms, 1), 'gpu_accelerated': result.get('gpu_accelerated', False)})}\n\n"

    except Exception as exc:
        logger.exception("SSE streaming error: %s", exc)
        yield f"data: {json.dumps({'type': 'error', 'message': str(exc)})}\n\n"
