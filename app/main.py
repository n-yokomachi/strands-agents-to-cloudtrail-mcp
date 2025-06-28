import streamlit as st
import boto3
from strands import Agent
from strands.models import BedrockModel

# Unified Stack Version - Updated for clean deployment

st.set_page_config(page_title="Strands Agents Chat", page_icon="🤖", layout="wide")

st.title("🤖 Strands Agents with Claude 3.5 Sonnet v2")
st.markdown("*Powered by Amazon Bedrock*")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Create Bedrock session
@st.cache_resource
def create_agent():
    model = BedrockModel(
        model_id='apac.anthropic.claude-3-5-sonnet-20241022-v2:0',
        region_name='ap-northeast-1',
        temperature=0.7,
        max_tokens=4000
    )
    
    agent = Agent(
        model=model,
        system_prompt="You are a helpful AI assistant. Be concise and friendly."
    )
    
    return agent

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            agent = create_agent()
            response = agent(prompt)
            text = str(response)
            st.markdown(text)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": text})

# Sidebar
with st.sidebar:
    st.header("Settings")
    st.info("Model: Claude 3.5 Sonnet v2")
    st.info("Region: ap-northeast-1")
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("💡 **Note**: Make sure to set your AWS credentials and enable Bedrock model access!") 