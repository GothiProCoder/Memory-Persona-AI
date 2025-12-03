import streamlit as st
import importlib
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
st.set_page_config(
    page_title="Memory Persona AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom CSS
load_css()

# Initialize Session State
if "page" not in st.session_state:
    st.session_state.page = "Chat"
if "user_id" not in st.session_state:
    st.session_state.user_id = "default_user"

# Initialize API Client
api = APIClient()

# Render Sidebar
with st.sidebar:
    render_sidebar()

# Main Content Routing
if st.session_state.page == "Chat":
    render_chat(api)
elif st.session_state.page == "Memories":
    render_memory(api)
elif st.session_state.page == "Settings":
    st.title("Settings")
    st.info("Configuration options coming soon.")
