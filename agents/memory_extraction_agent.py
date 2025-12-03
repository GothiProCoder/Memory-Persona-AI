"""
Memory Extraction Agent using LangChain's create_agent()
https://docs.langchain.com/oss/python/langchain/agents
https://docs.langchain.com/oss/python/langchain/structured-output
"""

from typing import Any, Dict, List
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy, ToolStrategy
from langchain.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from schemas.memory_schemas import MemoryExtractionResult
from models.gemini_model import ModelFactory
from store.memory_store import get_memory_store
from utils.logger import get_logger
from utils.exceptions import MemoryExtractionError, StructuredOutputError

from langchain_core.globals import set_debug, set_verbose
set_verbose(True)
set_debug(True)
logger = get_logger(__name__)


@dataclass
class MemoryExtractionContext:
    """
    Context for memory extraction agent
    https://docs.langchain.com/oss/python/langchain/runtime
    """
    user_id: str
    message_count: int


class MemoryExtractionAgent:
    """
    Agent for extracting user memories, preferences, and emotional patterns from chat history
    Uses create_agent() with ProviderStrategy for Gemini structured output
    https://docs.langchain.com/oss/python/langchain/agents
    https://docs.langchain.com/oss/python/langchain/structured-output
    """
    
    def __init__(self):
        """Initialize the memory extraction agent"""
        self.model = ModelFactory.get_model().with_config(timeout=60)
        self.store = get_memory_store()
        self._agent = None
    
    def _build_agent(self) -> Any:
        """
        Build the memory extraction agent using create_agent()
        https://docs.langchain.com/oss/python/langchain/agents
        https://docs.langchain.com/oss/python/langchain/structured-output
        """
        if self._agent is not None:
            return self._agent
        
        try:
            logger.info("Building memory extraction agent...")
            
            # Create agent with ProviderStrategy for Gemini native structured output
            # https://docs.langchain.com/oss/python/langchain/structured-output
            # self._agent = create_agent(
            #     model=self.model,
            #     tools=[],  # Memory extraction doesn't need external tools
            #     response_format=ProviderStrategy(MemoryExtractionResult),
            #     system_prompt=self._get_system_prompt(),
            #     context_schema=MemoryExtractionContext,
            # )
            
            self._agent = create_agent(
                model=self.model,
                tools=[],
                response_format=ToolStrategy(
                    schema=MemoryExtractionResult,
                    handle_errors=True,  # Enable automatic retry on validation errors
                    tool_message_content="Memory extraction completed successfully. Profile saved."
                ),
                system_prompt=self._get_system_prompt(),
            )
            
            logger.info("✓ Memory extraction agent built successfully")
            return self._agent
            
        except Exception as e:
            logger.error(f"✗ Failed to build memory extraction agent: {str(e)}")
            raise MemoryExtractionError(f"Agent creation failed: {str(e)}")
    
    def _get_system_prompt(self) -> str:
        """System prompt for memory extraction with explicit JSON instruction"""
        return """You are an expert memory extraction specialist. Analyze the provided chat conversation and extract structured insights about the user.

    EXTRACTION GUIDELINES:

    1. **User Preferences** (with confidence 0-1):
    - Communication style preferences
    - Work/productivity preferences  
    - Social interaction preferences
    - Technical preferences
    - Only include confidence >= 0.7

    2. **Emotional Patterns** (with frequency):
    - Recurring emotional states
    - Identified triggers
    - Frequency: "rare", "occasional", or "frequent"

    3. **Memorable Facts** (prioritized):
    - Personal information (hobbies, interests, life events)
    - Professional achievements and goals
    - Health or wellness details
    - Relationships mentioned
    - Importance: "low", "medium", or "high"

    4. **Summary**:
    - 1-2 sentences capturing user's core profile

    CRITICAL REQUIREMENTS:
    - Return ONLY valid JSON matching the specified schema
    - All string fields must be non-empty
    - Confidence scores must be between 0.0 and 1.0
    - Frequency must be: "rare", "occasional", or "frequent"
    - Importance must be: "low", "medium", or "high"
    - Use empty arrays [] for categories with no findings
    - Do NOT fabricate information - only extract what's explicitly present
    - Do NOT return markdown, code blocks, or explanations - JSON ONLY"""

    
    def extract_memories(self, messages: List[Dict[str, str]], user_id: str = "default_user") -> Dict[str, Any]:
        """
        Extract memories from a list of chat messages
        
        Args:
            messages: List of chat messages [{"role": "user", "content": "..."}, ...]
            user_id: User identifier for storing memories
            
        Returns:
            Dictionary containing extracted memories
            
        Raises:
            MemoryExtractionError: If extraction fails
            StructuredOutputError: If structured output parsing fails
        """
        try:
            logger.info(f"Starting memory extraction for {len(messages)} messages...")
            
            agent = self._build_agent()
            
            # Convert messages to formatted string for analysis
            formatted_messages = self._format_messages(messages)
            
            # Invoke agent with structured output
            # https://docs.langchain.com/oss/python/langchain/agents
            # result = agent.invoke(
            #     {
            #         "messages": [HumanMessage(content=formatted_messages)]
            #     },
            #     context=MemoryExtractionContext(
            #         user_id=user_id,
            #         message_count=len(messages)
            #     )
            # )
            
            result = agent.invoke(
                {"messages": [HumanMessage(content=formatted_messages)]},
                config={"timeout": 60, "max_retries": 2}  # Add timeout & retry
            )

            
            # Extract structured response
            # if "structured_response" not in result:
            #     logger.error("No structured response found in agent output")
            #     raise StructuredOutputError("Agent did not return structured response")
            
            # structured_response = result["structured_response"]
            # logger.info(f"✓ Memory extraction successful")
            
            # Extract structured response from agent state
            logger.debug(f"Full agent result keys: {list(result.keys())}")
            if "structured_response" not in result:
                # Fallback: check if result is already the Pydantic object
                if isinstance(result, dict) and "output" in result:
                    structured_response = result["output"]
                else:
                    raise StructuredOutputError("No structured response found")

            
            structured_response = result["structured_response"]
            
            # Validate response is correct type
            if not isinstance(structured_response, MemoryExtractionResult):
                logger.error(f"✗ Invalid response type: {type(structured_response)}")
                raise StructuredOutputError(
                    f"Expected MemoryExtractionResult, got {type(structured_response)}"
                )
            
            logger.info(f"✓ Memory extraction successful for user {user_id}")
            logger.info(f"  - Preferences extracted: {len(structured_response.user_preferences)}")
            logger.info(f"  - Emotional patterns found: {len(structured_response.emotional_patterns)}")
            logger.info(f"  - Memorable facts captured: {len(structured_response.memorable_facts)}")
            
            # Save to memory store
            # https://docs.langchain.com/oss/python/langchain/long-term-memory
            # memory_data = {
            #     "user_preferences": [p.dict() for p in structured_response.user_preferences],
            #     "emotional_patterns": [p.dict() for p in structured_response.emotional_patterns],
            #     "memorable_facts": [f.dict() for f in structured_response.memorable_facts],
            #     "summary": structured_response.summary
            # }
            
            memory_data = {
                "user_preferences": [p.model_dump() for p in structured_response.user_preferences],
                "emotional_patterns": [p.model_dump() for p in structured_response.emotional_patterns],
                "memorable_facts": [f.model_dump() for f in structured_response.memorable_facts],
                "summary": structured_response.summary,
                "user_id": structured_response.user_id or user_id
            }
            
            self.store.save_user_memory(user_id, memory_data)
            
            return memory_data
            
        except StructuredOutputError:
            raise
        except MemoryExtractionError:
            raise
        except Exception as e:
            logger.error(f"✗ Memory extraction failed: {str(e)}")
            raise MemoryExtractionError(f"Memory extraction failed: {str(e)}")
    
    def _format_messages(self, messages: List[Dict[str, str]]) -> str:
        """Format messages for the agent"""
        formatted = "Analyze the following conversation:\n\n"
        for i, msg in enumerate(messages, 1):
            role = msg.get("role", "unknown").upper()
            content = msg.get("content", "")
            formatted += f"{i}. [{role}]: {content}\n"
        return formatted


def get_memory_extraction_agent() -> MemoryExtractionAgent:
    """Get or create the global memory extraction agent instance"""
    if not hasattr(get_memory_extraction_agent, '_instance'):
        get_memory_extraction_agent._instance = MemoryExtractionAgent()
    return get_memory_extraction_agent._instance