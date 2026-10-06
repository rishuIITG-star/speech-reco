from typing import Dict, Any

class BaseLLM:
    def __init__(self, model: str, temperature: float = 0.0):
        self.model = model
        self.temperature = temperature
        
    def generate(self, system_prompt: str, user_prompt: str, response_format: str = "json") -> str:
        raise NotImplementedError
