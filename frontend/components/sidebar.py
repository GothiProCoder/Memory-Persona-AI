import streamlit as st
from frontend.assets.icons import Icons

def render_sidebar():
    """
    Render the application sidebar.
    
    Displays the logo, navigation menu, and user profile information.
    Handles navigation state updates via buttons.
    """
    with st.sidebar:
        # Logo Area
        st.markdown(f"""
            <div class="logo-area">
                <div class="logo-icon">{Icons.LOGO}</div>
                <div class="logo-text">Memory Persona AI</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        st.markdown('<p style="color: #666; font-size: 0.8rem; padding-left: 10px; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px;">Menu</p>', unsafe_allow_html=True)
        
        # Using columns to create clickable areas effectively (simulating custom buttons)
        # Since we can't easily inject pure HTML click handlers that modify Streamlit state directly without components
        # We will use st.button but styled to be invisible or overlay
        
        # Chat Button
        chat_active = st.session_state.page == "Chat"
        if st.button("Chat", key="nav_chat", use_container_width=True, type="primary" if chat_active else "secondary"):
            st.session_state.page = "Chat"
            st.rerun()

        # Memories Button
        memories_active = st.session_state.page == "Memories"
        if st.button("Memory Dashboard", key="nav_memories", use_container_width=True, type="primary" if memories_active else "secondary"):
            st.session_state.page = "Memories"
            st.rerun()

        st.markdown("---")
        
        # User Profile Simulation
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 10px; padding: 10px; background: rgba(255,255,255,0.03); border-radius: 8px;">
                <div style="width: 32px; height: 32px; background: #6C63FF; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                    {Icons.USER}
                </div>
                <div>
                    <div style="font-weight: 600; font-size: 0.9rem;">User ID</div>
                    <div style="font-size: 0.75rem; color: #888;">{st.session_state.user_id}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # User ID Selector (Hidden or Small)
        # Allows simulating different users in the demo
        new_user_id = st.text_input("Change User ID", value=st.session_state.user_id, key="user_id_input")
        if new_user_id != st.session_state.user_id:
            st.session_state.user_id = new_user_id
            st.rerun()
