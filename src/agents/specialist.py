from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

from src.core.config import settings


class SpecialistAgent:
    name: str = "Specialist"
    system_prompt: str = ""
    allowed_tools: list[str] = []

    def __init__(self, all_mcp_tools: list):

        my_tools = [t for t in all_mcp_tools if t.name in self.allowed_tools]

        llm = ChatGroq(
            model=settings.model_name,
            api_key=settings.groq_api_key,
            temperature=0.2,
            timeout=360
        )

        if my_tools:
            self.llm_with_tools = llm.bind_tools(my_tools)
        else:
            self.llm_with_tools = llm

    def __call__(self, state: dict) -> dict:
        messages = [
            {
                "role": "system",
                "content": self.system_prompt
            }
        ] + state["messages"]

        response = self.llm_with_tools.invoke(messages)

        return {
            "messages": [response]
        }