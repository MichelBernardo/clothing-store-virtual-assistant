import streamlit as st
import uuid

from client.api_client import AssistantAPIClient
from components.components import render_sidebar, render_thought_process


# Page settings
st.set_page_config(page_title="AI Store", page_icon="🛒", layout="centered")

# Session State Initialization
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

# Intanciates the API client
api = AssistantAPIClient()


# 1. Renders sidebar
render_sidebar(api)

# 2. Renders the Messages History on the Main Screen 
st.title("Agentic AI-based Virtual Assistant")

for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    else:
        # If it is an IA Message, we check whether it is a thought or a final message
        if msg.get("type") == "thought":
            render_thought_process(msg["node"], msg["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(msg["content"])

# 3. User Input
if user_input := st.chat_input("Ex: I want to buy a pair of size 42 jeans..."):
    # Saves and displays the user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Prepares to receive the stream from the backend
    with st.spinner("Processing..."):
        
        # An empty placeholder that will be updated with the live steps 
        stream_placeholder = st.container()

        # Connects to the API and listens to the real-time stream
        for event in api.send_message(st.session_state.thread_id, user_input):
            
            if event["type"] == "thought":
                # Show the thinking process in real time
                with stream_placeholder:
                    render_thought_process(event["node"], event["content"])
                # Saves to the  state for when the page reload
                st.session_state.messages.append({"role": "assistant", "type": "thought", "node": event["node"], "content": event["content"]})
                
            elif event["type"] == "message":
                # Shows the agent final message 
                with stream_placeholder:
                    with st.chat_message("assistant"):
                        st.markdown(event["content"])
                # Saves to the state
                st.session_state.messages.append({"role": "assistant", "type": "message", "node": event["node"], "content": event["content"]})