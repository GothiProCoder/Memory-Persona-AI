import streamlit as st
from frontend.assets.icons import Icons

def render_chat(api_client):
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
            <div style="color: #6C63FF;">{Icons.CHAT}</div>
            <h1 style="margin: 0; font-size: 2rem;">Personality Lab</h1>
        </div>
        <p style="color: #555; margin-bottom: 30px;">See how different personalities respond to your thoughts.</p>
    """, unsafe_allow_html=True)

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Input Area
    with st.container():
        query = st.chat_input("Say something...")
        
        if query:
            # 1. Show Original Input (The "Before" State)
            st.markdown("### 1. Original Input")
            st.info(query)

            # 2. Show Context (Memories Used)
            # Fetch memory to display context
            with st.spinner("Retrieving Context..."):
                mem_res = api_client.get_memory(st.session_state.user_id)
            
            st.markdown("### 2. Memory Context Applied")
            if mem_res.get("status") == "success" and mem_res.get("data"):
                data = mem_res.get("data", {})
                
                # Extract top items to simulate backend logic
                prefs = [p['preference'] for p in data.get('user_preferences', [])[:3]]
                facts = [f['fact'] for f in data.get('memorable_facts', [])[:2]]
                
                if prefs or facts:
                    with st.expander("View Active Memories", expanded=True):
                        if prefs:
                            st.caption("Preferences:")
                            for p in prefs:
                                st.markdown(f"- {p}")
                        if facts:
                            st.caption("Key Facts:")
                            for f in facts:
                                st.markdown(f"- {f}")
                else:
                    st.caption("No relevant memories found to influence response.")
            else:
                st.caption("No memory context available.")

            # === BEFORE SECTION - GENERIC RESPONSE ===
            # st.markdown("---")
            st.markdown("""
            <div style="margin: 32px 0 24px 0;">
                <h2 style="font-size: 1.5rem; font-weight: 700; color: #31333F; margin: 0 0 8px 0;">
                    Generic Response (No Personalization)
                </h2>
                <p style="color: #555555; font-size: 0.95rem; margin: 0; font-weight: 500;">
                    This is how a standard AI responds without your memories or personality preferences.
                </p>
            </div>
            """, unsafe_allow_html=True)

            with st.spinner("Generating generic response..."):
                generic_result = api_client.get_generic_response(query, st.session_state.user_id)

            if generic_result.get("status") == "success":
                generic_response = generic_result.get("generic_response", "")
                
                st.markdown(f"""
                <div class="card-container" style="border-top: 4px solid #9CA3AF; background: linear-gradient(135deg, #FFFFFF 0%, #F9FAFB 100%);">
                    <div style="font-size: 1rem; line-height: 1.6; color: #555555; margin-bottom: 16px;">
                        {generic_response}
                    </div>
                    <div class="tone-tags" style="margin-top: 16px;">
                        <span class="tone-tag">Generic Tone</span>
                        <span class="tone-tag">No Memory Context</span>
                        <span class="tone-tag">Standard Response</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error(f"Generic response error: {generic_result.get('message')}")

            # st.markdown("---")

            
            # 3. Personalized Responses (The "After" State)
            st.markdown("### 3. Personalized Responses")
            
            # Fetch Response
            with st.spinner("Generating Personalities..."):
                result = api_client.transform_personality(query, st.session_state.user_id)
            
            if result.get("status") == "success":
                responses = result.get("responses", {})
                
                # Layout: 3 Columns
                col1, col2, col3 = st.columns(3)
                
                # Mentor
                with col1:
                    mentor_resp = responses.get("mentor", {})
                    if mentor_resp:
                        render_personality_card(
                            "Mentor", 
                            mentor_resp.get("response", ""), 
                            mentor_resp.get("tone_characteristics", []),
                            Icons.MENTOR,
                            "mentor-border"
                        )
                
                # Friend
                with col2:
                    friend_resp = responses.get("friend", {})
                    if friend_resp:
                        render_personality_card(
                            "Friend", 
                            friend_resp.get("response", ""), 
                            friend_resp.get("tone_characteristics", []),
                            Icons.FRIEND,
                            "friend-border"
                        )
                
                # Therapist
                with col3:
                    therapist_resp = responses.get("therapist", {})
                    if therapist_resp:
                        render_personality_card(
                            "Therapist", 
                            therapist_resp.get("response", ""), 
                            therapist_resp.get("tone_characteristics", []),
                            Icons.THERAPIST,
                            "therapist-border"
                        )
                
                # Analysis Section
                st.markdown("---")
                st.markdown("### Analysis")
                st.success(result.get("analysis", "No analysis available."))
                
            else:
                st.error(f"Error: {result.get('message', 'Unknown error')}")


def render_personality_card(title, content, tags, icon, border_class):
    tags_html = "".join([f'<span class="tone-tag">{tag}</span>' for tag in tags])
    
    st.markdown(f"""
        <div class="card-container personality-card {border_class}">
            <div class="card-title">
                {icon}
                <span>{title}</span>
            </div>
            <div class="card-content">
                {content}
            </div>
            <div class="tone-tags">
                {tags_html}
            </div>
        </div>
    """, unsafe_allow_html=True)
