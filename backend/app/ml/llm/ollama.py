import requests
from .base import BaseLLM

class OllamaLLM(BaseLLM):
    def generate(self, system_prompt: str, user_prompt: str, response_format: str = "json") -> str:
        payload = {
            "model": self.model,
            "system": system_prompt,
            "prompt": user_prompt,
            "temperature": self.temperature,
            "format": response_format,
            "stream": False
        }
        try:
            resp = requests.post("http://localhost:11434/api/generate", json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            return data["response"]
        except Exception as e:
            raise RuntimeError(f"Ollama generation failed: {str(e)}")
