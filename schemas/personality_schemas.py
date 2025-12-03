"""
Pydantic models for personality transformation output.

This module defines the schemas for generating responses with specific personality
traits. It allows the system to produce multiple variations of a response (e.g.,
Mentor, Friend, Therapist) from a single query.
"""

from pydantic import BaseModel, Field
from typing import List, Literal


class PersonalityResponse(BaseModel):
    """
    Response from a single personality type.
    
    Contains the transformed response content along with metadata about how
    the personality was applied.
    """
    personality_type: Literal["mentor", "friend", "therapist"] = Field(
        description="The personality type used for this response"
    )
    response: str = Field(
        description="The generated response in the specified personality tone"
    )
    tone_characteristics: List[str] = Field(
        description="Key characteristics of this personality's tone"
    )
    approach: str = Field(
        description="The approach used in this response"
    )


class PersonalityTransformationResult(BaseModel):
    """
    Complete personality transformation result with multiple personality responses.
    
    This is the structured output returned by the Personality Engine Agent, containing
    responses for all requested personality archetypes.
    
    Using ProviderStrategy(PersonalityTransformationResult) for Gemini native structured output
    """
    user_query: str = Field(
        description="The original user query"
    )
    responses: List[PersonalityResponse] = Field(
        description="Responses from different personality types"
    )
    analysis: str = Field(
        description="Brief analysis of how each personality approaches the query"
    )


class PersonalityComparison(BaseModel):
    """
    Comparison data for displaying before/after personality differences.
    
    Used primarily for frontend display to show side-by-side comparisons of
    how different personalities handle the same input.
    """
    query: str = Field(description="The original query")
    mentor_response: str = Field(description="Mentor personality response")
    friend_response: str = Field(description="Friend personality response")
    therapist_response: str = Field(description="Therapist personality response")
    analysis: str = Field(description="Comparative analysis of responses")
