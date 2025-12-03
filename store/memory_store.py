"""
InMemoryStore implementation for long-term memory
https://docs.langchain.com/oss/python/langchain/long-term-memory
"""

from langgraph.store.memory import InMemoryStore
from typing import Any, Dict, Optional
from utils.logger import get_logger
from utils.exceptions import StoreError

logger = get_logger(__name__)


class MemoryStore:
    """
    Wrapper around LangGraph's InMemoryStore for managing long-term user memories
    https://docs.langchain.com/oss/python/langchain/long-term-memory
    """
    
    def __init__(self):
        """Initialize the in-memory store"""
        self.store = InMemoryStore()
        logger.info("✓ InMemoryStore initialized")
    
    def save_user_memory(self, user_id: str, memory_data: Dict[str, Any]) -> None:
        """
        Save user memory to the store
        
        Args:
            user_id: User identifier
            memory_data: Memory data to store (preferences, patterns, facts)
        """
        try:
            # Store with tuple namespace: ("users", user_id)
            self.store.put(
                namespace=("users",),
                key=user_id,
                value=memory_data
            )
            logger.info(f"✓ Saved memory for user: {user_id}")
        except Exception as e:
            logger.error(f"✗ Failed to save memory for user {user_id}: {str(e)}")
            raise StoreError(f"Failed to save user memory: {str(e)}")
    
    def get_user_memory(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user memory from the store
        
        Args:
            user_id: User identifier
            
        Returns:
            Memory data if found, None otherwise
        """
        try:
            result = self.store.get(
                namespace=("users",),
                key=user_id
            )
            if result:
                logger.info(f"✓ Retrieved memory for user: {user_id}")
                return result.value
            else:
                logger.info(f"ℹ No memory found for user: {user_id}")
                return None
        except Exception as e:
            logger.error(f"✗ Failed to retrieve memory for user {user_id}: {str(e)}")
            raise StoreError(f"Failed to retrieve user memory: {str(e)}")
    
    def delete_user_memory(self, user_id: str) -> None:
        """
        Delete user memory from the store
        
        Args:
            user_id: User identifier
        """
        try:
            self.store.delete(
                namespace=("users",),
                key=user_id
            )
            logger.info(f"✓ Deleted memory for user: {user_id}")
        except Exception as e:
            logger.error(f"✗ Failed to delete memory for user {user_id}: {str(e)}")
            raise StoreError(f"Failed to delete user memory: {str(e)}")
    
    def list_user_memories(self) -> Dict[str, Any]:
        """
        List all stored user memories
        
        Returns:
            Dictionary of all stored memories
        """
        try:
            memories = {}
            # LangGraph's InMemoryStore stores items - iterate through namespace
            for item in self.store.search(namespace=("users",)):
                if item:
                    memories[item.key] = item.value
            logger.info(f"ℹ Found {len(memories)} stored memories")
            return memories
        except Exception as e:
            logger.error(f"✗ Failed to list memories: {str(e)}")
            raise StoreError(f"Failed to list memories: {str(e)}")
    
    def get_store(self) -> InMemoryStore:
        """Get the underlying store instance for agent runtime"""
        return self.store


# Global store instance
_store_instance: Optional[MemoryStore] = None


def get_memory_store() -> MemoryStore:
    """
    Get or create the global memory store instance
    """
    global _store_instance
    if _store_instance is None:
        _store_instance = MemoryStore()
    return _store_instance