"""
Frontend utilities and helpers
"""

import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

# App Configuration
APP_NAME = "Memory Extraction & Personality Engine"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Advanced AI Agent with Long-term Memory and Personality Transformation"

# UI Configuration
SIDEBAR_WIDTH = "normal"
LAYOUT = "wide"

# API Endpoints
ENDPOINTS = {
    "health": f"{BACKEND_URL}/health",
    "memory_extract": f"{BACKEND_URL}/memory/extract",
    "memory_get": f"{BACKEND_URL}/memory/user",
    "personality_transform": f"{BACKEND_URL}/personality/transform"
}