# boot/llm/service.py
"""
The primary service for interacting with the LLM engine.

This module contains the LLMService class, which acts as the main entry point
for the rest of the application to make generation requests. It uses the factory
to create a provider and delegates the actual API calls to it.
"""

from __future__ import annotations

from boot.llm.factory import create_provider
from boot.llm.types import GenerationConfig, LLMProvider, NormalizedResponse
from boot.models.config import AppSettings


class LLMService:
    """
    Orchestrates LLM interactions through a provider-agnostic interface.

    This service uses the factory pattern to select the appropriate LLM provider
    at runtime based on application settings. It then delegates generation
    tasks to the selected provider.
    """

    def __init__(self, settings: AppSettings):
        """
        Initializes the LLMService with the appropriate provider.

        Args:
            settings: The application settings, which determine which provider
                      to use and provide necessary credentials.
        """
        self._provider: LLMProvider = create_provider(
            name=settings.provider,
            api_key=settings.get_api_key(),
            base_url=settings.get_base_url(),
            model=settings.get_model(),
        )

    async def generate(self, cfg: GenerationConfig) -> NormalizedResponse:
        """
        Performs a generation request using the configured provider.

        This method is the primary way the application should interact with the LLM.
        It abstracts away all provider-specific implementation details.

        Args:
            cfg: The generation configuration.

        Returns:
            A normalized response from the LLM provider.
        """
        # In a more advanced implementation, this is where cross-cutting
        # concerns like retries, circuit breakers, caching, and comprehensive
        # telemetry would be added.
        return await self._provider.generate(cfg)
