"""
Frontend application entry point.

This module initializes the Streamlit application, configuring the page layout,
styles, and session state. It routes to different application components based
on the selected page in the sidebar (Chat or Memories).
"""

import streamlit as st
import sys
import os

# Add the current directory to sys.path so we can import from frontend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from frontend.utils.api_client import APIClient
from frontend.styles.custom import load_css
from frontend.components.sidebar import render_sidebar
from frontend.components.chat import render_chat
from frontend.components.memory import render_memory

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
