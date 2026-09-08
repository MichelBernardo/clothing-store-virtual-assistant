from typing import Literal
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage

from src.core.config import settings


class Routing(BaseModel):
    next: Literal["Sales", "Support", "Payment", "FINISH"] = Field(
        description="The name of the next agent who should act, or FINISH if the task is complete."
    )

class SupervisorAgent:
    def __init__(self):
        llm = ChatGroq(
            model=settings.model_name,
            api_key=settings.groq_api_key,
            temperature=0.1,
            timeout=360
        )

        self.router_llm = llm.with_structured_output(Routing)

        system_prompt = """
            You are the Supervisor Agent of a Clothing Store Virtual Assistant.
            Your sole function is to read the conversation history and decide which specialized agent should act next.

            AGENT CAPABILITIES:
            - "Sales": Handles products, stock, creating orders, and REGISTERING new customers.
            - "Payment": Handles pending orders and processing payments.
            - "Support": Handles order tracking, returns, complaints, and general assistance.

            STRICT ROUTING RULES:
            Return EXACTLY one of these strings: "Sales", "Support", "Payment", or "FINISH".

            CRITICAL RULES:
            1. IF THE LAST MESSAGE WAS WRITTEN BY AN AI ASSISTANT, YOU MUST ROUTE TO "FINISH". This pauses the graph.
            2. ONLY route to a specialist if the LAST message is from the HUMAN USER.
            3. CONTINUITY (MOST IMPORTANT): Read the conversation history. If the user is answering a question asked by a specific agent (e.g., providing a name and phone because Sales asked for it), YOU MUST ROUTE BACK TO THAT SAME AGENT.
            4. NEVER chain agents together based on what another agent said.
        """

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("placeholder", "{messages}")
        ])

        self.chain = self.prompt | self.router_llm

    def __call__(self, state: dict) -> dict:
        """
        Processes the current state and returns the destiny.
        """
        ultima_mensagem = state["messages"][-1]
        if isinstance(ultima_mensagem, AIMessage):
            return {"next_agent": "FINISH"}

        routing_decision = self.chain.invoke({"messages": state["messages"]})

        return {
            "next_agent": routing_decision.next
        }