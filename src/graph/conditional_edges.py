from src.graph.state import AgentState


def router(state: AgentState) -> str:
    return state.get("next_agent", "FINISH")