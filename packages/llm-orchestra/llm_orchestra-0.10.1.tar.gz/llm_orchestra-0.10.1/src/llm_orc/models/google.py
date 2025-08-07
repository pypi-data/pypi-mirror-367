"""Google Gemini model implementation."""

import asyncio
import time

from google import genai

from llm_orc.models.base import ModelInterface


class GeminiModel(ModelInterface):
    """Gemini model implementation."""

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash") -> None:
        super().__init__()
        self.api_key = api_key
        self.model_name = model
        self.client = genai.Client(api_key=api_key)

    @property
    def name(self) -> str:
        return f"gemini-{self.model_name}"

    async def generate_response(self, message: str, role_prompt: str) -> str:
        """Generate response using Gemini API."""
        start_time = time.time()
        prompt = f"{role_prompt}\n\nUser: {message}\nAssistant:"

        # Run in thread pool since Gemini doesn't have async support
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.models.generate_content(
                model=self.model_name, contents=prompt
            ),
        )

        duration_ms = int((time.time() - start_time) * 1000)

        # Estimate token usage for Gemini (rough approximation)
        estimated_input_tokens = len(prompt) // 4
        response_text = response.text or ""
        estimated_output_tokens = len(response_text) // 4

        # Estimate cost (simplified Gemini pricing)
        cost_per_input_token = 0.0000005  # $0.50 per million input tokens
        cost_per_output_token = 0.0000015  # $1.50 per million output tokens
        cost_usd = (estimated_input_tokens * cost_per_input_token) + (
            estimated_output_tokens * cost_per_output_token
        )

        self._record_usage(
            input_tokens=estimated_input_tokens,
            output_tokens=estimated_output_tokens,
            duration_ms=duration_ms,
            cost_usd=cost_usd,
            model_name=self.model_name,
        )

        return response_text
