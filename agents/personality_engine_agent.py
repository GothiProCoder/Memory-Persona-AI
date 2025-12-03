"""
Personality Transformation Agent using LangChain's create_agent().

This module defines the agent responsible for transforming system responses based
on selected personality archetypes (Mentor, Friend, Therapist) and user memory.
It utilizes LangChain's middleware capabilities to inject personality-specific
system prompts and user context dynamically.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain.messages import HumanMessage

from models.gemini_model import ModelFactory
from store.memory_store import get_memory_store
from utils.logger import get_logger
from utils.exceptions import PersonalityGenerationError, StructuredOutputError

logger = get_logger(__name__)


@dataclass
class PersonalityContext:
    """
    Context for personality transformation agent.
    
    Stores the necessary context variables (user ID, personality type) for the
    dynamic prompt middleware to customize the agent's behavior at runtime.
    """
    user_id: str
    personality_type: str


class PersonalityEngineAgent:
    """
    Agent for transforming responses based on personality type while using user memories.
    
    Uses create_agent() with dynamic middleware for personality-specific system prompts.
    It manages a set of distinct personalities and applies them to user queries.
    """
    
    # Pre-defined system prompts for each personality archetype
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
        """
        Initialize the personality engine agent.
        
        Sets up the base model and memory store access. It also initializes a
        dictionary to cache agent instances by personality type to avoid rebuilding them.
        """
        self.model = ModelFactory.get_model()
        self.store = get_memory_store()
        self._agents = {}  # Cache agents by personality type
    
    def _build_agent(self, personality_type: str) -> Any:
        """
        Build a personality-specific agent.
        
        Creates a new LangChain agent configured with the specific system prompt
        for the requested personality type. It uses middleware to inject user
        memory context dynamically before each invocation.
        
        Args:
            personality_type (str): The type of personality to build (e.g., 'mentor').
            
        Returns:
            Any: The configured agent runnable.
            
        Raises:
            PersonalityGenerationError: If the agent cannot be built.
        """
        if personality_type in self._agents:
            return self._agents[personality_type]
        
        try:
            logger.info(f"Building {personality_type} personality agent...")
            
            # Create dynamic system prompt middleware
            # This allows modifying the prompt at runtime based on the context
            @dynamic_prompt
            def personality_system_prompt(request: ModelRequest) -> str:
                base_prompt = self.PERSONALITY_PROMPTS.get(
                    personality_type,
                    self.PERSONALITY_PROMPTS["mentor"]
                )
                
                # Inject user memory context if available
                # Retrieves the user ID from the runtime context passed during invoke
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
        Generate a response with the specified personality type.
        
        Orchestrates the response generation: selects the right agent, invokes it
        with the user's query and context, and formats the output.
        
        Args:
            query (str): User query to respond to.
            personality_type (str): Type of personality (mentor, friend, therapist).
            user_id (str): User identifier for memory context.
            
        Returns:
            Dict[str, Any]: Dictionary with personality response and metadata.
            
        Raises:
            PersonalityGenerationError: If generation fails.
            StructuredOutputError: If the agent returns empty content.
        """
        try:
            if personality_type not in self.PERSONALITY_PROMPTS:
                raise ValueError(f"Unknown personality type: {personality_type}")
            
            logger.info(f"Generating {personality_type} response for user {user_id}...")
            
            agent = self._build_agent(personality_type)
            
            # Invoke agent
            # Passes context so the middleware can access user_id
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
        Generate responses for multiple personality types.
        
        Iterates through the requested personality types and generates a response
        for each one. Useful for side-by-side comparisons.
        
        Args:
            query (str): User query.
            personality_types (Optional[List[str]]): List of personality types (defaults to all).
            user_id (str): User identifier.
            
        Returns:
            Dict[str, Any]: Dictionary with all personality responses keyed by type.
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
        """
        Format memory data as context for the agent.
        
        Selects top items from user preferences, emotional patterns, and facts
        to provide a concise context summary for the prompt.
        """
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
        """Get tone characteristics list for a personality type."""
        characteristics = {
            "mentor": ["patient", "educational", "encouraging", "experienced"],
            "friend": ["witty", "supportive", "casual", "genuine"],
            "therapist": ["empathetic", "validating", "reflective", "non-judgmental"]
        }
        return characteristics.get(personality_type, [])
    
    def _get_approach_description(self, personality_type: str) -> str:
        """Get text description of the approach for a personality type."""
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
        
        Used as a baseline comparison to show the impact of the personality engine.
        
        Args:
            query (str): The user query.
            
        Returns:
            str: A neutral AI response.
            
        Raises:
            PersonalityGenerationError: If the base model fails to respond.
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
    """
    Get or create the global personality engine instance.
    
    Singleton pattern for efficient resource usage.
    
    Returns:
        PersonalityEngineAgent: The global agent instance.
    """
    if not hasattr(get_personality_engine, '_instance'):
        get_personality_engine._instance = PersonalityEngineAgent()
    return get_personality_engine._instance
