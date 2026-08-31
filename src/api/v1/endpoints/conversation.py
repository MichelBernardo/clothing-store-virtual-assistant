import json
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.core.db import get_all_sessions, save_session


router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.get("/conversations")
def get_conversations():
    """Consulta o banco de dados PostgreSQL real."""
    return get_all_sessions()

@router.post("/chat/{thread_id}")
async def chat_stream(thread_id: str, payload: ChatRequest, request: Request):
    """Recebe a mensagem e faz o streaming."""
    
    # Salva no PostgreSQL
    save_session(thread_id, f"Sessão: {thread_id[:6]}")

    # Recupera o LangGraph do estado da aplicação
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
                    thought_data = {
                        "type": "thought",
                        "node": node_name,
                        "content": f"O nó [{node_name}] processou a informação..."
                    }
                    yield f"data: {json.dumps(thought_data)}\n\n"
                    
                    if "messages" in state_update:
                        msg_content = state_update["messages"][-1].content
                        msg_data = {
                            "type": "message",
                            "node": node_name,
                            "content": msg_content
                        }
                        yield f"data: {json.dumps(msg_data)}\n\n"
                        
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")