"""
Personality transformation API endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from schemas.request_response import PersonalityRequest, PersonalityTransformationResponse, GenericResponse, GenericRequest
from agents.personality_engine_agent import get_personality_engine
from utils.logger import get_logger
from utils.exceptions import PersonalityEngineException

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/personality", tags=["personality"])


@router.post("/transform", response_model=PersonalityTransformationResponse)
async def transform_with_personality(request: PersonalityRequest) -> PersonalityTransformationResponse:
    """
    Transform a response with different personality types
    
    Endpoint: POST /api/v1/personality/transform
    
    Request:
    {
        "query": "What should I do about my anxiety?",
        "personality_types": ["mentor", "friend", "therapist"],
        "user_id": "user_123"
    }
    
    Response:
    {
        "status": "success",
        "original_query": "What should I do about my anxiety?",
        "responses": {
            "mentor": {
                "personality_type": "mentor",
                "response": "...",
                "tone_characteristics": [...],
                "approach": "..."
            },
            "friend": {...},
            "therapist": {...}
        },
        "analysis": "Each personality brings unique perspective...",
        "message": "Personality responses generated successfully"
    }
    """
    try:
        logger.info(f"Received personality transformation request: {request.personality_types}")
        
        # Validate input
        if not request.query or not request.query.strip():
            raise ValueError("Query cannot be empty")
        
        if not request.personality_types:
            request.personality_types = ["mentor", "friend", "therapist"]
        
        # Validate personality types
        valid_types = {"mentor", "friend", "therapist"}
        invalid_types = set(request.personality_types) - valid_types
        if invalid_types:
            raise ValueError(f"Invalid personality types: {invalid_types}. Valid types: {valid_types}")
        
        # Get engine and generate responses
        engine = get_personality_engine()
        responses = engine.generate_personality_responses(
            query=request.query,
            personality_types=request.personality_types,
            user_id=request.user_id
        )
        
        # Generate comparison analysis
        analysis = _generate_analysis(request.query, responses)
        
        return PersonalityTransformationResponse(
            status="success",
            original_query=request.query,
            responses=responses,
            analysis=analysis,
            message="Personality responses generated successfully"
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except PersonalityEngineException as e:
        logger.error(f"Personality generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Personality transformation failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


def _generate_analysis(query: str, responses: Dict[str, Any]) -> str:
    """Generate a comparative analysis of the different personality responses"""
    analysis = f"Analysis for query: '{query}'\n\n"
    
    success_count = sum(1 for r in responses.values() if "error" not in r)
    analysis += f"Generated {success_count} personality responses.\n\n"
    
    if "mentor" in responses and "error" not in responses.get("mentor", {}):
        analysis += "**Mentor approach**: Provides structured guidance and learning-focused advice.\n\n"
    
    if "friend" in responses and "error" not in responses.get("friend", {}):
        analysis += "**Friend approach**: Offers relatable, supportive perspective with casual tone.\n\n"
    
    if "therapist" in responses and "error" not in responses.get("therapist", {}):
        analysis += "**Therapist approach**: Uses empathetic listening and emotional validation.\n"
    
    analysis += "\nEach personality type brings unique perspectives to the same question, " \
                "allowing you to choose the response style that best fits your needs."
    
    return analysis

@router.post("/generic", response_model=GenericResponse)
async def get_generic_response(request: GenericRequest) -> GenericResponse:
    """
    Return a generic, non-personalized response.
    Frontend will label this as 'BEFORE' in the UI.
    
    Endpoint: POST /api/v1/personality/generic
    """
    try:
        if not request.query or not request.query.strip():
            raise ValueError("Query cannot be empty")

        engine = get_personality_engine()
        generic_text = engine.generate_generic_response(request.query)

        return {
            "status": "success",
            "query": request.query,
            "generic_response": generic_text,
            "message": "Generic response generated"
        }

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Generic response error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
