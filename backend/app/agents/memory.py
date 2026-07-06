"""
FinSense AI — Conversation Memory Manager

Persists conversation history to disk per user per conversation.
Replaces the per-request ConversationBufferMemory that had no persistence.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_MEMORY_DIR = Path("data/conversations")


class ConversationMemory:
    """
    Persistent, per-conversation memory backed by JSON files.

    Each conversation is stored at:
        data/conversations/<conversation_id>.json
    """

    def __init__(self, conversation_id: Optional[str] = None):
        self.conversation_id = conversation_id or str(uuid.uuid4())
        _MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        self._path = _MEMORY_DIR / f"{self.conversation_id}.json"

    def get_history(self) -> list[BaseMessage]:
        """Load conversation history as LangChain messages."""
        if not self._path.exists():
            return []
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                data = json.load(f)
            messages: list[BaseMessage] = []
            for item in data:
                if item["role"] == "user":
                    messages.append(HumanMessage(content=item["content"]))
                elif item["role"] == "assistant":
                    messages.append(AIMessage(content=item["content"]))
            # Limit to last N turns
            limit = settings.CONVERSATION_HISTORY_LIMIT * 2  # pairs
            return messages[-limit:]
        except Exception as exc:
            logger.warning("Failed to load conversation history: %s", exc)
            return []

    def add_turn(self, question: str, answer: str) -> None:
        """Append a Q&A turn to the conversation."""
        history = self._load_raw()
        history.append({
            "role": "user",
            "content": question,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        history.append({
            "role": "assistant",
            "content": answer,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        # Trim to limit
        max_items = settings.CONVERSATION_HISTORY_LIMIT * 2
        if len(history) > max_items:
            history = history[-max_items:]

        self._save_raw(history)

    def clear(self) -> None:
        """Clear the conversation history."""
        if self._path.exists():
            self._path.unlink()

    def _load_raw(self) -> list[dict]:
        if not self._path.exists():
            return []
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save_raw(self, history: list[dict]) -> None:
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2)
        except Exception as exc:
            logger.warning("Failed to save conversation: %s", exc)
