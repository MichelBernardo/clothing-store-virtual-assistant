from contextlib import asynccontextmanager
from mcp.client.sse import sse_client
from mcp import ClientSession
from langchain_core.tools import StructuredTool

# Novos imports para criar o modelo dinâmico
from pydantic import create_model, Field
from typing import Any

from src.core.config import settings


# Função para traduzir o JSON Schema do MCP para um Pydantic Model do LangChain
def create_pydantic_model_from_schema(schema: dict, model_name: str):
    properties = schema.get("properties", {})
    required_fields = schema.get("required", [])
    
    fields = {}
    for key, value in properties.items():
        json_type = value.get("type", "string")
        
        # Mapeia tipos JSON para Python
        type_mapping = {
            "string": str, "integer": int, "number": float,
            "boolean": bool, "array": list, "object": dict
        }
        py_type = type_mapping.get(json_type, Any)
        description = value.get("description", "")
        
        # Define se o campo é obrigatório (...) ou opcional (None)
        if key in required_fields:
            fields[key] = (py_type, Field(..., description=description))
        else:
            fields[key] = (py_type, Field(None, description=description))
            
    # Cria uma classe Pydantic dinamicamente em tempo de execução
    return create_model(model_name, **fields)


@asynccontextmanager
async def get_mcp_tools_context():
    print(f"Connecting to the MCP server at {settings.mcp_server_url} via SSE...")

    async with sse_client(settings.mcp_server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("MCP Connection via SSE successfully established!\n")

            print("Consulting tools...")
            tools_response = await session.list_tools()
            
            langchain_tools = []
            
            def criar_ferramenta_langchain(mcp_tool):
                async def executora_dinamica(**kwargs): # Removemos o *args
                    resultado = await session.call_tool(mcp_tool.name, arguments=kwargs)
                    return resultado.content[0].text
                
                # Injeta o schema Pydantic dinâmico na ferramenta
                dynamic_schema = create_pydantic_model_from_schema(
                    mcp_tool.inputSchema, 
                    model_name=f"{mcp_tool.name}Schema"
                )

                return StructuredTool.from_function(
                    coroutine=executora_dinamica,
                    name=mcp_tool.name,
                    description=mcp_tool.description,
                    args_schema=dynamic_schema # A mágica acontece aqui!
                )

            for mcp_tool in tools_response.tools:
                langchain_tools.append(criar_ferramenta_langchain(mcp_tool))
                print(f"    -> Tool wrapped: {mcp_tool.name}")

            yield langchain_tools