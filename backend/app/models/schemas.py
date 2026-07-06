"""
FinSense AI — Pydantic Schemas

Request/response models with full validation.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field, field_validator


# ── Auth Schemas ───────────────────────────────────────────────────────────────

class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    password: str = Field(..., min_length=8, max_length=128)
    display_name: Optional[str] = Field(None, max_length=100)


class UserLoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    user_id: str
    username: str
    display_name: Optional[str] = None
    created_at: datetime
    transaction_count: int = 0


# ── Transaction Schemas ────────────────────────────────────────────────────────

TRANSACTION_CATEGORIES = [
    "Food & Dining",
    "Transportation",
    "Entertainment",
    "Shopping",
    "Utilities",
    "Healthcare",
    "Education",
    "Travel",
    "Housing",
    "Income",
    "Investment",
    "Other",
]

class TransactionCreateRequest(BaseModel):
    amount: float = Field(..., gt=0, le=1_000_000)
    transaction_type: Literal["credit", "debit"]
    category: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    date: datetime

    @field_validator("amount")
    @classmethod
    def round_amount(cls, v: float) -> float:
        return round(v, 2)

    @field_validator("description")
    @classmethod
    def sanitize_description(cls, v: str) -> str:
        # Strip dangerous characters
        return v.strip()[:500]

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if v not in TRANSACTION_CATEGORIES:
            raise ValueError(f"Category must be one of: {TRANSACTION_CATEGORIES}")
        return v


class TransactionResponse(BaseModel):
    id: str
    amount: float
    transaction_type: str
    category: str
    description: str
    date: datetime
    created_at: datetime
    user_id: str


class TransactionListResponse(BaseModel):
    transactions: list[TransactionResponse]
    total: int
    page: int
    page_size: int


# ── Agent Schemas ──────────────────────────────────────────────────────────────

class AgentQueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None
    stream: bool = False

    @field_validator("question")
    @classmethod
    def sanitize_question(cls, v: str) -> str:
        return v.strip()


class AgentQueryResponse(BaseModel):
    response: str
    intent: Optional[str] = None
    conversation_id: Optional[str] = None
    sources: list[str] = Field(default_factory=list)
    execution_time_ms: Optional[float] = None
    gpu_accelerated: bool = False


class ConversationMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ── Health Schemas ─────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    gpu: dict


class GPUHealthResponse(BaseModel):
    cuda_available: bool
    device_name: Optional[str] = None
    vram_gb: float = 0.0
    faiss_gpu: bool = False
    mixed_precision: bool = False
