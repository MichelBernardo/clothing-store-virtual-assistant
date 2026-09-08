import httpx
import json
import requests

from core.configs import settings


class AssistantAPIClient:
    @staticmethod
    def get_conversations():
        try:
            response = httpx.get(f"{settings.api_url}/conversations")
            return response.json()
        except Exception:
            return []

    @staticmethod
    def send_message(thread_id: str, message: str):
        """Does the response streaming via Server-Sent Events (SSE)"""
        with httpx.stream("POST", f"{settings.api_url}/chat/{thread_id}", json={"message": message}, timeout=120.0) as response:
            for line in response.iter_lines():
                if line.startswith("data: "):
                    data_str = line[len("data: "):]
                    yield json.loads(data_str)

    @staticmethod
    def get_conversation_history(thread_id: str):
        """Retrieves history in the FastAPI API"""
        url = f"{settings.api_url}/chat/{thread_id}/history" 
        
        try:
            import requests
            response = requests.get(url)
            if response.status_code == 200:
                return response.json().get("messages", [])
        except Exception as e:
            print(f"Error retrieving history in the backend: {e}")
        return []