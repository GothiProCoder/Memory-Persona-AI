"""
Custom styling configuration for the Streamlit frontend.

This module provides functionality to load and inject custom CSS into the
Streamlit application to override default styles and create a branded look.
"""

import streamlit as st
import os

def load_css():
    """
    Load and inject custom CSS from the main.css file.
    
    Reads the content of 'main.css' located in the same directory and
    injects it into the Streamlit app using `st.markdown` with `unsafe_allow_html=True`.
    """
    css_file = os.path.join(os.path.dirname(__file__), "main.css")
    with open(css_file, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
