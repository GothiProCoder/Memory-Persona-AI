"""
Health check endpoints module.

This module provides an endpoint for monitoring the application's health status.
It allows external monitoring tools to verify that the service is running and responsive.
"""

from fastapi import APIRouter
from datetime import datetime

from schemas.request_response import HealthCheckResponse
from config.settings import settings

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """
    Health check endpoint.
    
    Provides basic application status, version, and current timestamp.
    Used by load balancers and monitoring systems to check service availability.
    
    Endpoint: GET /api/v1/health
    
    Returns:
        HealthCheckResponse: A standard health status object.
    """
    return HealthCheckResponse(
        status="healthy",
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow().isoformat() + "Z"  # Standard ISO 8601 timestamp
    )
