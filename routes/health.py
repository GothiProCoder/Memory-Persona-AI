"""
Health check endpoints
"""

from fastapi import APIRouter
from datetime import datetime

from schemas.request_response import HealthCheckResponse
from config.settings import settings

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """
    Health check endpoint
    
    Endpoint: GET /api/v1/health
    
    Response:
    {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": "2024-12-02T19:30:00Z"
    }
    """
    return HealthCheckResponse(
        status="healthy",
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )