from src.agents.specialist import SpecialistAgent


class PaymentAgent(SpecialistAgent):
    name = "Payment"
    allowed_tools = ["get_pending_orders", "process_payment"]
    
    system_prompt = """
    You are the Financial Agent.
    1. Check pending orders with 'get_pending_orders'.
    2. When the customer confirms the method (PIX or CREDIT_CARD), use 'process_payment'.
    Be direct and secure.
    """