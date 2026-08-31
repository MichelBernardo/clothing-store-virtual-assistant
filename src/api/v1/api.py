import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from src.core.config import settings
from src.mcp_clients.store_db_mcp_client import get_mcp_tools_context
from src.graph.workflow import build_store_virtual_assistant_workflow
from src.api.v1.endpoints.conversation import router as conversation_router
from src.core.db import init_db


app = FastAPI(title="Store Assistant API")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da API."""
    # 1. Cria a nossa tabela personalizada de sessões (se não existir)
    init_db()
    
    # 2. Abre o Pool de Conexões Assíncronas para o LangGraph
    connection_kwargs = {
            "autocommit": True,
            "prepare_threshold": 0,
        }

    async with AsyncConnectionPool(
        conninfo=settings.database_url, 
        max_size=20, 
        kwargs=connection_kwargs
    ) as pool:
        
        # 3. Prepara o Checkpointer e cria as tabelas do LangGraph (checkpoints, checkpoint_blobs...)
        checkpointer = AsyncPostgresSaver(pool)
        await checkpointer.setup()

        # 4. Inicia o MCP e anexa o grafo de IA ao estado global do FastAPI
        async with get_mcp_tools_context() as mcp_tools:
            
            app.state.workflow_app = build_store_virtual_assistant_workflow(mcp_tools, checkpointer)
            print("✅ API Backend Ready! LangGraph connected to MCP and PostgresSaver.")
            
            yield  # A API recebe requisições enquanto estiver neste yield

# Atribui o lifespan configurado
app.router.lifespan_context = lifespan

# Registra os seus endpoints
app.include_router(conversation_router, prefix=settings.api_base)