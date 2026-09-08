import streamlit as st
import uuid

from client.api_client import AssistantAPIClient


# Page settings
st.set_page_config(page_title="AI Store", page_icon="🛒", layout="centered")

# Instanciates the API client
api = AssistantAPIClient()

# Session State Initialization
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []


# ==========================================
# 1. SIDEBAR
# ==========================================
with st.sidebar:
    st.title("Conversas")
    
    # Buttom to initiate a clean new conversation
    if st.button("➕ Nova Conversa", use_container_width=True):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    st.divider()
    
    # Lists the database sessions
    try:
        sessions_response = api.get_conversations()
        
        # Ensures that session is a list, independently of the API format
        if isinstance(sessions_response, dict):
            sessions = sessions_response.get("conversations", sessions_response.get("sessions", []))
        else:
            sessions = sessions_response

        if sessions:
            for index, session in enumerate(reversed(sessions)):
                if isinstance(session, dict):
                    t_id = session.get("id") or session.get("thread_id") or session.get("session_id")
                else:
                    t_id = session
                
                name = f"💬 Conversation {len(sessions) - index}"
                
                if t_id and st.button(name, key=t_id, use_container_width=True):
                    st.session_state.thread_id = t_id
                    st.session_state.messages = api.get_conversation_history(t_id)
                    st.rerun()
        else:
            st.info("No previous conversations.")
    except Exception as e:
        st.error(f"Error loading conversations: {str(e)}")


# ==========================================
# 2. MAIN SCREEN
# ==========================================
st.title("Clothing Store Virtual Assistant")

# Exhibits the messages in the main screen
for msg in st.session_state.messages:
    if msg.get("role") == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    elif msg.get("type") == "message" or msg.get("role") == "assistant":
        with st.chat_message("assistant"):
            st.markdown(msg["content"])
    elif msg.get("type") == "error":
        st.error(f"❌ Backend error: {msg['content']}")


# ==========================================
# 3. USER INTERACTION
# ==========================================
if user_input := st.chat_input("Ex: Quero comprar uma calça jeans slim tamanho 42..."):
    # Saves and displays the user message
    st.session_state.messages.append({"role": "user", "type": "message", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Initiates the assistant response block
    with st.chat_message("assistant"):
        
        status = st.status("🧠 Agents analyzing...", expanded=True)
        
        # We create an empty space below the status to fill with the final answer
        response_placeholder = st.empty()
        full_response = ""

        # Connects to the API and listens the streaming in real time
        for event in api.send_message(st.session_state.thread_id, user_input):
            
            if event["type"] == "thought":
                # Writes the step by step inside the minimizable box.
                status.write(f"🔄 **[{event['node']}]** processou informações.")
                
            elif event["type"] == "message":
                # Anti-Leak Filter: If the message if the database raw JSON, we ignore.
                if event["content"].startswith("[{") and "category" in event["content"]:
                    continue
                
                # Concatanates the answer and displays outside the box
                full_response += event["content"]
                response_placeholder.markdown(full_response)
            
            elif event["type"] == "error":
                status.error(f"Erro interno: {event['content']}")
                st.session_state.messages.append({"role": "assistant", "type": "error", "content": event["content"]})

        status.update(label="Raciocínio concluído", state="complete", expanded=False)
        
        # Saves the final response in the state
        if full_response:
            st.session_state.messages.append({"role": "assistant", "type": "message", "content": full_response})