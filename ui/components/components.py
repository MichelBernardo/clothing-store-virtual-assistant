import streamlit as st
import uuid


def render_sidebar(api_client):
    """Renders the side bar with the sessions history."""
    with st.sidebar:
        st.title("🛍️ Store Assistant")
        st.write("---")

        if st.button("New Conversation", use_container_width=True):
            st.session_state.thread_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.rerun()

        st.write("### Your Conversations")
        conversations = api_client.get_conversations()

        if not conversations:
            st.caption("No conversation yet")

        for conv in conversations:
            # Highlights the current conversation 
            is_active = (conv["id"] == st.session_state.get("thread_id"))
            btn_type = "primary" if is_active else "secondary"

            if st.button(f"💬 {conv['title']}", key=conv["id"], type=btn_type, use_container_width=True):
                st.session_state.thread_id = conv["id"]
                st.session_state.messages = []  # In production, we would look up the API history
                st.rerun()

def render_thought_process(node_name: str, content: str):
    """Renders the thought process in a subtle color and font (Markdown/HTML)."""
    html_thought = f"""
    <div style='background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 10px; border-left: 4px solid #4a90e2;'>
        <small style='color: #555; font-family: monospace;'>
            <b>🧠 [Thinking - {node_name}]:</b> {content}
        </small>
    </div>
    """
    st.markdown(html_thought, unsafe_allow_html=True)