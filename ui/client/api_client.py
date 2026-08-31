import httpx
import json

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
        """Faz o streaming da resposta via Server-Sent Events (SSE)"""
        with httpx.stream("POST", f"{settings.api_url}/chat/{thread_id}", json={"message": message}, timeout=120.0) as response:
            for line in response.iter_lines():
                if line.startswith("data: "):
                    data_str = line[len("data: "):]
                    yield json.loads(data_str)