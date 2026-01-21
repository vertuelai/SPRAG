import streamlit as st
import requests
from typing import List, Dict
import uuid

# Configuration
BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="M365 Knowledge Assistant",
    page_icon="💬",
    layout="wide"
)

# Initialize session state
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.title("M365 Knowledge Assistant")
    st.markdown("---")
    
    # New conversation button
    if st.button("➕ New Conversation", use_container_width=True):
        st.session_state.conversation_id = None
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("### Settings")
    
    site_filter = st.text_input(
        "SharePoint Site Filter (optional)",
        placeholder="https://contoso.sharepoint.com/sites/..."
    )
    
    top_k = st.slider("Max Results", min_value=3, max_value=10, value=5)
    
    st.markdown("---")
    st.markdown("**User ID:** `" + st.session_state.user_id[:8] + "...`")
    if st.session_state.conversation_id:
        st.markdown("**Conversation:** `" + st.session_state.conversation_id[:8] + "...`")

# Main chat interface
st.title("💬 M365 Knowledge Assistant")
st.markdown("Ask questions about your organization's knowledge in SharePoint and OneDrive")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Display citations if present
        if message.get("citations"):
            with st.expander("📚 Sources"):
                for citation in message["citations"]:
                    st.markdown(f"**[{citation['number']}] [{citation['title']}]({citation['url']})**")
                    st.caption(citation['snippet'])

# Chat input
if prompt := st.chat_input("Ask a question..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Show assistant thinking
    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base..."):
            try:
                # Call backend API
                response = requests.post(
                    f"{BACKEND_URL}/api/query",
                    json={
                        "query": prompt,
                        "conversation_id": st.session_state.conversation_id,
                        "user_id": st.session_state.user_id,
                        "site_filter": site_filter if site_filter else None,
                        "top_k": top_k
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Update conversation ID
                    st.session_state.conversation_id = result["conversation_id"]
                    
                    # Display answer
                    st.markdown(result["answer"])
                    
                    # Display citations
                    if result["citations"]:
                        with st.expander("📚 Sources"):
                            for citation in result["citations"]:
                                st.markdown(f"**[{citation['number']}] [{citation['title']}]({citation['url']})**")
                                st.caption(citation['snippet'])
                    
                    # Add to message history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result["answer"],
                        "citations": result["citations"]
                    })
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to connect to backend: {str(e)}")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")
