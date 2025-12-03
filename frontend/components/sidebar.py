import streamlit as st
from frontend.assets.icons import Icons

def render_sidebar():
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
        
        # Actually, standard st.buttons are robust. Let's use them but we might struggle with styling them exactly like the CSS .nav-item
        # Alternative: Use radio button hidden and styled? No.
        # Let's use standard st.buttons for navigation for simplicity and reliability, 
        # but wrapping them or styling them might be tricky.
        # A common pattern is using a visually pleasing radio or selectbox, or just buttons.
        
        # Let's try to make buttons look like nav items.
        
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

        # Settings Button
        settings_active = st.session_state.page == "Settings"
        if st.button("Settings", key="nav_settings", use_container_width=True, type="primary" if settings_active else "secondary"):
            st.session_state.page = "Settings"
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
        new_user_id = st.text_input("Change User ID", value=st.session_state.user_id, key="user_id_input")
        if new_user_id != st.session_state.user_id:
            st.session_state.user_id = new_user_id
            st.rerun()
