# boot/llm/providers/openai.py
"""Concrete implementation of the LLMProvider protocol for OpenAI models."""

from __future__ import annotations

from typing import Any

import httpx

from boot.errors import ConfigError, GenerationError
from boot.llm.types import (
    GenerationConfig,
    NormalizedResponse,
    ProviderCapabilities,
)


class OpenAIProvider:
    """An LLMProvider implementation for OpenAI's Chat Completions API."""

    name: str = "openai"
    capabilities: ProviderCapabilities = ProviderCapabilities(
        streaming=True, json_mode=True, tools=True
    )

    def __init__(self, api_key: str, base_url: str, model: str):
        """
        Initializes the OpenAI provider.

        Args:
            api_key: The OpenAI API key.
            base_url: The base URL for the OpenAI API.
            model: The default model name to use for requests.

        Raises:
            ConfigError: If the API key is not provided.
        """
        if not api_key:
            raise ConfigError("OpenAI API key is required.")
        self.api_key = api_key
        self.base_url = base_url
        self.default_model = model

    def _prepare_payload(self, cfg: GenerationConfig) -> dict[str, Any]:
        """Constructs the JSON payload for the OpenAI API."""
        return {
            "model": cfg.model,
            "messages": cfg.messages
            or [
                {
                    "role": "system",
                    "content": cfg.system_prompt or "You are a helpful assistant.",
                },
                {"role": "user", "content": cfg.prompt},
            ],
            "temperature": cfg.temperature,
        }

    def _parse_response(
        self, raw_data: dict[str, Any], model: str
    ) -> NormalizedResponse:
        """Parses the raw JSON response into a normalized format."""
        choices = raw_data.get("choices")
        if not isinstance(choices, list) or not choices:
            raise GenerationError(
                "Invalid OpenAI response: 'choices' missing or empty."
            )

        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            raise GenerationError(
                "Invalid OpenAI response: choice item is not an object."
            )

        message = first_choice.get("message")
        if not isinstance(message, dict):
            raise GenerationError(
                "Invalid OpenAI response: 'message' must be an object."
            )

        text = message.get("content")
        if not isinstance(text, str):
            raise GenerationError(
                "Invalid OpenAI response: 'content' must be a string."
            )

        usage = raw_data.get("usage", {})
        return NormalizedResponse(
            text=text,
            model=model,
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            finish_reason=first_choice.get("finish_reason"),
            provider_metadata=raw_data,
        )

    async def generate(self, cfg: GenerationConfig) -> NormalizedResponse:
        """Sends a request to OpenAI and returns a normalized response."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        url = f"{self.base_url}/chat/completions"
        payload = self._prepare_payload(cfg)
        timeout = httpx.Timeout(cfg.timeout_s)

        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                return self._parse_response(response.json(), cfg.model)
            except httpx.HTTPStatusError as e:
                body = e.response.text
                msg = f"OpenAI API request failed with status {e.response.status_code}: {body}"
                raise GenerationError(msg) from e
            except httpx.RequestError as e:
                raise GenerationError(f"OpenAI API request failed: {e}") from e
