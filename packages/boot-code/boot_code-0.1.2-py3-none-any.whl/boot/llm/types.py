# boot/llm/types.py
"""
This module defines the core data structures and interfaces for the LLM engine.

It includes:
- Configuration and response objects for normalized interaction.
- The LLMProvider protocol that all concrete provider implementations must adhere to.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass(frozen=True)
class GenerationConfig:
    """
    A comprehensive, provider-agnostic configuration for an LLM generation request.

    This object normalizes the various parameters that can be sent to an LLM,
    allowing the core service to remain unaware of provider-specific details.

    Attributes:
        prompt: The primary text prompt for the generation task.
        model: The specific model identifier to use (e.g., 'gpt-4o-mini').
        temperature: The sampling temperature (0.0 for deterministic output).
        timeout_s: Network timeout in seconds for the request.
        system_prompt: An optional system-level instruction for the model.
        messages: For chat-based models, a list of message dictionaries.
    """

    prompt: str
    model: str
    temperature: float = 0.1
    timeout_s: int = 120
    system_prompt: str | None = None
    messages: list[dict[str, Any]] | None = None


@dataclass(frozen=True)
class ProviderCapabilities:
    """
    Describes the features supported by a specific LLM provider.

    Attributes:
        streaming: Whether the provider supports response streaming.
        json_mode: Whether the provider can enforce JSON output.
        tools: Whether the provider supports function/tool calling.
    """

    streaming: bool = False
    json_mode: bool = False
    tools: bool = False


@dataclass(frozen=True)
class NormalizedResponse:
    """
    A standardized, provider-agnostic representation of an LLM's response.

    This ensures that the application layer receives a consistent data structure
    regardless of which backend provider was used.

    Attributes:
        text: The main text content of the response.
        model: The model that generated the response.
        input_tokens: The number of tokens in the input prompt.
        output_tokens: The number of tokens in the generated response.
        finish_reason: The reason the model stopped generating tokens.
        provider_metadata: A dictionary for any provider-specific metadata.
    """

    text: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    finish_reason: str | None = None
    provider_metadata: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class LLMProvider(Protocol):
    """
    A protocol defining the contract for all LLM provider implementations.

    This is the "Strategy" in the Strategy pattern. Each concrete provider class
    must implement this interface, allowing them to be used interchangeably by the
    LLMService.
    """

    name: str
    capabilities: ProviderCapabilities

    async def generate(self, cfg: GenerationConfig) -> NormalizedResponse:
        """
        Generates a response based on the provided configuration.

        Args:
            cfg: The generation configuration object.

        Returns:
            A normalized response object.

        Raises:
            GenerationError: If the API call fails or the response is invalid.
        """
        ...
