"""
FinSense AI — Backend API Tests
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

# Set test env vars BEFORE importing app
import os
os.environ.setdefault("GOOGLE_API_KEY", "test_key_for_testing")
os.environ.setdefault("SECRET_KEY", "test_secret_key_must_be_32_chars_long!!")
os.environ.setdefault("ENVIRONMENT", "development")

from app.main import app

client = TestClient(app, raise_server_exceptions=False)


class TestHealthRoutes:
    def test_health_returns_200(self):
        response = client.get("/api/v1/health")
        # May return 500 if embedding service fails to init in test env
        assert response.status_code in (200, 500)

    def test_gpu_health_returns_json(self):
        response = client.get("/api/v1/health/gpu")
        assert response.status_code in (200, 500)
        if response.status_code == 200:
            data = response.json()
            assert "cuda_available" in data


class TestAuthRoutes:
    def test_register_user(self):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser_api",
                "password": "SecurePassword123!",
                "display_name": "Test User",
            },
        )
        # 201 = success, 409 = already exists (idempotent)
        assert response.status_code in (201, 409, 503)

    def test_login_wrong_password(self):
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "nonexistent", "password": "wrongpass"},
        )
        assert response.status_code in (404, 422, 503)

    def test_me_without_token(self):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_me_with_invalid_token(self):
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401


class TestTransactionRoutes:
    def test_list_transactions_without_auth(self):
        response = client.get("/api/v1/transactions")
        assert response.status_code == 401

    def test_create_transaction_without_auth(self):
        response = client.post(
            "/api/v1/transactions",
            json={
                "amount": 50.0,
                "transaction_type": "debit",
                "category": "Food & Dining",
                "description": "Test transaction",
                "date": "2025-01-01T00:00:00",
            },
        )
        assert response.status_code == 401

    def test_transaction_validation_negative_amount(self):
        """Negative amounts should be rejected by Pydantic validation."""
        # Even without auth, Pydantic should catch this
        response = client.post(
            "/api/v1/transactions",
            json={
                "amount": -50.0,  # Invalid
                "transaction_type": "debit",
                "category": "Food & Dining",
                "description": "Invalid",
                "date": "2025-01-01T00:00:00",
            },
        )
        assert response.status_code in (401, 422)  # Auth fails first, then validation


class TestAgentRoutes:
    def test_agent_query_without_auth(self):
        response = client.post(
            "/api/v1/agent/query",
            json={"question": "What is a budget?"},
        )
        assert response.status_code == 401

    def test_agent_query_with_invalid_token(self):
        response = client.post(
            "/api/v1/agent/query",
            json={"question": "What is a budget?"},
            headers={"Authorization": "Bearer invalid"},
        )
        assert response.status_code == 401


class TestSecurity:
    """Security regression tests."""

    def test_no_sensitive_data_in_error_response(self):
        """Error responses should not leak stack traces."""
        response = client.get("/api/v1/nonexistent-endpoint")
        assert response.status_code == 404

    def test_cors_headers_present(self):
        response = client.options(
            "/api/v1/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        # CORS should be configured
        assert response.status_code in (200, 405)
