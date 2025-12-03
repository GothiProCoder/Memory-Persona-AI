"""
Configuration management for Personality Engine Backend.

This module defines the application settings and configuration using Pydantic's
BaseSettings. It handles environment variable loading and provides default
values for the application, including API settings, model configuration,
agent parameters, and memory storage options.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    This class defines the schema for application configuration, validating
    environment variables and providing defaults where appropriate.
    """
    
    # API Configuration
    APP_NAME: str = "Memory Extraction & Personality Engine"  # Application display name
    APP_VERSION: str = "1.0.0"  # Semantic versioning
    DEBUG: bool = False  # Enable debug mode for detailed logging and error messages
    
    # Google Gemini Configuration
    GOOGLE_API_KEY: str  # Required: Google API Key for Gemini models
    MODEL_NAME: str = "gemini-2.5-flash"  # Default model for all agents
    
    # Agent Configuration
    MAX_TOKENS: int = 4096  # Max output tokens for model generation
    TEMPERATURE: float = 0.7  # Control randomness (0.0 = deterministic, 1.0 = creative)
    TOP_P: float = 0.95  # Nucleus sampling parameter
    TOP_K: int = 40  # Top-k sampling parameter
    
    # Memory Configuration
    MEMORY_ENABLED: bool = True  # Master switch for memory features
    MEMORY_STORE_TYPE: str = "in_memory"  # "in_memory" or "persistent" - defines storage backend
    
    # Timeout Configuration
    REQUEST_TIMEOUT: int = 30  # Standard HTTP request timeout in seconds
    STREAMING_TIMEOUT: int = 60  # Timeout for streaming responses in seconds
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"  # Logging verbosity (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    class Config:
        """Pydantic configuration options."""
        env_file = ".env"  # Load variables from .env file
        case_sensitive = True  # Ensure environment variables match case exactly


# Global settings instance
# This singleton instance is imported throughout the application
settings = Settings()
