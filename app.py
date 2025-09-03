import streamlit as st
import subprocess
import time
import os
from backend.agents.agents import create_agent
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
import threading
import requests
import sys

# Page configuration
st.set_page_config(
    page_title="Grievance Management Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better UI
st.markdown("""
<style>
    /* Main container styling */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 1rem 1.5rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: flex-start;
        animation: fadeIn 0.5s;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .chat-message.user {
        background-color: #007AFF;
        color: white;
        margin-left: 20%;
        border-bottom-right-radius: 0.3rem;
    }
    
    .chat-message.bot {
        background-color: #F1F3F4;
        color: #1F1F1F;
        margin-right: 20%;
        border-bottom-left-radius: 0.3rem;
    }
    
    .chat-message .avatar {
        font-size: 1.5rem;
        margin-right: 1rem;
        min-width: 2rem;
    }
    
    .chat-message .message {
        flex: 1;
        line-height: 1.5;
    }
    
    /* Welcome message styling */
    .welcome-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .welcome-container h2 {
        margin-bottom: 0.5rem;
        font-size: 2rem;
    }
    
    .welcome-container p {
        margin-bottom: 0;
        opacity: 0.95;
    }
    
    /* Quick action buttons */
    .quick-action-btn {
        background-color: white;
        border: 2px solid #E5E7EB;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem;
        cursor: pointer;
        transition: all 0.3s;
        text-align: center;
    }
    
    .quick-action-btn:hover {
        border-color: #007AFF;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 123, 255, 0.15);
    }
    
    /* Input form styling */
    .stForm {
        border: none !important;
        padding: 0 !important;
    }
    
    .stTextInput > div > div > input {
        border-radius: 2rem;
        padding: 0.75rem 1.5rem;
        border: 2px solid #E5E7EB;
        font-size: 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #007AFF;
        box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.1);
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 2rem;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Chat container */
    .chat-container {
        height: 500px;
        overflow-y: auto;
        padding: 1rem;
        background-color: #FAFAFA;
        border-radius: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Scrollbar styling */
    .chat-container::-webkit-scrollbar {
        width: 6px;
    }
    
    .chat-container::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    
    .chat-container::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 3px;
    }
    
    .chat-container::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
if "api_server_running" not in st.session_state:
    st.session_state.api_server_running = False
if "agent" not in st.session_state:
    st.session_state.agent = None
if "input_key" not in st.session_state:
    st.session_state.input_key = 0
if "show_welcome" not in st.session_state:
    st.session_state.show_welcome = True

def start_api_server():
    """Start the FastAPI server in the background"""
    if not st.session_state.api_server_running:
        try:
            response = requests.get("http://localhost:8000/docs")
            if response.status_code == 200:
                st.session_state.api_server_running = True
                return
        except:
            pass
        
        subprocess.Popen([sys.executable, "-m", "backend.api.api_server"])
        time.sleep(3)
        st.session_state.api_server_running = True

def get_chat_response(user_input):
    """Get response from the agent"""
    try:
        if st.session_state.agent is None:
            st.session_state.agent = create_agent()
        
        chat_history = st.session_state.memory.chat_memory.messages
        
        response = st.session_state.agent.invoke({
            "input": user_input,
            "chat_history": chat_history
        })
        
        st.session_state.memory.chat_memory.add_user_message(user_input)
        st.session_state.memory.chat_memory.add_ai_message(response["output"])
        
        return response["output"]
    except Exception as e:
        return f" Error: {str(e)}"

def display_message(msg, is_user=False):
    """Display a chat message"""
    message_class = "user" if is_user else "bot"
    avatar = "👤" if is_user else "🤖"
    
    st.markdown(f"""
    <div class="chat-message {message_class}">
        <div class="avatar">{avatar}</div>
        <div class="message">{msg}</div>
    </div>
    """, unsafe_allow_html=True)

def process_input(user_input):
    """Process user input and add to chat"""
    if user_input and user_input.strip():
        st.session_state.show_welcome = False
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.spinner("Bot is thinking..."):
            bot_response = get_chat_response(user_input)
        
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        st.session_state.input_key += 1

# Start API server automatically
if not st.session_state.api_server_running:
    with st.spinner("Starting services..."):
        start_api_server()
    st.rerun()

# Header
st.markdown("""
<div style='text-align: center; padding: 1rem 0;'>
    <h1 style='color: #1F1F1F; font-size: 2.5rem; margin-bottom: 0;'>
        Grievance Management Assistant
    </h1>
    <p style='color: #6B7280; font-size: 1.1rem;'>
        Your 24/7 complaint registration and tracking companion
    </p>
</div>
""", unsafe_allow_html=True)

# Main layout
col1, col2, col3 = st.columns([1, 6, 1])

with col2:
    # Welcome message
    if st.session_state.show_welcome and len(st.session_state.messages) == 0:
        st.markdown("""
        <div class="welcome-container">
            <h2>👋 Hello! How can I help you today?</h2>
            <p>I'm here to assist you with registering complaints and checking their status.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick action suggestions
        st.markdown("<h3 style='text-align: center; color: #374151; margin: 2rem 0 1rem 0;'>Quick Actions</h3>", unsafe_allow_html=True)
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            if st.button("📝 Register Complaint", use_container_width=True, key="quick_register"):
                process_input("I want to register a new complaint")
                st.rerun()
        
        with col_b:
            if st.button("📊 Check Status", use_container_width=True, key="quick_status"):
                process_input("I want to check my complaint status")
                st.rerun()
        
        with col_c:
            if st.button("📱 My Complaints", use_container_width=True, key="quick_list"):
                process_input("Show all my complaints")
                st.rerun()
    
    # Chat messages container
    if st.session_state.messages:
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.messages:
                display_message(msg["content"], msg["role"] == "user")
    
    # Spacer
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Input form
    with st.form(key='chat_form', clear_on_submit=True):
        col_input, col_send = st.columns([6, 1])
        
        with col_input:
            user_input = st.text_input(
                "Type your message...", 
                placeholder="E.g., 'I want to register a complaint about my laptop'",
                key=f"user_input_{st.session_state.input_key}",
                label_visibility="collapsed"
            )
        
        with col_send:
            submit_button = st.form_submit_button("Send ➤", type="primary", use_container_width=True)
        
        if submit_button and user_input:
            process_input(user_input)
            st.rerun()
    
    # Additional actions
        # Additional actions
    col_clear, col_help = st.columns([1, 1])
    
    with col_clear:
        if st.button("🔄 New Conversation", use_container_width=True, type="secondary"):
            st.session_state.messages = []
            st.session_state.memory.clear()
            st.session_state.input_key += 1
            st.session_state.show_welcome = True
            st.rerun()
    
    with col_help:
        # Use expander instead of popover
        with st.expander("ℹ️ Help", expanded=False):
            st.markdown("""
            **How to use this chatbot:**
            
            1. **Register a complaint:**
               - Click "Register Complaint" or type your request
               - Provide your name, mobile number, and complaint details
               - You'll receive a unique complaint ID
            
            2. **Check complaint status:**
               - Click "Check Status" or ask about your complaint
               - Provide your complaint ID (e.g., CMP-ABC12345)
            
            3. **View all complaints:**
               - Click "My Complaints" or ask to see all complaints
               - Provide your mobile number
            
            **Example messages:**
            - "I want to register a complaint about my laptop"
            - "Check status of CMP-ABC12345"
            - "Show all complaints for 9876543210"
            """)

# Sidebar with minimal info
with st.sidebar:
    st.markdown("### 🔧 System Status")
    if st.session_state.api_server_running:
        st.success("✅ Services Running")
    else:
        st.error("❌ Services Down")
        if st.button("Restart Services"):
            with st.spinner("Restarting..."):
                start_api_server()
            st.rerun()
    
    st.markdown("---")
    
    st.markdown("### 📊 Statistics")
    total_messages = len(st.session_state.messages)
    user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
    bot_messages = len([m for m in st.session_state.messages if m["role"] == "assistant"])
    
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.metric("User", user_messages)
    with col_stat2:
        st.metric("Bot", bot_messages)
    
    st.markdown("---")
    
    st.markdown("### 💡 Tips")
    st.info("""
    - Be specific with your complaints
    - Keep your complaint ID safe
    - Use your registered mobile number
    """)
    
    st.markdown("---")
    
    # About section
    with st.expander("ℹ️ About"):
        st.markdown("""
        **Grievance Management System v1.0**
        
        This AI-powered chatbot helps you:
        - Register complaints quickly
        - Track complaint status in real-time
        - View complaint history
        
        """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; padding: 1rem 0; color: #6B7280;'>
        <p style='margin: 0;'>Made with ❤️ | Grievance Management System v1.0</p>
        <p style='margin: 0; font-size: 0.9rem; opacity: 0.8;'>Powered by LangChain & MongoDB Atlas</p>
    </div>
    """,
    unsafe_allow_html=True
)