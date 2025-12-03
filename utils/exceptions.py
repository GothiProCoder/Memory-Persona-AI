"""
Exception classes for the application
"""


class PersonalityEngineException(Exception):
    """Base exception for all Personality Engine errors"""
    pass


class ModelInitializationError(PersonalityEngineException):
    """Raised when model initialization fails"""
    pass


class AgentCreationError(PersonalityEngineException):
    """Raised when agent creation fails"""
    pass


class MemoryExtractionError(PersonalityEngineException):
    """Raised when memory extraction fails"""
    pass


class PersonalityGenerationError(PersonalityEngineException):
    """Raised when personality transformation fails"""
    pass


class InvalidInputError(PersonalityEngineException):
    """Raised when input validation fails"""
    pass


class StructuredOutputError(PersonalityEngineException):
    """Raised when structured output parsing fails"""
    pass


class StoreError(PersonalityEngineException):
    """Raised when memory store operations fail"""
    pass