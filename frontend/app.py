"""
Frontend application entry point.

This module initializes the Streamlit application, configuring the page layout,
styles, and session state. It routes to different application components based
on the selected page in the sidebar (Chat or Memories).
"""

import streamlit as st
import sys
import os
import requests
import time

# Add the current directory to sys.path so we can import from frontend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from frontend.utils.api_client import APIClient
from frontend.styles.custom import load_css
from frontend.components.sidebar import render_sidebar
from frontend.components.chat import render_chat
from frontend.components.memory import render_memory

# ========= BACKEND AUTO-WAKE FUNCTION =========
def wake_backend_service():
    """
    Auto-wake Render backend with retry logic and visual feedback.
    Returns True if backend is awake, False otherwise.
    """
    # Get backend URL from environment or use default
    BACKEND_URL = os.getenv("BACKEND_URL", "https://memory-persona-ai.onrender.com")
    HEALTH_ENDPOINT = f"{BACKEND_URL}/api/v1/health"
    
    MAX_ATTEMPTS = 8
    RETRY_DELAY = 8  # seconds
    
    # Create UI containers for status updates
    status_container = st.empty()
    progress_container = st.empty()
    
    for attempt in range(1, MAX_ATTEMPTS + 1):
        # Update status message
        status_container.info(
            f"☕ Waking up backend server... "
            f"Attempt {attempt}/{MAX_ATTEMPTS} "
            f"(first load takes ~60 seconds)"
        )
        
        # Update progress bar
        progress_container.progress(attempt / MAX_ATTEMPTS)
        
        # Check if backend is awake
        try:
            response = requests.get(HEALTH_ENDPOINT, timeout=10)
            if response.status_code == 200:
                status_container.success("✅ Backend is ready!")
                progress_container.empty()
                time.sleep(0.5)
                status_container.empty()
                return True
        except Exception as e:
            # Backend not responding yet, continue retrying
            pass
        
        # Wait before next retry (except on last attempt)
        if attempt < MAX_ATTEMPTS:
            time.sleep(RETRY_DELAY)
    
    # Failed to wake up
    status_container.error(
        "❌ Backend failed to start. Please refresh the page or try again later."
    )
    progress_container.empty()
    return False

# ========= END WAKE-UP FUNCTION =========

# Page Configuration
# Sets up the browser tab title and default layout width
st.set_page_config(
    page_title="Memory Persona AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom CSS
# Applies custom styling to the Streamlit app
load_css()

# Initialize Session State
# Stores global application state across re-runs
if "page" not in st.session_state:
    st.session_state.page = "Chat"  # Default landing page
if "user_id" not in st.session_state:
    st.session_state.user_id = "default_user"  # Default user for demo purposes

# ========= AUTO-WAKE BACKEND (RUNS ONCE PER SESSION) =========
if "backend_awake" not in st.session_state:
    st.session_state.backend_awake = wake_backend_service()
    
    # Stop app execution if backend failed to wake
    if not st.session_state.backend_awake:
        st.stop()
# ========= END AUTO-WAKE =========

# Initialize API Client
# Centralized client for making requests to the backend
api = APIClient()

# Render Sidebar
# Displays navigation and controls
with st.sidebar:
    render_sidebar()

# Main Content Routing
# Switches the main view based on the current page selection
if st.session_state.page == "Chat":
    render_chat(api)
elif st.session_state.page == "Memories":
    render_memory(api)
elif st.session_state.page == "Settings":
    st.title("Settings")
    st.info("Configuration options coming soon.")
