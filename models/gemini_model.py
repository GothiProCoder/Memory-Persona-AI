"""
Google Gemini 2.5 Flash Model Integration module.

This module handles the initialization and configuration of the Google Gemini
Large Language Model (LLM) using LangChain's integration. It ensures that the
model is correctly set up with API keys and parameters from the settings.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import settings
from utils.logger import get_logger
from utils.exceptions import ModelInitializationError

logger = get_logger(__name__)


def initialize_gemini_model() -> ChatGoogleGenerativeAI:
    """
    Initialize Google Gemini 2.5 Flash model with proper configuration.
    
    Creates a new instance of `ChatGoogleGenerativeAI` with settings defined
    in the application configuration (temperature, tokens, etc.).
    
    Returns:
        ChatGoogleGenerativeAI: Configured Gemini model instance ready for generation.
        
    Raises:
        ModelInitializationError: If model initialization fails (e.g., invalid API key).
    """
    try:
        logger.info(f"Initializing {settings.MODEL_NAME}...")
        
        # Initialize the model with parameters from settings
        # These control the creativity and length of the output
        model = ChatGoogleGenerativeAI(
            model=settings.MODEL_NAME,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=settings.TEMPERATURE,
            max_output_tokens=settings.MAX_TOKENS,
            top_p=settings.TOP_P,
            top_k=settings.TOP_K,
        )
        
        logger.info(f"✓ {settings.MODEL_NAME} initialized successfully")
        return model
        
    except Exception as e:
        logger.error(f"✗ Failed to initialize Gemini model: {str(e)}")
        raise ModelInitializationError(f"Model initialization failed: {str(e)}")


class ModelFactory:
    """
    Factory for managing model instances.
    
    Implements the Singleton pattern to ensure only one model instance is created
    and reused throughout the application lifecycle, which is efficient for resource usage.
    """
    _instance: ChatGoogleGenerativeAI = None
    
    @classmethod
    def get_model(cls) -> ChatGoogleGenerativeAI:
        """
        Get or create Gemini model instance (singleton pattern).
        
        If an instance already exists, it returns it. Otherwise, it creates a new one
        using `initialize_gemini_model`.
        
        Returns:
            ChatGoogleGenerativeAI: The singleton model instance.
        """
        if cls._instance is None:
            cls._instance = initialize_gemini_model()
        return cls._instance
    
    @classmethod
    def reset(cls):
        """
        Reset model instance.
        
        Clears the singleton instance, forcing re-initialization on the next call
        to `get_model`. Useful for testing or configuration changes.
        """
        cls._instance = None
