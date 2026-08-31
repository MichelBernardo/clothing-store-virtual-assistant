from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from src.graph.state import AgentState
from src.agents.supervisor import SupervisorAgent
from src.agents.sales import SalesAgent
from src.agents.support import SupportAgent
from src.agents.payment import PaymentAgent
from src.graph.conditional_edges import router


def build_store_virtual_assistant_workflow(mcp_tools: list, checkpointer):
    workflow = StateGraph(AgentState)

    supervisor = SupervisorAgent()
    sales_agent = SalesAgent(mcp_tools)
    support_agent = SupportAgent(mcp_tools)
    payment_agent = PaymentAgent(mcp_tools)

    tool_node = ToolNode(mcp_tools)

    workflow.add_node("Supervisor", supervisor)
    workflow.add_node("Sales", sales_agent)
    workflow.add_node("Support", support_agent)
    workflow.add_node("Payment", payment_agent)
    workflow.add_node("Tools", tool_node)

    workflow.add_edge(START, "Supervisor")

    workflow.add_conditional_edges(
        "Supervisor",
        router,
        {
            "Sales": "Sales",
            "Support": "Support",
            "Payment": "Payment",
            "FINISH": END
        }
    )

    for agent_node in ["Sales", "Support", "Payment"]:
        workflow.add_conditional_edges(
            agent_node,
            tools_condition,
            {
                "tools": "Tools",
                END: "Supervisor"
            }
        )

    def route_from_tools(state: AgentState) -> str:
        return state.get("next_agent", "Supervisor")

    workflow.add_conditional_edges(
        "Tools",
        route_from_tools,
        {
            "Sales": "Sales",
            "Support": "Support",
            "Payment": "Payment",
            "Supervisor": "Supervisor"
        }
    )

    return workflow.compile(checkpointer=checkpointer)