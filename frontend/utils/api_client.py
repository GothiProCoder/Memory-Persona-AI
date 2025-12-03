"""
API Client for GuppShupp Backend.

This module provides a Python client for interacting with the backend API.
It handles HTTP requests, error handling, and response parsing for various
endpoints including health checks, personality transformation, and memory operations.
"""
import requests
import os
from typing import Dict, Any, List

class APIClient:
    """
    Client wrapper for backend API calls.
    
    Encapsulates connection logic and error handling for the frontend.
    """
    
    def __init__(self, base_url: str = None):
        """
        Initialize the API client.
        
        Args:
            base_url (str, optional): The base URL of the backend API.
                Defaults to BACKEND_URL env var or localhost.
        """
        if base_url:
            self.base_url = base_url
        else:
            self.base_url = os.getenv("BACKEND_URL", "https://memory-persona-ai.onrender.com/") # Replace with http://localhost:8000 if trying from own system.
                                                                                                # In that case, you will need to setup gemini api key in the .env file
        self.mock_mode = False  # Disabled mock mode to integrate with real backend

    def get_health(self) -> Dict[str, Any]:
        """
        Check API health.
        
        Returns:
            Dict[str, Any]: Status dictionary containing health info or error details.
        """
        try:
            response = requests.get(f"{self.base_url}/api/v1/health")
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "error", "message": f"Status code: {response.status_code}"}
        except Exception as e:
            # Fallback to help debugging if backend is not reachable yet
            return {"status": "error", "message": f"Connection failed: {str(e)}"}

    def transform_personality(self, query: str, user_id: str = "default_user") -> Dict[str, Any]:
        """
        Send query to personality transform endpoint.
        
        Args:
            query (str): The user's input text.
            user_id (str): The ID of the user for personalization.
            
        Returns:
            Dict[str, Any]: The backend response containing personalized answers.
        """
        try:
            payload = {
                "query": query,
                "user_id": user_id,
                "personality_types": ["mentor", "friend", "therapist"]
            }
            # Increased timeout for LLM calls as generation can be slow
            response = requests.post(
                f"{self.base_url}/api/v1/personality/transform", 
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            try:
                error_data = response.json()
                error_msg = error_data.get("detail") or error_data.get("message") or str(e)
                return {"status": "error", "message": error_msg}
            except:
                return {"status": "error", "message": str(e)}
        except Exception as e:
            return {
                "status": "error",
                "message": f"Backend Error: {str(e)}",
                "original_query": query,
                "responses": {},
                "analysis": "Could not process request due to backend error."
            }

    def get_memory(self, user_id: str) -> Dict[str, Any]:
        """
        Get memories for a user.
        
        Handles different backend response structures to ensure robustness.
        
        Args:
            user_id (str): The user ID to retrieve memories for.
            
        Returns:
            Dict[str, Any]: Standardized response dictionary containing memory data.
        """
        try:
            response = requests.get(f"{self.base_url}/api/v1/memory/user/{user_id}", timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Polymorphic handling of backend response
            if "status" in data:
                # Type 1: Standard response wrapper
                return data
            elif "memories" in data:
                # Type 2: Direct response (found in route/memory.py during review)
                return {
                    "status": "success",
                    "data": data["memories"],
                    "message": "Memories retrieved successfully"
                }
            else:
                # Unknown structure, treat body as data if it looks like a memory object
                # This is a defensive coding practice
                if "user_preferences" in data:
                     return {
                        "status": "success",
                        "data": data,
                        "message": "Memories retrieved successfully"
                    }
                
                return {"status": "error", "message": "Unknown backend response format", "raw_data": data}

        except requests.exceptions.HTTPError as e:
            try:
                error_data = response.json()
                # Backend might return null/None for data if 404
                error_msg = error_data.get("detail") or error_data.get("message") or str(e)
                return {"status": "error", "message": error_msg}
            except:
                return {"status": "error", "message": str(e)}
        except Exception as e:
            print(f"Backend Error (Get Memory): {e}")
            return {"status": "error", "message": str(e), "data": {}}
            
    def extract_memory(self, messages: List[Dict[str, str]], user_id: str = "default_user") -> Dict[str, Any]:
        """
        Extract memory from chat messages.
        
        Args:
            messages (List[Dict[str, str]]): List of message dicts (role, content).
            user_id (str): The user ID associated with the messages.
            
        Returns:
            Dict[str, Any]: Backend response with extraction status and data.
        """
        try:
            payload = {
                "messages": messages,
                "user_id": user_id
            }
            # High timeout for memory extraction as it involves heavy processing
            response = requests.post(f"{self.base_url}/api/v1/memory/extract", json=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            try:
                error_data = response.json()
                error_msg = error_data.get("detail") or error_data.get("message") or str(e)
                return {"status": "error", "message": error_msg}
            except:
                return {"status": "error", "message": str(e)}
        except Exception as e:
            print(f"Backend Error (Extract Memory): {e}")
            return {"status": "error", "message": str(e), "data": {}}

    def get_generic_response(self, query: str, user_id: str = "default_user") -> Dict[str, Any]:
        """
        Get generic (non-personalized) response for BEFORE comparison.
        
        This endpoint is used to show the contrast between standard AI answers
        and the personalized ones.
        
        Args:
            query (str): The user's query.
            user_id (str): User ID (optional, mainly for logging).
            
        Returns:
            Dict[str, Any]: The generic response from the backend.
        """
        try:
            payload = {
                "query": query,
                "user_id": user_id
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/personality/generic",
                json=payload,
                timeout=30  # Shorter timeout for generic response as it's simpler
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            try:
                error_data = response.json()
                error_msg = error_data.get("detail") or error_data.get("message") or str(e)
                return {"status": "error", "message": error_msg}
            except:
                return {"status": "error", "message": str(e)}
        except Exception as e:
            return {"status": "error", "message": f"Backend Error: {str(e)}"}
