import json
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage

from src.core.db import get_all_sessions, save_session


router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.get("/conversations")
def get_conversations():
    """Query the actual PostgreSQL database."""
    return get_all_sessions()

@router.post("/chat/{thread_id}")
async def chat_stream(thread_id: str, payload: ChatRequest, request: Request):
    """Receives the message and streaming it."""
    
    # Saves to PostgreSQL
    save_session(thread_id, f"Sessão: {thread_id[:6]}")

    # This retrieves the LangGraph from application state
    workflow_app = request.app.state.workflow_app

    async def event_generator():
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            async for event in workflow_app.astream(
                {"messages": [("user", payload.message)]}, 
                config=config, 
                stream_mode="updates"
            ):
                for node_name, state_update in event.items():
                    # 1. Always sends the thought to the hanging box
                    thought_data = {
                        "type": "thought",
                        "node": node_name,
                        "content": f"The node [{node_name}] processed the information..."
                    }
                    yield f"data: {json.dumps(thought_data)}\n\n"
                    
                    if "messages" in state_update:
                        msg = state_update["messages"][-1]
                        
                        # Converts the message to a dictionary securely 
                        if hasattr(msg, "model_dump"):
                            msg_data = msg.model_dump()
                        elif hasattr(msg, "dict"):
                            msg_data = msg.dict()
                        elif isinstance(msg, dict):
                            msg_data = msg
                        else:
                            msg_data = vars(msg)

                        msg_type = msg_data.get("type", "")
                        content = msg_data.get("content", "")

                        # Unpacks the text if it comes broken into blocks
                        if isinstance(content, list):
                            content = " ".join([str(c.get("text", "")) for c in content if isinstance(c, dict) and "text" in c])
                            
                        content = str(content).strip()
                        
                        if msg_type in ["ai", "chat"] and content:
                            msg_payload = {
                                "type": "message",
                                "node": node_name,
                                "content": content
                            }
                            yield f"data: {json.dumps(msg_payload)}\n\n"
                        
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/chat/{thread_id}/history")
async def get_chat_history(thread_id: str, request: Request):
    """Retrieves the message history of a thread directly from LangGraph."""
    app = request.app.state.workflow_app
    config = {"configurable": {"thread_id": thread_id}}
    
    state = await app.aget_state(config)
    
    chat_history = []
    
    if state and hasattr(state, "values") and "messages" in state.values:
        for msg in state.values["messages"]:
            
            # 1. Absolute extraction tatic: Converts any class to a dictionary
            if hasattr(msg, "model_dump"):
                msg_data = msg.model_dump()
            elif hasattr(msg, "dict"):
                msg_data = msg.dict()
            elif isinstance(msg, dict):
                msg_data = msg
            else:
                msg_data = vars(msg)
            
            # 2. Takes the type and the raw content
            msg_type = msg_data.get("type", "")
            content = msg_data.get("content", "")
            
            # 3. Unpacks the text if the AI sent it in blocks or lists
            if isinstance(content, list):
                text_parts = []
                for item in content:
                    if isinstance(item, str):
                        text_parts.append(item)
                    elif isinstance(item, dict) and "text" in item:
                        text_parts.append(item["text"])
                content = " ".join(text_parts)
                
            content = str(content).strip()
            
            # If the message is empty, we ignore it.
            if not content:
                continue
                
            # 4. Adds in the list with the correct role to the frontend
            if msg_type == "human":
                chat_history.append({"role": "user", "type": "message", "content": content})
            elif msg_type == "ai" or msg_type == "chat":
                chat_history.append({"role": "assistant", "type": "message", "content": content})
                
    return {"messages": chat_history}