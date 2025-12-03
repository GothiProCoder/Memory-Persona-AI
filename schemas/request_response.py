"""
API request and response schemas
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any


class ChatMessage(BaseModel):
    """Single chat message"""
    role: str = Field(description="Role: 'user' or 'assistant'")
    content: str = Field(description="Message content")


class MemoryExtractionRequest(BaseModel):
    """
    Request for memory extraction endpoint
    """
    messages: List[ChatMessage] = Field(
        description="List of 30+ chat messages to analyze"
    )
    user_id: str = Field(
        description="User ID for storing memories",
        default="default_user"
    )


class MemoryExtractionResponse(BaseModel):
    """
    Response from memory extraction endpoint
    """
    status: str = Field(description="Status of extraction (success/error)")
    data: Dict[str, Any] = Field(description="Extracted memory data")
    message: str = Field(description="Human-readable message")
    messages_analyzed: int = Field(description="Number of messages analyzed")


class PersonalityRequest(BaseModel):
    """
    Request for personality transformation endpoint
    """
    query: str = Field(description="User query to transform")
    personality_types: List[str] = Field(
        description="List of personality types to use (mentor, friend, therapist)",
        default=["mentor", "friend", "therapist"]
    )
    user_id: str = Field(
        description="User ID to apply their stored memories",
        default="default_user"
    )


class PersonalityResponseItem(BaseModel):
    """Single personality response item"""
    personality_type: str
    response: str
    tone_characteristics: List[str]
    approach: str


class PersonalityTransformationResponse(BaseModel):
    """
    Response from personality transformation endpoint
    """
    status: str = Field(description="Status (success/error)")
    original_query: str = Field(description="The original query")
    responses: Dict[str, Any] = Field(description="Responses for each personality")
    analysis: str = Field(description="Comparative analysis")
    message: str = Field(description="Human-readable message")


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(description="Status (healthy/unhealthy)")
    version: str = Field(description="API version")
    timestamp: str = Field(description="ISO timestamp")

class GenericRequest(BaseModel):
    """
    Request for generic (non-personalized) response endpoint
    """
    query: str = Field(description="User query")
    user_id: str = Field(
        default="default_user",
        description="User ID (optional, for tracking but not used for personalization)"
    )

class GenericResponse(BaseModel):
    """
    Response from generic (non-personalized) endpoint
    Per LangChain structured output docs:
    [https://docs.langchain.com/oss/python/langchain/structured-output](https://docs.langchain.com/oss/python/langchain/structured-output)
    """
    status: str = Field(description="Status (success/error)")
    query: str = Field(description="The original query")
    generic_response: str = Field(description="Generic AI response without memory or personality")
    message: str = Field(description="Human-readable message")
