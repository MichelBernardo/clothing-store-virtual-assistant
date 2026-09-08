import uuid
import asyncio

from src.mcp_clients.store_db_mcp_client import get_mcp_tools_context
from src.graph.workflow import build_store_virtual_assistant_workflow
from src.core.config import settings


print(f"DEBUG URL: {settings.mcp_server_url}")

async def main():
    # 1. Opens a MCP session. It remains active as long as we are within this block.
    async with get_mcp_tools_context() as mcp_tools:

        # 2. Builds the AI injecting the tools
        app = build_store_virtual_assistant_workflow(mcp_tools)
        nova_thread = str(uuid.uuid4())
        config = {"configurable": {"thread_id": nova_thread}}

        print("\n🤖 Virtual Store Assistant is ready! (Type 'exit' to quit)\n" + "-"*50)

        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ['exit', 'quit']:
                break

            print("\n🔍 [DEBUG] Starting processing...")

            try:
                async for event in app.astream(
                    {"messages": [("user", user_input)]}, 
                    config=config, 
                    stream_mode="updates"
                ):
                    # The event is a dictionary which the key is the name of the node that just ran
                    for node_name, state_update in event.items():
                        print(f"  ➡️  Node completed: [{node_name}]")

                        # If the node generated a message, it displays
                        if "messages" in state_update:
                            ultima_msg = state_update["messages"][-1]

                            print(f"      Type: {type(ultima_msg).__name__}")
                            print(f"      Content: {ultima_msg.content}")

                            if getattr(ultima_msg, "tool_calls", None):
                                for tool_call in ultima_msg.tool_calls:
                                    print(f"      🔧 Tool: {tool_call['name']}")
                                    print(f"         Args: {tool_call['args']}")

            except Exception as e:
                print(f"\n❌ [ERROR] The flow broke down due to the error: {e}")

# Runs the system
if __name__ == "__main__":
    asyncio.run(main())