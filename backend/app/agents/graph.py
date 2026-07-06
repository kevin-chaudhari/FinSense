"""
FinSense AI — LangGraph Multi-Agent StateGraph

Implements a proper LangGraph workflow replacing the deprecated
initialize_agent(AgentType.ZERO_SHOT_REACT_DESCRIPTION) pattern.

Agent Flow:
  User Query
     │
     ▼
  [classify] ──► intent: "personal_budgeting" ──► [budgeting_node] ──► [synthesis]
             └──► intent: "financial_education" ──► [education_node] ──► [synthesis]
             └──► intent: "general" ──────────────► [education_node] ──► [synthesis]
                                                                            │
                                                                            ▼
                                                                      Final Response
"""

from __future__ import annotations

import time
from typing import Annotated, Any, Optional, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from app.config import settings
from app.core.exceptions import AgentError
from app.core.logging import get_logger
from app.agents.nodes.classifier import classify_intent
from app.agents.nodes.budgeting import personal_budgeting_node
from app.agents.nodes.education import financial_education_node
from app.agents.nodes.synthesis import synthesis_node
from app.agents.memory import ConversationMemory

logger = get_logger(__name__)


# ── State Definition ───────────────────────────────────────────────────────────

class AgentState(TypedDict):
    """Typed state flowing through the LangGraph."""
    # Message history (reducer: appends messages)
    messages: Annotated[list[BaseMessage], add_messages]
    # The current user query
    query: str
    # Classified intent
    intent: Optional[str]
    # User context (RAG-retrieved data)
    context: Optional[str]
    # Sources used
    sources: list[str]
    # User ID for per-user data retrieval
    user_id: str
    # Final synthesized response
    final_response: Optional[str]
    # Error message (if any node fails)
    error: Optional[str]
    # GPU acceleration used?
    gpu_accelerated: bool


# ── Router ─────────────────────────────────────────────────────────────────────

def route_by_intent(state: AgentState) -> str:
    """Route to appropriate node based on classified intent."""
    intent = state.get("intent", "general")
    if intent == "personal_budgeting":
        return "budgeting_node"
    elif intent == "financial_education":
        return "education_node"
    else:
        return "education_node"


# ── Graph Builder ──────────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    """Construct and compile the LangGraph StateGraph."""
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("classify", classify_intent)
    graph.add_node("budgeting_node", personal_budgeting_node)
    graph.add_node("education_node", financial_education_node)
    graph.add_node("synthesis", synthesis_node)

    # Edges
    graph.add_edge(START, "classify")

    graph.add_conditional_edges(
        "classify",
        route_by_intent,
        {
            "budgeting_node": "budgeting_node",
            "education_node": "education_node",
        },
    )

    graph.add_edge("budgeting_node", "synthesis")
    graph.add_edge("education_node", "synthesis")
    graph.add_edge("synthesis", END)

    return graph.compile()


# Compile graph at module load (warm it up)
_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
        logger.info("LangGraph StateGraph compiled and ready")
    return _graph


# ── Public API ─────────────────────────────────────────────────────────────────

async def run_agent(
    user_id: str,
    question: str,
    conversation_id: Optional[str] = None,
) -> dict[str, Any]:
    """
    Execute the LangGraph agent pipeline.

    Returns:
        {
            "response": str,
            "intent": str,
            "sources": list[str],
            "execution_time_ms": float,
            "gpu_accelerated": bool,
        }
    """
    start = time.perf_counter()

    # Load conversation history
    memory = ConversationMemory(conversation_id=conversation_id)
    history = memory.get_history()

    # Build initial state
    initial_state: AgentState = {
        "messages": history + [HumanMessage(content=question)],
        "query": question,
        "intent": None,
        "context": None,
        "sources": [],
        "user_id": user_id,
        "final_response": None,
        "error": None,
        "gpu_accelerated": False,
    }

    try:
        graph = get_graph()
        final_state = await graph.ainvoke(initial_state)

        response = final_state.get("final_response") or "I'm unable to generate a response."
        intent = final_state.get("intent", "general")
        sources = final_state.get("sources", [])
        gpu_used = final_state.get("gpu_accelerated", False)

        # Save to conversation memory
        memory.add_turn(question=question, answer=response)

        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "Agent completed [user=%s, intent=%s, %.1fms, gpu=%s]",
            user_id,
            intent,
            elapsed_ms,
            gpu_used,
        )

        return {
            "response": response,
            "intent": intent,
            "sources": sources,
            "execution_time_ms": round(elapsed_ms, 1),
            "conversation_id": memory.conversation_id,
            "gpu_accelerated": gpu_used,
        }

    except Exception as exc:
        logger.exception("Agent execution failed for user '%s': %s", user_id, exc)
        raise AgentError(f"Agent failed to process your request: {exc}")
