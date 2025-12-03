"""
Configuration management for Personality Engine Backend
https://docs.langchain.com/oss/python/langchain/install
https://docs.langchain.com/oss/python/integrations/providers/google
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    
    # API Configuration
    APP_NAME: str = "Memory Extraction & Personality Engine"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Google Gemini Configuration
    # https://docs.langchain.com/oss/python/integrations/providers/google
    GOOGLE_API_KEY: str
    MODEL_NAME: str = "gemini-2.5-flash"
    
    # Agent Configuration
    # https://docs.langchain.com/oss/python/langchain/agents
    MAX_TOKENS: int = 4096
    TEMPERATURE: float = 0.7
    TOP_P: float = 0.95
    TOP_K: int = 40
    
    # Memory Configuration
    # https://docs.langchain.com/oss/python/langchain/long-term-memory
    MEMORY_ENABLED: bool = True
    MEMORY_STORE_TYPE: str = "in_memory"  # "in_memory" or "persistent"
    
    # Timeout Configuration
    REQUEST_TIMEOUT: int = 30
    STREAMING_TIMEOUT: int = 60
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()