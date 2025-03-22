import streamlit as st
import anthropic
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Claude Chat App",
    page_icon="🤖",
    layout="centered"
)

# Custom CSS for better appearance
st.markdown("""
<style>
    .chat-message {
        padding: 1.5rem; 
        border-radius: 0.5rem; 
        margin-bottom: 1rem; 
        display: flex;
        flex-direction: column;
        color: #000000;
    }
    .chat-message.user {
        background-color: #EFEFEF;
    }
    .chat-message.assistant {
        background-color: #E0F7FA;
    }
    .chat-message .message-content {
        display: flex;
        margin-top: 0.5rem;
    }
    .chat-message .avatar {
        width: 20%;
    }
    .chat-message .content {
        width: 80%;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "api_key_configured" not in st.session_state:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        st.session_state.api_key_configured = bool(api_key)
        st.session_state.api_key = api_key or ""

def display_message(role, content):
    """Display a message in the chat interface"""
    avatar = "👤" if role == "user" else "🤖"
    css_class = "user" if role == "user" else "assistant"
    
    message_html = f"""
    <div class="chat-message {css_class}">
        <div class="message-content">
            <div class="avatar">{avatar}</div>
            <div class="content">{content}</div>
        </div>
    </div>
    """
    st.markdown(message_html, unsafe_allow_html=True)

def main():
    initialize_session_state()
    
    st.title("💬 Chat with Claude")
    
    # API Key configuration section
    with st.sidebar:
        st.header("Configuration")
        api_key_input = st.text_input(
            "Enter Anthropic API Key", 
            value=st.session_state.api_key,
            type="password",
            help="Get your API key from https://console.anthropic.com/"
        )
        
        if api_key_input != st.session_state.api_key:
            st.session_state.api_key = api_key_input
            st.session_state.api_key_configured = bool(api_key_input)
        
        model_option = st.selectbox(
            "Select Claude Model",
            ["claude-3-7-sonnet-20250219", "claude-3-5-sonnet-20240229", "claude-3-opus-20240229", "claude-3-5-haiku-20240307"],
            index=0
        )
        
        max_tokens = st.slider("Max Tokens for Response", 100, 4000, 1000)
        
        if st.button("Clear Conversation"):
            st.session_state.messages = []
            st.rerun()
    
    # Display chat messages
    for message in st.session_state.messages:
        display_message(message["role"], message["content"])
    
    # Chat input
    user_input = st.chat_input("Type your message here...", disabled=not st.session_state.api_key_configured)
    
    if not st.session_state.api_key_configured:
        st.warning("Please configure your Anthropic API key in the sidebar")
    
    if user_input:
        # Add user message to state and display it
        st.session_state.messages.append({"role": "user", "content": user_input})
        display_message("user", user_input)
        
        try:
            # Create Anthropic client
            client = anthropic.Anthropic(api_key=st.session_state.api_key)
            
            with st.spinner("Claude is thinking..."):
                # Convert session messages to Anthropic format
                messages_for_api = [
                    {"role": msg["role"], "content": msg["content"]} 
                    for msg in st.session_state.messages
                ]
                
                # Get response from Claude
                response = client.messages.create(
                    model=model_option,
                    max_tokens=max_tokens,
                    messages=messages_for_api
                )
                
                assistant_message = response.content[0].text
                
                # Add assistant response to state and display it
                st.session_state.messages.append({"role": "assistant", "content": assistant_message})
                display_message("assistant", assistant_message)
                
        except Exception as e:
            st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()