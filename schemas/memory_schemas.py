"""
Pydantic models for structured memory extraction output
https://docs.langchain.com/oss/python/langchain/structured-output
https://docs.langchain.com/oss/python/concepts/memory
"""

from pydantic import BaseModel, Field
from typing import List


class UserPreference(BaseModel):
    """
    Individual user preference extracted from conversation
    """
    preference: str = Field(description="A specific user preference")
    category: str = Field(description="Category of preference (e.g., 'communication', 'work', 'social')")
    confidence: float = Field(description="Confidence score 0-1", ge=0, le=1)


class EmotionalPattern(BaseModel):
    """
    Identified emotional pattern in user behavior
    """
    pattern: str = Field(description="Description of the emotional pattern")
    trigger: str = Field(description="What triggers this pattern")
    frequency: str = Field(description="How often this pattern appears (rare, occasional, frequent)")


class MemorableFact(BaseModel):
    """
    Key factual information worth remembering
    """
    fact: str = Field(description="The memorable fact")
    fact_type: str = Field(description="Type of fact (e.g., 'personal', 'professional', 'hobby')")
    importance: str = Field(description="Importance level (low, medium, high)")


class MemoryExtractionResult(BaseModel):
    """
    Complete memory extraction structured output
    Using ProviderStrategy(MemoryExtractionResult) for Gemini native structured output
    https://docs.langchain.com/oss/python/langchain/structured-output
    """
    user_preferences: List[UserPreference] = Field(
        description="List of extracted user preferences",
        default_factory=list
    )
    emotional_patterns: List[EmotionalPattern] = Field(
        description="List of identified emotional patterns",
        default_factory=list
    )
    memorable_facts: List[MemorableFact] = Field(
        description="List of key facts to remember",
        default_factory=list
    )
    summary: str = Field(
        description="Brief summary of the user profile"
    )
    user_id: str = Field(
        description="Associated user ID for this memory extraction",
        default="default_user"
    )