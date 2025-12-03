"""
FastAPI main application entry point.

This module initializes the FastAPI application, configures middleware (CORS),
sets up lifecycle events (startup, shutdown), and includes API routers.
It serves as the backend for the Memory Extraction & Personality Engine.

Memory Extraction & Personality Engine Backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production - Allow all origins for dev/demo
    allow_credentials=True,  # Allow cookies and authentication headers
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Lifecycle events
@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler.
    
    Logs initial configuration and environment details when the application starts.
    This helps in verifying the runtime environment.
    """
    logger.info("="*70)
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"   Environment: {'DEBUG' if settings.DEBUG else 'PRODUCTION'}")
    logger.info(f"   Model: {settings.MODEL_NAME}")
    logger.info(f"   Memory Store: {settings.MEMORY_STORE_TYPE}")
    logger.info("="*70)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event handler.
    
    Performs cleanup tasks and logs the shutdown event.
    """
    logger.info("="*70)
    logger.info(f"🛑 Shutting down {settings.APP_NAME}")
    logger.info("="*70)


# Include routers
app.include_router(health.router)
app.include_router(memory.router)
app.include_router(personality.router)


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint - API information.
    
    Returns:
        dict: A dictionary containing application metadata and key endpoint URLs.
    """
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
    """
    Global exception handler for unhandled exceptions.
    
    Args:
        request (Request): The incoming request that caused the error.
        exc (Exception): The exception that was raised.
        
    Returns:
        dict: A standardized error response with status, message, and details.
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return {
        "status": "error",
        "message": "Internal server error",
        "detail": str(exc) if settings.DEBUG else "An unexpected error occurred"  # Hide details in production
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting uvicorn server...")
    # Run uvicorn programmatically for local development
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )
