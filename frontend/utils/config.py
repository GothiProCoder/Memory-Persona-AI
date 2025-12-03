"""
Frontend utilities and helpers.

This module loads environment variables and provides centralized configuration
constants for the frontend application, including API endpoints and UI settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# API Configuration
# Base URL for the backend API, defaults to localhost
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1")
# Default timeout for HTTP requests in seconds
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

# App Configuration
APP_NAME = "Memory Extraction & Personality Engine"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Advanced AI Agent with Long-term Memory and Personality Transformation"

# UI Configuration
SIDEBAR_WIDTH = "normal"
LAYOUT = "wide"

# API Endpoints
# Map of internal logical names to full URL paths
ENDPOINTS = {
    "health": f"{BACKEND_URL}/health",
    "memory_extract": f"{BACKEND_URL}/memory/extract",
    "memory_get": f"{BACKEND_URL}/memory/user",
    "personality_transform": f"{BACKEND_URL}/personality/transform"
}
