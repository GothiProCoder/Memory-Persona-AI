"""
Memory extraction API endpoints.

This module defines the REST API endpoints for the memory extraction feature.
It handles requests to analyze chat messages and extract user memories,
returning structured insights.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from schemas.request_response import MemoryExtractionRequest, MemoryExtractionResponse
from agents.memory_extraction_agent import get_memory_extraction_agent
from utils.logger import get_logger
from utils.exceptions import PersonalityEngineException

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/memory", tags=["memory"])


@router.post("/extract", response_model=MemoryExtractionResponse)
async def extract_memories(request: MemoryExtractionRequest) -> MemoryExtractionResponse:
    """
    Extract user memories, preferences, and emotional patterns from chat messages.
    
    This endpoint processes a batch of chat messages using the Memory Extraction Agent
    to identify and store key information about the user.
    
    Endpoint: POST /api/v1/memory/extract
    
    Request:
    {
        "messages": [
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."}
        ],
        "user_id": "user_123"
    }
    
    Response:
    {
        "status": "success",
        "data": {
            "user_preferences": [...],
            "emotional_patterns": [...],
            "memorable_facts": [...]
        },
        "message": "Memory extraction completed",
        "messages_analyzed": 30
    }
    
    Args:
        request (MemoryExtractionRequest): The input request containing messages and user ID.
        
    Returns:
        MemoryExtractionResponse: The result of the extraction process.
        
    Raises:
        HTTPException: If input is invalid (400) or extraction fails (500).
    """
    try:
        logger.info(f"Received memory extraction request for {len(request.messages)} messages")
        
        # Validate input
        if not request.messages:
            raise ValueError("Messages list cannot be empty")
        
        # Provide a warning if message count is low, as it affects extraction quality
        if len(request.messages) < 10:
            logger.warning(f"Only {len(request.messages)} messages provided (recommended: 30+)")
        
        # Convert Pydantic models to dictionaries for internal processing
        messages_data = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        # Get agent and extract memories
        agent = get_memory_extraction_agent()
        memory_data = agent.extract_memories(messages_data, request.user_id)
        
        return MemoryExtractionResponse(
            status="success",
            data=memory_data,
            message=f"Successfully extracted memories from {len(request.messages)} messages",
            messages_analyzed=len(request.messages)
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except PersonalityEngineException as e:
        logger.error(f"Memory extraction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Memory extraction failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/user/{user_id}", response_model=Dict[str, Any])
async def get_user_memories(user_id: str) -> Dict[str, Any]:
    """
    Retrieve stored memories for a specific user.
    
    Fetches the accumulated memory profile for a user from the persistent store.
    
    Endpoint: GET /api/v1/memory/user/{user_id}
    
    Response:
    {
        "user_id": "user_123",
        "memories": {
            "user_preferences": [...],
            "emotional_patterns": [...],
            "memorable_facts": [...]
        }
    }
    
    Args:
        user_id (str): The user identifier.
        
    Returns:
        Dict[str, Any]: A dictionary containing the user's stored memories.
        
    Raises:
        HTTPException: If no memories are found (404) or retrieval fails (500).
    """
    try:
        from agents.memory_extraction_agent import get_memory_extraction_agent
        agent = get_memory_extraction_agent()
        
        memories = agent.store.get_user_memory(user_id)
        
        if memories is None:
            raise HTTPException(status_code=404, detail=f"No memories found for user {user_id}")
        
        return {
            "user_id": user_id,
            "memories": memories
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving memories: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving memories")
