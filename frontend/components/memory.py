import streamlit as st
from frontend.assets.icons import Icons

def render_memory(api_client):
    """
    Render the Memory Dashboard interface.
    
    This function displays the user's stored memories (preferences, patterns, facts)
    and provides a tool for manual memory extraction from text.
    
    Args:
        api_client: The initialized API client instance.
    """
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
            <div style="color: #6C63FF;">{Icons.BRAIN}</div>
            <h1 style="margin: 0; font-size: 2rem;">Memory Core</h1>
        </div>
        <p style="color: #555; margin-bottom: 30px;">Insights extracted from your conversations.</p>
    """, unsafe_allow_html=True)
    
    # Tabs for View and Extract
    tab1, tab2 = st.tabs(["Dashboard", "Extraction Tool"])
    
    with tab1:
        col_header, col_btn = st.columns([6, 1])
        with col_btn:
            if st.button("Refresh", key="refresh_memory"):
                st.rerun()

        # Fetch Data from backend
        with st.spinner("Accessing Memory Core..."):
            result = api_client.get_memory(st.session_state.user_id)
        
        if result.get("status") == "success":
            data = result.get("data", {})
            
            if not data:
                st.info("No memory data found for this user yet. Use the Extraction Tool to analyze a conversation!")
            else:
                # Stats Row - Summary counts
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("Preferences", len(data.get('user_preferences', [])))
                with c2:
                    st.metric("Emotional Patterns", len(data.get('emotional_patterns', [])))
                with c3:
                    st.metric("Facts Stored", len(data.get('memorable_facts', [])))
                
                st.markdown("---")

                # Preferences Section
                st.markdown("### User Preferences")
                if data.get('user_preferences'):
                    cols = st.columns(2)
                    for i, pref in enumerate(data['user_preferences']):
                        with cols[i % 2]:
                            confidence = float(pref.get('confidence', 0))
                            # Custom card with confidence bar
                            st.markdown(f"""
                                <div class="card-container">
                                    <div style="color: #888; font-size: 0.75rem; text-transform: uppercase; margin-bottom: 4px;">{pref.get('category', 'General')}</div>
                                    <div style="font-weight: 600; font-size: 1rem; margin-bottom: 8px;">{pref.get('preference')}</div>
                                    <div style="display: flex; align-items: center; gap: 8px;">
                                        <div style="flex-grow: 1; height: 4px; background: #eee; border-radius: 2px;">
                                            <div style="width: {confidence*100}%; height: 100%; background: #6C63FF; border-radius: 2px;"></div>
                                        </div>
                                        <span style="font-size: 0.75rem; color: #666;">{int(confidence*100)}%</span>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("No preferences recorded yet.")

                # Emotional Patterns Section
                st.markdown("### Emotional Patterns")
                if data.get('emotional_patterns'):
                    for pattern in data['emotional_patterns']:
                        st.markdown(f"""
                            <div class="card-container" style="display: flex; justify-content: space-between; align-items: flex-start;">
                                <div>
                                    <div style="font-weight: 600; color: #E91E63; margin-bottom: 4px;">{pattern.get('pattern')}</div>
                                    <div style="color: #666; font-size: 0.9rem;">Trigger: <b>{pattern.get('trigger')}</b></div>
                                </div>
                                <span class="tone-tag">{pattern.get('frequency')}</span>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No emotional patterns detected.")
                
                # Memorable Facts Section
                st.markdown("### Memorable Facts")
                if data.get('memorable_facts'):
                    for fact in data['memorable_facts']:
                        st.markdown(f"""
                            <div class="card-container">
                                <div style="font-weight: 500;">{fact.get('fact')}</div>
                                <div style="margin-top: 6px; font-size: 0.8rem; color: #888;">
                                    Type: {fact.get('fact_type')} | Importance: {fact.get('importance')}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No facts stored.")
                
        else:
            # Handle error gracefully
            msg = result.get('message', 'Unknown error')
            if "404" in str(msg) or "not found" in str(msg).lower():
                 st.warning("No memory profile found for this user ID. Try extracting memories first.")
            else:
                st.error(f"Error fetching memory: {msg}")

    with tab2:
        st.markdown("### Manual Memory Extraction")
        st.markdown("Paste a conversation log below to extract insights.")
        
        conversation_text = st.text_area("Conversation Log", height=200, 
            placeholder="User: I love hiking on weekends.\nAssistant: That sounds fun! Where do you go?\nUser: Usually to the mountains. It helps me relax from work stress.")
        
        if st.button("Extract Memories", type="primary"):
            if not conversation_text:
                st.warning("Please enter some text.")
            else:
                # Parse text into messages format required by API
                messages = []
                lines = conversation_text.split('\n')
                for line in lines:
                    if line.strip():
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            role = "user" if parts[0].strip().lower() == "user" else "assistant"
                            content = parts[1].strip()
                            messages.append({"role": role, "content": content})
                        else:
                            # Fallback assume user if no prefix
                            messages.append({"role": "user", "content": line})
                
                with st.spinner("Analyzing conversation..."):
                    extract_res = api_client.extract_memory(messages, st.session_state.user_id)
                
                if extract_res.get("status") == "success":
                    st.success("Extraction Complete! Check the Dashboard tab to see updated memories.")
                    with st.expander("View Extraction Result"):
                        st.json(extract_res.get("data"))
                else:
                    st.error(f"Extraction failed: {extract_res.get('message')}")
