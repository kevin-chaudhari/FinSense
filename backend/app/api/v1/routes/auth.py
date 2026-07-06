"""
FinSense AI — Authentication Routes

POST /api/v1/auth/register  — Create account
POST /api/v1/auth/login     — Obtain JWT tokens
POST /api/v1/auth/refresh   — Refresh access token
POST /api/v1/auth/logout    — Invalidate session
GET  /api/v1/auth/me        — Current user info
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.exceptions import AuthenticationError
from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user_id,
)
from app.models.schemas import (
    RefreshTokenRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.models.user import user_repository
from app.repositories.transaction_repo import transaction_repository

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(body: UserRegisterRequest) -> TokenResponse:
    """
    Create a new user account.

    - Hashes password with bcrypt
    - Returns JWT access + refresh tokens
    """
    user = user_repository.create(
        username=body.username,
        password=body.password,
        display_name=body.display_name,
    )
    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    logger.info("New user registered: '%s' (id=%s)", user.username, user.id)
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and obtain JWT tokens",
)
async def login(body: UserLoginRequest) -> TokenResponse:
    """
    Authenticate with username + password.

    Returns access token (short-lived) and refresh token (long-lived).
    """
    user = user_repository.authenticate(body.username, body.password)
    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    logger.info("User login: '%s'", user.username)
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
)
async def refresh_token(body: RefreshTokenRequest) -> TokenResponse:
    """Exchange a refresh token for a new access token."""
    payload = decode_token(body.refresh_token)
    if payload.get("type") != "refresh":
        raise AuthenticationError("Invalid refresh token type.")

    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Malformed token.")

    new_access = create_access_token(user_id)
    new_refresh = create_refresh_token(user_id)
    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user",
)
async def get_me(user_id: str = Depends(get_current_user_id)) -> UserResponse:
    """Return the currently authenticated user's profile."""
    user = user_repository.get_by_id(user_id)
    if user is None:
        raise AuthenticationError("User not found.")
    tx_count = transaction_repository.count(user_id)
    return UserResponse(
        user_id=user.id,
        username=user.username,
        display_name=user.display_name,
        created_at=user.created_at,
        transaction_count=tx_count,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout current user",
)
async def logout(user_id: str = Depends(get_current_user_id)) -> dict:
    """
    Logout endpoint.
    Stateless JWT — client should discard tokens.
    In production, add token to a denylist (Redis).
    """
    logger.info("User logged out: %s", user_id)
    return {"message": "Successfully logged out."}
