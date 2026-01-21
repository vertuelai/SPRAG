import streamlit as st
import requests
from typing import List, Dict
import uuid
import time

# Configuration
BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="ADIC SharePoint RAG",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS with animations and modern design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container with animated gradient */
    .main {
        background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #4facfe);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        padding: 2rem;
        min-height: 100vh;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Chat container with glassmorphism */
    .stChatFloatingInputContainer {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Sidebar with dark theme */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: rgba(255, 255, 255, 0.95) !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: rgba(255, 255, 255, 0.95) !important;
    }
    
    /* Animated title */
    h1 {
        color: white;
        font-weight: 700;
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.5), 0 0 40px rgba(102, 126, 234, 0.3);
        font-size: 3.5rem !important;
        margin-bottom: 1rem;
        animation: glow 2s ease-in-out infinite alternate;
        letter-spacing: -1px;
    }
    
    @keyframes glow {
        from { text-shadow: 0 0 20px rgba(255, 255, 255, 0.5), 0 0 40px rgba(102, 126, 234, 0.3); }
        to { text-shadow: 0 0 30px rgba(255, 255, 255, 0.8), 0 0 60px rgba(102, 126, 234, 0.5); }
    }
    
    /* Subtitle with typing effect style */
    .subtitle {
        color: rgba(255, 255, 255, 0.95);
        font-size: 1.3rem;
        margin-bottom: 2.5rem;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        font-weight: 300;
        letter-spacing: 0.5px;
    }
    
    /* Chat messages with modern cards */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .stChatMessage:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 50px rgba(102, 126, 234, 0.2);
    }
    
    /* Enhanced buttons with ripple effect */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 1rem 2.5rem;
        font-weight: 600;
        font-size: 1.05rem;
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .stButton>button:before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton>button:hover:before {
        width: 300px;
        height: 300px;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.6);
    }
    
    /* Slider with gradient track */
    .stSlider {
        padding: 1.5rem 0;
    }
    
    /* Expander with animation */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
        border-radius: 12px;
        font-weight: 600;
        padding: 1rem;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.25) 0%, rgba(118, 75, 162, 0.25) 100%);
        transform: scale(1.02);
    }
    
    /* Session info badges with glow */
    .info-badge {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%);
        padding: 0.75rem 1.25rem;
        border-radius: 12px;
        margin: 0.75rem 0;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
        transition: all 0.3s ease;
    }
    
    .info-badge:hover {
        transform: translateX(5px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Citation cards with enhanced styling */
    .citation-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .citation-card:hover {
        transform: translateX(10px);
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.15);
        border-left-width: 6px;
    }
    
    /* Loading spinner custom */
    .stSpinner > div {
        border-color: #667eea !important;
    }
    
    /* Input field styling */
    .stChatInputContainer input {
        border-radius: 15px;
        border: 2px solid rgba(102, 126, 234, 0.3);
        padding: 1rem;
        font-size: 1.05rem;
    }
    
    .stChatInputContainer input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Pulse animation for new messages */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    .new-message {
        animation: pulse 2s ease-in-out;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar with enhanced design
with st.sidebar:
    st.markdown("# 🤖 ADIC")
    st.markdown("# SharePoint RAG")
    st.markdown('<p style="font-size: 0.9rem; opacity: 0.8; margin-top: -1rem;">Your Intelligent Knowledge Assistant</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # New conversation button with icon
    if st.button("✨ New Conversation", use_container_width=True, key="new_conv"):
        st.session_state.conversation_id = None
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    
    top_k = st.slider(
        "📊 Max Results", 
        min_value=3, 
        max_value=10, 
        value=5, 
        help="Maximum number of documents to retrieve from SharePoint"
    )
    
    # Add temperature control for demo
    st.markdown("### 🎨 Advanced")
    show_sources = st.checkbox("📚 Auto-expand Sources", value=False, help="Automatically show source citations")
    
    st.markdown("---")
    st.markdown("### 📌 Session Info")
    st.markdown(f'''
    <div class="info-badge">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            👤 <strong>User:</strong> {st.session_state.user_id[:8]}...
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    if st.session_state.conversation_id:
        st.markdown(f'''
        <div class="info-badge">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                💬 <strong>Chat:</strong> {st.session_state.conversation_id[:8]}...
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Message counter
    if st.session_state.messages:
        msg_count = len(st.session_state.messages)
        st.markdown(f'''
        <div class="info-badge">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                💭 <strong>Messages:</strong> {msg_count}
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🎯 About")
    st.markdown("""
    <div style="font-size: 0.85rem; line-height: 1.6; opacity: 0.9;">
        <p><strong>ADIC SharePoint RAG</strong> uses advanced AI to search your organization's SharePoint documents and provide accurate, cited answers.</p>
        <p style="margin-top: 1rem;">
            <strong>Features:</strong><br/>
            • Semantic search across SharePoint<br/>
            • AI-powered answers with citations<br/>
            • Conversation memory<br/>
            • Source transparency
        </p>
    </div>
    """, unsafe_allow_html=True)

# Main chat interface with hero section
st.markdown("# 🤖 ADIC SharePoint RAG")
st.markdown('<p class="subtitle">💡 Ask anything about your organization\'s knowledge base and get instant, cited answers</p>', unsafe_allow_html=True)

# Add quick action chips
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("📋 Company Policies", use_container_width=True):
        st.session_state.quick_prompt = "What are our company policies?"
with col2:
    if st.button("🏥 Benefits Info", use_container_width=True):
        st.session_state.quick_prompt = "Tell me about employee benefits"
with col3:show_sources):
                for citation in message["citations"]:
                    citation_html = f"""
                    <div class="citation-card">
                        <div style="display: flex; align-items: start; gap: 1rem;">
                            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                        color: white; padding: 0.5rem 0.75rem; border-radius: 8px; 
                                        font-weight: bold; min-width: 40px; text-align: center;">
                                {citation['number']}
                            </div>
                            <div style="flex: 1;">
                                <a href="{citation['url']}" target="_blank" 
                                   style="color: #667eea; font-weight: 600; font-size: 1.05rem; 
prompt = st.chat_input("💭 Ask me anything about your SharePoint documents...")

# Handle quick prompts
if 'quick_prompt' in st.session_state and st.session_state.quick_prompt:
    prompt = st.session_state.quick_prompt
    st.session_state.quick_prompt = None

if promptdecoration: none; display: flex; align-items: center; gap: 0.5rem;">
                                    📄 {citation['title']}
                                    <span style="font-size: 0.8rem; opacity: 0.6;">↗</span>
                                </a>
                                <p style="color: #666; margin-top: 0.5rem; font-size: 0.95rem; line-height: 1.5;">
                                    {citation['snippet']}
                                </p>
                            </div>
                        </div

# Display chat messages
for message in st.session_state.messages:
    avatar = "🧑‍💼" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        
        # Show citations for assistant messages
        if message["role"] == "assistant" and message.get("citations"):
            with st.expander("📚 **View Sources & Citations**", expanded=False):
                for citation in message["citations"]:
                    citation_html = f"""
                    <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%); 
                                padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
                        <strong style="color: #667eea;">[{citation['number']}]</strong> 
                        <a href="{citation['url']}" target="_blank" style="color: #764ba2; font-weight: 600;">{citation['title']}</a>
                        <br><small style="color: #666;">{citation['snippet']}</small>
                    </div>
                    """
                    st.markdown(citation_html, unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Ask a question..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user", avatar="🧑‍💼"):
        st.markdown(prompt)
    
    # Query backend
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🔍 Searching knowledge base and analyzing..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/api/query",show_sources):
                        for citation in data["citations"]:
                            citation_html = f"""
                            <div class="citation-card">
                                <div style="display: flex; align-items: start; gap: 1rem;">
                                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                                color: white; padding: 0.5rem 0.75rem; border-radius: 8px; 
                                                font-weight: bold; min-width: 40px; text-align: center;">
                                        {citation['number']}
                                    </div>
                                    <div style="flex: 1;">
                                        <a href="{citation['url']}" target="_blank" 
                                           style="color: #667eea; font-weight: 600; font-size: 1.05rem; 
                                                  text-decoration: none; display: flex; align-items: center; gap: 0.5rem;">
                                            📄 {citation['title']}
                                            <span style="font-size: 0.8rem; opacity: 0.6;">↗</span>
                                        </a>
                                        <p style="color: #666; margin-top: 0.5rem; font-size: 0.95rem; line-height: 1.5;">
                                            {citation['snippet']}
                                        </p>
                                    </div>
                                </div
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Update conversation ID
                st.session_state.conversation_id = data["conversation_id"]
                
                # Display answer
                st.markdown(data["answer"])
                
                # Display citations
                if data["citations"]:
                    with st.expander("📚 **View Sources & Citations**", expanded=False):
                        for citation in data["citations"]:
                            citation_html = f"""
                            <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%); 
                                        padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
                                <strong style="color: #667eea;">[{citation['number']}]</strong> 
                                <a href="{citation['url']}" target="_blank" style="color: #764ba2; font-weight: 600;">{citation['title']}</a>
                                <br><small style="color: #666;">{citation['snippet']}</small>
                            </div>
                            """
                            st.markdown(citation_html, unsafe_allow_html=True)
                
                # Add to messages
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": data["answer"],
                    "citations": data["citations"]
                })
                
            except requests.exceptions.ConnectionError:
                st.error("🚫 **Connection Error**\\n\\nCannot connect to the backend server. Please ensure the API is running on port 8000.")
            except requests.exceptions.HTTPError as e:
                st.error(f"⚠️ **API Error**\\n\\n{e.response.text}")
            except Exception as e:
                st.error(f"❌ **Unexpected Error**\\n\\n{str(e)}")
