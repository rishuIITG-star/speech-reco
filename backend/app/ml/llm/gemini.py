import google.generativeai as genai
import google.api_core.exceptions
import json
import time
import logging
from .base import BaseLLM
from app.core.config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

class GeminiLLM(BaseLLM):
    def __init__(self, model: str, temperature: float = 0.0, fallbacks: list = None, forbidden_models: list = None):
        super().__init__(model, temperature)
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
        self.fallbacks = fallbacks or []
        self.forbidden_models = forbidden_models or []
            
    def generate(self, system_prompt: str, user_prompt: str, response_format: str = "json", schema=None) -> str:
        models_to_try = [self.model] + self.fallbacks
        
        last_error = None
        for current_model in models_to_try:
            if current_model in self.forbidden_models:
                continue
                
            self.model = current_model
            model = genai.GenerativeModel(self.model, system_instruction=system_prompt)
            
            config = genai.types.GenerationConfig(
                temperature=self.temperature,
                response_mime_type="application/json" if response_format == "json" else "text/plain",
                response_schema=schema if schema else None
            )
            
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    response = model.generate_content(user_prompt, generation_config=config)
                    return response.text
                except google.api_core.exceptions.ResourceExhausted as e:
                    error_msg = str(e)
                    if "limit: 0" in error_msg:
                        # Non-retryable
                        last_error = e
                        break
                    else:
                        # Ordinary 429
                        if attempt < max_attempts - 1:
                            time.sleep(2 ** attempt)
                            continue
                        else:
                            last_error = e
                            break
                except Exception as e:
                    last_error = e
                    break
                    
        logger.error(f"Full Google error: {str(last_error)}")
        raise RuntimeError("The language model is unavailable right now. Please try again in a few minutes.")
