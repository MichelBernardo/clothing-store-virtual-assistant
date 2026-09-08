from contextlib import asynccontextmanager
from mcp.client.sse import sse_client
from mcp import ClientSession
from langchain_core.tools import StructuredTool

from pydantic import create_model, Field
from typing import Any

from src.core.config import settings


# Function to translate the MCP JSON Schema into a LangGraph Pydantic Model
def create_pydantic_model_from_schema(schema: dict, model_name: str):
    properties = schema.get("properties", {})
    required_fields = schema.get("required", [])
    
    fields = {}
    for key, value in properties.items():
        json_type = value.get("type", "string")
        
        # Maps JSON types to Python
        type_mapping = {
            "string": str, "integer": int, "number": float,
            "boolean": bool, "array": list, "object": dict
        }
        py_type = type_mapping.get(json_type, Any)
        description = value.get("description", "")
        
        # Defines whether the field is mandatory or optional
        if key in required_fields:
            fields[key] = (py_type, Field(..., description=description))
        else:
            fields[key] = (py_type, Field(None, description=description))
            
    # Creates a Pydantic class dinamically in execution time
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
            
            def create_langchain_tool(mcp_toll):
                async def executora_dinamica(**kwargs):
                    resultado = await session.call_tool(mcp_tool.name, arguments=kwargs)
                    return resultado.content[0].text
                
                # Injects the dynamci Pydantic schema into the tool
                dynamic_schema = create_pydantic_model_from_schema(
                    mcp_tool.inputSchema, 
                    model_name=f"{mcp_tool.name}Schema"
                )

                return StructuredTool.from_function(
                    coroutine=executora_dinamica,
                    name=mcp_tool.name,
                    description=mcp_tool.description,
                    args_schema=dynamic_schema
                )

            for mcp_tool in tools_response.tools:
                langchain_tools.append(create_langchain_tool(mcp_tool))
                print(f"    -> Tool wrapped: {mcp_tool.name}")

            yield langchain_tools