"""
Memory Extraction Agent using LangChain's create_agent().

This module defines the agent responsible for analyzing chat history and extracting
structured information about the user, including preferences, emotional patterns,
and memorable facts. It uses Google's Gemini model with structured output.
"""

from typing import Any, Dict, List
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain.messages import HumanMessage

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
    Context for memory extraction agent.
    
    Holds runtime context data required by the agent during execution.
    """
    user_id: str
    message_count: int


class MemoryExtractionAgent:
    """
    Agent for extracting user memories, preferences, and emotional patterns from chat history.
    
    Uses create_agent() with ToolStrategy for Gemini structured output to ensure
    the response conforms to the `MemoryExtractionResult` schema.
    """
    
    def __init__(self):
        """
        Initialize the memory extraction agent.
        
        Sets up the model with a higher timeout for long processing and gets
        the global memory store instance.
        """
        self.model = ModelFactory.get_model().with_config(timeout=60)
        self.store = get_memory_store()
        self._agent = None
    
    def _build_agent(self) -> Any:
        """
        Build the memory extraction agent using create_agent().
        
        Configures the agent with the Gemini model and a structured output strategy.
        It uses `ToolStrategy` to force the model to output data matching the
        `MemoryExtractionResult` Pydantic model.
        
        Returns:
            Any: The compiled LangChain agent runnable.
            
        Raises:
            MemoryExtractionError: If agent creation fails.
        """
        if self._agent is not None:
            return self._agent
        
        try:
            logger.info("Building memory extraction agent...")
             
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
        """
        System prompt for memory extraction with explicit JSON instruction.
        
        Returns:
            str: The detailed system prompt guiding the model on how to extract information.
        """
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
        Extract memories from a list of chat messages.
        
        Orchestrates the extraction process: formats messages, invokes the agent,
        validates the structured output, and saves the result to the store.
        
        Args:
            messages (List[Dict[str, str]]): List of chat messages [{"role": "user", "content": "..."}, ...]
            user_id (str): User identifier for storing memories.
            
        Returns:
            Dict[str, Any]: Dictionary containing extracted memories.
            
        Raises:
            MemoryExtractionError: If extraction fails generally.
            StructuredOutputError: If structured output parsing fails.
        """
        try:
            logger.info(f"Starting memory extraction for {len(messages)} messages...")
            
            agent = self._build_agent()
            
            # Convert messages to formatted string for analysis
            formatted_messages = self._format_messages(messages)
            
            # Invoke the agent with a timeout and retry logic
            result = agent.invoke(
                {"messages": [HumanMessage(content=formatted_messages)]},
                config={"timeout": 60, "max_retries": 2}  # Add timeout & retry
            )

            # Extract structured response from agent state
            logger.debug(f"Full agent result keys: {list(result.keys())}")
            if "structured_response" not in result:
                # Fallback: check if result is already the Pydantic object
                # This handles cases where the agent returns the output directly
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
            
            # Serialize the structured response to a dictionary for storage
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
        """
        Format messages for the agent.
        
        Converts the list of message dictionaries into a single string format
        suitable for LLM consumption.
        
        Args:
            messages (List[Dict[str, str]]): List of message dictionaries.
            
        Returns:
            str: Formatted conversation string.
        """
        formatted = "Analyze the following conversation:\n\n"
        for i, msg in enumerate(messages, 1):
            role = msg.get("role", "unknown").upper()
            content = msg.get("content", "")
            formatted += f"{i}. [{role}]: {content}\n"
        return formatted


def get_memory_extraction_agent() -> MemoryExtractionAgent:
    """
    Get or create the global memory extraction agent instance.
    
    Implements Singleton pattern for the agent to reuse resources.
    
    Returns:
        MemoryExtractionAgent: The global agent instance.
    """
    if not hasattr(get_memory_extraction_agent, '_instance'):
        get_memory_extraction_agent._instance = MemoryExtractionAgent()
    return get_memory_extraction_agent._instance
