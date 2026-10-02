"""Google Generative AI service for Gemini integration."""

import logging

import google.generativeai as genai
from fastapi import HTTPException, status

from ..config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Google Gemini API."""

    def __init__(self) -> None:
        """Initialize Gemini service with API key."""
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY is required")
        genai.configure(api_key=settings.google_api_key)
        self.model_name = settings.google_model
        self.model = genai.GenerativeModel(self.model_name)

    async def generate(
        self, prompt: str, system_prompt: str | None = None, max_tokens: int = 512
    ) -> str:
        """Generate content using Gemini model."""
        try:
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            response = self.model.generate_content(
                full_prompt, generation_config={"max_output_tokens": max_tokens}
            )
            return response.text or "No response generated."
        except Exception as exc:
            logger.exception("Gemini generation failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI generation failed: {exc}",
            ) from exc

    async def summarize(self, text: str, style: str = "concise") -> str:
        """Summarize text using Gemini."""
        if style == "bullet":
            instruction = "Summarize this text in a short bullet list."
        elif style == "detailed":
            instruction = "Provide a detailed summary with sections and key insights."
        else:
            instruction = "Provide a concise summary with key takeaways."

        return await self.generate(f"Text to summarize:\n{text}", instruction)
