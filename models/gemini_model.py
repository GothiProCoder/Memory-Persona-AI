"""
Google Gemini 2.5 Flash Model Integration
https://docs.langchain.com/oss/python/integrations/providers/google
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import settings
from utils.logger import get_logger
from utils.exceptions import ModelInitializationError

logger = get_logger(__name__)


def initialize_gemini_model() -> ChatGoogleGenerativeAI:
    """
    Initialize Google Gemini 2.5 Flash model with proper configuration
    https://docs.langchain.com/oss/python/integrations/providers/google
    
    Returns:
        ChatGoogleGenerativeAI: Configured Gemini model instance
        
    Raises:
        ModelInitializationError: If model initialization fails
    """
    try:
        logger.info(f"Initializing {settings.MODEL_NAME}...")
        
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
    Factory for managing model instances
    """
    _instance: ChatGoogleGenerativeAI = None
    
    @classmethod
    def get_model(cls) -> ChatGoogleGenerativeAI:
        """
        Get or create Gemini model instance (singleton pattern)
        """
        if cls._instance is None:
            cls._instance = initialize_gemini_model()
        return cls._instance
    
    @classmethod
    def reset(cls):
        """Reset model instance"""
        cls._instance = None