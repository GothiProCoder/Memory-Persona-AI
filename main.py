"""
FastAPI main application entry point
Memory Extraction & Personality Engine Backend
https://docs.langchain.com/oss/python/langchain/agents
https://docs.langchain.com/oss/python/langchain/deploy
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from config.settings import settings
from routes import memory, personality, health
from utils.logger import get_logger

logger = get_logger(__name__)

# Create FastAPI application instance
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend system for memory extraction and personality-based response transformation",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

# Add CORS middleware
# https://docs.langchain.com/oss/python/langchain/deploy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Lifecycle events
@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info("="*70)
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"   Environment: {'DEBUG' if settings.DEBUG else 'PRODUCTION'}")
    logger.info(f"   Model: {settings.MODEL_NAME}")
    logger.info(f"   Memory Store: {settings.MEMORY_STORE_TYPE}")
    logger.info("="*70)


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    logger.info("="*70)
    logger.info(f"🛑 Shutting down {settings.APP_NAME}")
    logger.info("="*70)


# Include routers
# https://docs.langchain.com/oss/python/langchain/deploy
app.include_router(health.router)
app.include_router(memory.router)
app.include_router(personality.router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
        "openapi": "/api/openapi.json",
        "endpoints": {
            "health": "/api/v1/health",
            "memory_extract": "/api/v1/memory/extract",
            "memory_get": "/api/v1/memory/user/{user_id}",
            "personality_transform": "/api/v1/personality/transform"
        }
    }


# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return {
        "status": "error",
        "message": "Internal server error",
        "detail": str(exc) if settings.DEBUG else "An unexpected error occurred"
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting uvicorn server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )