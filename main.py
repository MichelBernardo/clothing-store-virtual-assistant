import uuid
import asyncio

from src.mcp_clients.store_db_mcp_client import get_mcp_tools_context
from src.graph.workflow import build_store_virtual_assistant_workflow
from src.core.config import settings


print(f"DEBUG URL: {settings.mcp_server_url}")

async def main():
    # 1. Abre a sessão com o banco/MCP. Ela fica viva enquanto estivermos dentro deste bloco.
    async with get_mcp_tools_context() as mcp_tools:

        # 2. Constrói a IA injetando as ferramentas
        app = build_store_virtual_assistant_workflow(mcp_tools)
        nova_thread = str(uuid.uuid4())
        config = {"configurable": {"thread_id": nova_thread}}

        print("\n🤖 Virtual Store Assistant is ready! (Type 'exit' to quit)\n" + "-"*50)

        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ['exit', 'quit']:
                break

            print("\n🔍 [DEBUG] Iniciando processamento...")

            try:
                # 🟢 SUBSTITUÍMOS O .ainvoke PELO .astream
                async for event in app.astream(
                    {"messages": [("user", user_input)]}, 
                    config=config, 
                    stream_mode="updates"
                ):
                    # O event é um dicionário onde a chave é o nome do nó que acabou de rodar
                    for node_name, state_update in event.items():
                        print(f"  ➡️  Nó concluído: [{node_name}]")

                        # Se o nó gerou uma mensagem, a gente imprime
                        if "messages" in state_update:
                            ultima_msg = state_update["messages"][-1]

                            print(f"      Tipo: {type(ultima_msg).__name__}")
                            print(f"      Conteúdo: {ultima_msg.content}")

                            if getattr(ultima_msg, "tool_calls", None):
                                for tool_call in ultima_msg.tool_calls:
                                    print(f"      🔧 Tool: {tool_call['name']}")
                                    print(f"         Args: {tool_call['args']}")

            except Exception as e:
                print(f"\n❌ [ERRO] O fluxo quebrou com o erro: {e}")

# Roda o sistema
if __name__ == "__main__":
    asyncio.run(main())