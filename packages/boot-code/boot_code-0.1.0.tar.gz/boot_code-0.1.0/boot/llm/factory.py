# boot/llm/factory.py
"""
Provider Factory for the LLM Engine.

This module contains the factory function responsible for instantiating the
correct LLM provider based on a given name. It uses a registry to map provider
names to their corresponding implementation classes.
"""

from __future__ import annotations

from typing import Any

from boot.errors import ConfigError
from boot.llm.providers.gemini import GeminiProvider
from boot.llm.providers.openai import OpenAIProvider
from boot.llm.types import LLMProvider

# The PROVIDER_REGISTRY acts as a central mapping from a string name
# to the actual provider class. To add a new provider, one would simply
# add a new entry to this dictionary.
PROVIDER_REGISTRY: dict[str, type[LLMProvider]] = {
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
}


def create_provider(name: str, **kwargs: Any) -> LLMProvider:
    """
    Instantiates and returns an LLM provider based on its registered name.

    This function looks up the provider's class in the registry and initializes
    it with the provided keyword arguments, such as API keys and model names.

    Args:
        name: The name of the provider to create (e.g., 'openai', 'gemini').
        **kwargs: Keyword arguments to be passed to the provider's constructor.

    Returns:
        An instance of the requested LLMProvider.

    Raises:
        ConfigError: If the requested provider name is not found in the registry.
    """
    provider_class = PROVIDER_REGISTRY.get(name)
    if not provider_class:
        raise ConfigError(
            f"Unknown LLM provider: '{name}'. "
            f"Available providers: {list(PROVIDER_REGISTRY.keys())}"
        )
    return provider_class(**kwargs)
