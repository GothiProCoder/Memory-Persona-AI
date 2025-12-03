"""
Personality Transformation Agent using LangChain's create_agent()
Transforms responses based on stored user memories and selected personality type
https://docs.langchain.com/oss/python/langchain/agents
https://docs.langchain.com/oss/python/langchain/structured-output
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy, ToolStrategy
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain.messages import HumanMessage

from schemas.personality_schemas import PersonalityResponse
from models.gemini_model import ModelFactory
from store.memory_store import get_memory_store
from utils.logger import get_logger
from utils.exceptions import PersonalityGenerationError, StructuredOutputError

logger = get_logger(__name__)


@dataclass
class PersonalityContext:
    """
    Context for personality transformation agent
    https://docs.langchain.com/oss/python/langchain/runtime
    """
    user_id: str
    personality_type: str


class PersonalityEngineAgent:
    """
    Agent for transforming responses based on personality type while using user memories
    Uses create_agent() with dynamic middleware for personality-specific system prompts
    https://docs.langchain.com/oss/python/langchain/agents
    https://docs.langchain.com/oss/python/langchain/structured-output
    """
    
    PERSONALITY_PROMPTS = {
        "mentor": """You are a wise, patient mentor with deep expertise. Your approach:
- Provide thoughtful guidance rooted in experience
- Ask clarifying questions to understand the deeper need
- Reference the user's interests and background when available
- Offer structured learning paths
- Balance encouragement with honest feedback
- Keep responses educational yet warm and supportive""",
        
        "friend": """You are a witty, supportive friend who genuinely cares. Your approach:
- Match the user's energy and communication style
- Use appropriate humor to lighten the mood
- Reference shared experiences or knowledge
- Be direct but never harsh
- Offer practical advice wrapped in casual conversation
- Show genuine interest in their well-being""",
        
        "therapist": """You are an empathetic therapist trained in active listening. Your approach:
- Validate emotions and experiences first
- Use reflective listening techniques
- Ask open-ended questions to encourage exploration
- Avoid judgment and show unconditional positive regard
- Help identify patterns and underlying needs
- Suggest coping strategies when appropriate"""
    }
    
    def __init__(self):
        """Initialize the personality engine agent"""
        self.model = ModelFactory.get_model()
        self.store = get_memory_store()
        self._agents = {}  # Cache agents by personality type
    
    def _build_agent(self, personality_type: str) -> Any:
        """
        Build a personality-specific agent
        https://docs.langchain.com/oss/python/langchain/agents
        """
        if personality_type in self._agents:
            return self._agents[personality_type]
        
        try:
            logger.info(f"Building {personality_type} personality agent...")
            
            # Create dynamic system prompt middleware
            # https://docs.langchain.com/oss/python/langchain/agents (middleware section)
            @dynamic_prompt
            def personality_system_prompt(request: ModelRequest) -> str:
                base_prompt = self.PERSONALITY_PROMPTS.get(
                    personality_type,
                    self.PERSONALITY_PROMPTS["mentor"]
                )
                
                # Inject user memory context if available
                user_id = getattr(request.runtime.context, 'user_id', 'default_user')
                user_memory = self.store.get_user_memory(user_id)
                
                if user_memory:
                    memory_context = self._format_memory_context(user_memory)
                    return f"{base_prompt}\n\n{memory_context}"
                
                return base_prompt
            
            # Create agent with middleware for dynamic personality prompts
            agent = create_agent(
                model=self.model,
                tools=[],  # No external tools needed for personality transformation
                system_prompt=self.PERSONALITY_PROMPTS.get(
                    personality_type,
                    self.PERSONALITY_PROMPTS["mentor"]
                ),
                middleware=[personality_system_prompt],
                context_schema=PersonalityContext,
            )
            
            self._agents[personality_type] = agent
            logger.info(f"✓ {personality_type} personality agent built successfully")
            return agent
            
        except Exception as e:
            logger.error(f"✗ Failed to build {personality_type} personality agent: {str(e)}")
            raise PersonalityGenerationError(f"Agent creation failed: {str(e)}")
    
    def generate_response(
        self,
        query: str,
        personality_type: str,
        user_id: str = "default_user"
    ) -> Dict[str, Any]:
        """
        Generate a response with the specified personality type
        
        Args:
            query: User query to respond to
            personality_type: Type of personality (mentor, friend, therapist)
            user_id: User identifier for memory context
            
        Returns:
            Dictionary with personality response
            
        Raises:
            PersonalityGenerationError: If generation fails
        """
        try:
            if personality_type not in self.PERSONALITY_PROMPTS:
                raise ValueError(f"Unknown personality type: {personality_type}")
            
            logger.info(f"Generating {personality_type} response for user {user_id}...")
            
            agent = self._build_agent(personality_type)
            
            # Invoke agent
            result = agent.invoke(
                {"messages": [HumanMessage(content=query)]},
                context=PersonalityContext(
                    user_id=user_id,
                    personality_type=personality_type
                )
            )
            
            # Extract response from last message
            response_content = None
            if result["messages"]:
                last_message = result["messages"][-1]
                response_content = getattr(last_message, 'content', str(last_message))
            
            if not response_content:
                logger.error(f"No response content from {personality_type} agent")
                raise StructuredOutputError("Agent did not return response content")
            
            logger.info(f"✓ {personality_type} response generated successfully")
            
            return {
                "personality_type": personality_type,
                "response": response_content,
                "tone_characteristics": self._get_tone_characteristics(personality_type),
                "approach": self._get_approach_description(personality_type)
            }
            
        except PersonalityGenerationError:
            raise
        except Exception as e:
            logger.error(f"✗ Response generation failed: {str(e)}")
            raise PersonalityGenerationError(f"Response generation failed: {str(e)}")
    
    def generate_personality_responses(
        self,
        query: str,
        personality_types: Optional[List[str]] = None,
        user_id: str = "default_user"
    ) -> Dict[str, Any]:
        """
        Generate responses for multiple personality types
        
        Args:
            query: User query
            personality_types: List of personality types (defaults to all)
            user_id: User identifier
            
        Returns:
            Dictionary with all personality responses
        """
        if personality_types is None:
            personality_types = list(self.PERSONALITY_PROMPTS.keys())
        
        responses = {}
        for personality_type in personality_types:
            try:
                response = self.generate_response(query, personality_type, user_id)
                responses[personality_type] = response
            except Exception as e:
                logger.error(f"Failed to generate {personality_type} response: {str(e)}")
                responses[personality_type] = {
                    "error": str(e),
                    "personality_type": personality_type
                }
        
        return responses
    
    def _format_memory_context(self, memory_data: Dict[str, Any]) -> str:
        """Format memory data as context for the agent"""
        context = "IMPORTANT - User Context (use to personalize responses):\n"
        
        if memory_data.get("user_preferences"):
            prefs = memory_data["user_preferences"][:3]  # Top 3
            context += f"Preferences: {', '.join(p.get('preference', '') for p in prefs)}\n"
        
        if memory_data.get("emotional_patterns"):
            patterns = memory_data["emotional_patterns"][:2]  # Top 2
            context += f"Emotional patterns: {', '.join(p.get('pattern', '') for p in patterns)}\n"
        
        if memory_data.get("memorable_facts"):
            facts = memory_data["memorable_facts"][:2]  # Top 2
            context += f"Key facts: {', '.join(f.get('fact', '') for f in facts)}\n"
        
        return context
    
    def _get_tone_characteristics(self, personality_type: str) -> List[str]:
        """Get tone characteristics for a personality type"""
        characteristics = {
            "mentor": ["patient", "educational", "encouraging", "experienced"],
            "friend": ["witty", "supportive", "casual", "genuine"],
            "therapist": ["empathetic", "validating", "reflective", "non-judgmental"]
        }
        return characteristics.get(personality_type, [])
    
    def _get_approach_description(self, personality_type: str) -> str:
        """Get approach description for a personality type"""
        approaches = {
            "mentor": "Provides structured guidance with learning focus",
            "friend": "Offers support with casual, relatable tone",
            "therapist": "Uses active listening and emotional validation"
        }
        return approaches.get(personality_type, "Unknown approach")

    def generate_generic_response(self, query: str) -> str:
        """
        Generate a neutral, generic response without using stored memory
        or any personality-specific prompt.
        """
        try:
            prompt = (
                "You are a neutral, professional assistant. "
                "Answer the user's query in 2-3 concise sentences. "
                "Do not reference any prior conversation history or personal details.\n\n"
                f"User query: {query}"
            )
            # ([HumanMessage(content=prompt)])
            result = self.model.invoke(
                [HumanMessage(content=prompt)],
                config={"timeout": 30}  # 30 second timeout for generic
            )

            content = getattr(result, "content", str(result))

            if not content:
                logger.error("Empty generic response from base model")
                raise PersonalityGenerationError("Generic response was empty")

            return content

        except Exception as e:
            logger.error(f"Generic response generation failed: {e}")
            raise PersonalityGenerationError(f"Generic response generation failed: {e}")
    

def get_personality_engine() -> PersonalityEngineAgent:
    """Get or create the global personality engine instance"""
    if not hasattr(get_personality_engine, '_instance'):
        get_personality_engine._instance = PersonalityEngineAgent()
    return get_personality_engine._instance