"""
Exception classes for the application.

This module defines custom exception classes used throughout the application
for error handling. All exceptions inherit from `PersonalityEngineException`
to allow for unified error catching and handling.
"""


class PersonalityEngineException(Exception):
    """
    Base exception for all Personality Engine errors.
    
    All custom exceptions in this application should inherit from this class.
    """
    pass


class ModelInitializationError(PersonalityEngineException):
    """
    Raised when model initialization fails.
    
    Occurs during setup of LLMs (e.g., Gemini) if API keys are missing or
    connection fails.
    """
    pass


class AgentCreationError(PersonalityEngineException):
    """
    Raised when agent creation fails.
    
    Occurs when LangChain agent factories encounter errors during build.
    """
    pass


class MemoryExtractionError(PersonalityEngineException):
    """
    Raised when memory extraction fails.
    
    Specific to the Memory Extraction Agent's operations during analysis.
    """
    pass


class PersonalityGenerationError(PersonalityEngineException):
    """
    Raised when personality transformation fails.
    
    Specific to the Personality Engine Agent's response transformation process.
    """
    pass


class InvalidInputError(PersonalityEngineException):
    """
    Raised when input validation fails.
    
    Used for bad user requests or malformed data before processing.
    """
    pass


class StructuredOutputError(PersonalityEngineException):
    """
    Raised when structured output parsing fails.
    
    Occurs when the LLM response cannot be parsed into the expected Pydantic model
    or JSON schema.
    """
    pass


class StoreError(PersonalityEngineException):
    """
    Raised when memory store operations fail.
    
    Wraps errors from the underlying storage mechanism (InMemory, Redis, etc.).
    """
    pass
