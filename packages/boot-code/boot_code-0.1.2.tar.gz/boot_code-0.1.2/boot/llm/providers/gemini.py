# boot/llm/providers/gemini.py
"""Concrete implementation of the LLMProvider protocol for Google Gemini models."""

from __future__ import annotations

from typing import Any

import httpx

from boot.errors import ConfigError, GenerationError
from boot.llm.types import (
    GenerationConfig,
    NormalizedResponse,
    ProviderCapabilities,
)


class GeminiProvider:
    """An LLMProvider implementation for Google's Gemini API."""

    name: str = "gemini"
    capabilities: ProviderCapabilities = ProviderCapabilities(streaming=True)

    def __init__(self, api_key: str, base_url: str, model: str):
        """
        Initializes the Gemini provider.

        Args:
            api_key: The Gemini API key.
            base_url: The base URL for the Gemini API.
            model: The default model name to use for requests.

        Raises:
            ConfigError: If the API key is not provided.
        """
        if not api_key:
            raise ConfigError("Gemini API key is required.")
        self.api_key = api_key
        self.base_url = base_url
        self.default_model = model

    def _prepare_payload(self, cfg: GenerationConfig) -> dict[str, Any]:
        """Constructs the JSON payload for the Gemini API."""
        return {
            "contents": [{"parts": [{"text": cfg.prompt}]}],
            "generationConfig": {"temperature": cfg.temperature},
        }

    def _parse_response(
        self, raw_data: dict[str, Any], model: str
    ) -> NormalizedResponse:
        """Parses the raw JSON response into a normalized format."""
        candidates = raw_data.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            raise GenerationError(
                "Invalid Gemini response: 'candidates' missing or empty."
            )

        first_candidate = candidates[0]
        if not isinstance(first_candidate, dict):
            raise GenerationError(
                "Invalid Gemini response: candidate item is not an object."
            )

        content = first_candidate.get("content", {})
        parts = content.get("parts", [])
        if not parts:
            raise GenerationError("Invalid Gemini response: 'parts' missing or empty.")

        text = parts[0].get("text", "")
        if not isinstance(text, str):
            raise GenerationError("Invalid Gemini response: 'text' is not a string.")

        usage = raw_data.get("usageMetadata", {})
        return NormalizedResponse(
            text=text,
            model=model,
            input_tokens=usage.get("promptTokenCount", 0),
            output_tokens=usage.get("candidatesTokenCount", 0),
            finish_reason=first_candidate.get("finishReason"),
            provider_metadata=raw_data,
        )

    async def generate(self, cfg: GenerationConfig) -> NormalizedResponse:
        """Sends a request to Gemini and returns a normalized response."""
        url = f"{self.base_url}/models/{cfg.model}:generateContent?key={self.api_key}"
        payload = self._prepare_payload(cfg)
        timeout = httpx.Timeout(cfg.timeout_s)

        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return self._parse_response(response.json(), cfg.model)
            except httpx.HTTPStatusError as e:
                body = e.response.text
                msg = f"Gemini API request failed with status {e.response.status_code}: {body}"
                raise GenerationError(msg) from e
            except httpx.RequestError as e:
                raise GenerationError(f"Gemini API request failed: {e}") from e
