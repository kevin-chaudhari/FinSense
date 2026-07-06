"""
FinSense AI — API v1 Router
"""

from fastapi import APIRouter

from app.api.v1.routes import agent, auth, health, transactions

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(transactions.router)
api_router.include_router(agent.router)
api_router.include_router(health.router)
