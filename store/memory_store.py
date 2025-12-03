"""
InMemoryStore implementation for long-term memory.

This module provides a wrapper around LangGraph's InMemoryStore to manage
user memories. It handles saving, retrieving, and deleting memory data
associated with specific users.
"""

from langgraph.store.memory import InMemoryStore
from typing import Any, Dict, Optional
from utils.logger import get_logger
from utils.exceptions import StoreError

logger = get_logger(__name__)


class MemoryStore:
    """
    Wrapper around LangGraph's InMemoryStore for managing long-term user memories.
    
    This class abstracts the underlying storage mechanism (currently in-memory)
    and provides a simple API for memory operations keyed by user ID.
    """
    
    def __init__(self):
        """
        Initialize the in-memory store.
        
        Sets up the underlying LangGraph InMemoryStore.
        """
        self.store = InMemoryStore()
        logger.info("✓ InMemoryStore initialized")
    
    def save_user_memory(self, user_id: str, memory_data: Dict[str, Any]) -> None:
        """
        Save user memory to the store.
        
        Stores the provided memory data under a namespace specific to users.
        
        Args:
            user_id (str): User identifier used as the key.
            memory_data (Dict[str, Any]): Memory data to store (preferences, patterns, facts).
            
        Raises:
            StoreError: If the save operation fails.
        """
        try:
            # Store with tuple namespace: ("users", user_id)
            # This namespacing strategy allows for easy separation of data types
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
        Retrieve user memory from the store.
        
        Args:
            user_id (str): User identifier.
            
        Returns:
            Optional[Dict[str, Any]]: Memory data if found, None otherwise.
            
        Raises:
            StoreError: If the retrieval operation fails.
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
        Delete user memory from the store.
        
        Args:
            user_id (str): User identifier to delete.
            
        Raises:
            StoreError: If the delete operation fails.
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
        List all stored user memories.
        
        Iterates through the 'users' namespace to find all stored memory items.
        
        Returns:
            Dict[str, Any]: Dictionary of all stored memories where keys are user_ids.
            
        Raises:
            StoreError: If the listing operation fails.
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
        """
        Get the underlying store instance for agent runtime.
        
        Returns:
            InMemoryStore: The raw LangGraph store instance.
        """
        return self.store


# Global store instance
_store_instance: Optional[MemoryStore] = None


def get_memory_store() -> MemoryStore:
    """
    Get or create the global memory store instance.
    
    Implements the Singleton pattern for the memory store.
    
    Returns:
        MemoryStore: The global memory store instance.
    """
    global _store_instance
    if _store_instance is None:
        _store_instance = MemoryStore()
    return _store_instance
