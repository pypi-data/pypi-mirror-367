# FILE: boot/models/config.py
"""
Pydantic models for application settings, loaded from .env and CLI args.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, cast

from pydantic_settings import BaseSettings, SettingsConfigDict

from boot.errors import ConfigError


class AppSettings(BaseSettings):
    """
    Manages application settings, loading from environment variables and .env files.
    """

    # --- Core Settings ---
    provider: str = "openai"
    two_pass: bool = False
    build_pass: bool = False
    max_fix_attempts: int = 3
    http_timeout_seconds: int = 120
    output_dir: Path = Path("./generated_jobs")
    temperature: float | None = None

    # --- OpenAI Settings ---
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str = "https://api.openai.com/v1"

    # --- Gemini Settings ---
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-1.5-pro-latest"
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta"

    # --- Supabase Settings ---
    supabase_url: str = "https://fgcuyeytouwpsehhoisf.supabase.co"
    supabase_anon_key: str | None = None

    # Use the modern model_config dictionary to silence Pydantic V2 warnings
    model_config = SettingsConfigDict(
        env_prefix="SPEX_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        # Add this to handle both SPEX_ prefix and direct env vars
        case_sensitive=False,
    )

    def __init__(self, **kwargs: Any) -> None:
        """Custom init to handle environment variable loading."""
        super().__init__(**kwargs)
        # If supabase_anon_key is still None, try loading without prefix
        if self.supabase_anon_key is None:
            # Try loading directly from environment
            self.supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")

    def get_api_key(self) -> str:
        """Returns the API key for the currently configured provider."""
        key = getattr(self, f"{self.provider}_api_key", None)
        if not key:
            raise ConfigError(
                f"API key for provider '{self.provider}' is not set. "
                "Please set it via .env or --api-key."
            )
        return cast(str, key)

    def get_model(self) -> str:
        """Returns the model for the currently configured provider."""
        return cast(str, getattr(self, f"{self.provider}_model"))

    def get_base_url(self) -> str:
        """Returns the base URL for the currently configured provider."""
        return cast(str, getattr(self, f"{self.provider}_base_url"))


def get_settings(
    provider: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
    timeout: int | None = None,
    two_pass: bool | None = None,
    output_dir: Path | None = None,
    temperature: float | None = None,
    build_pass: bool | None = None,
) -> AppSettings:
    """
    Load base settings and apply any CLI overrides.
    """
    settings = AppSettings()

    # Apply overrides from CLI arguments if they are provided
    if provider:
        settings.provider = provider
    if two_pass is not None:
        settings.two_pass = two_pass
    if output_dir:
        settings.output_dir = output_dir
    if temperature is not None:
        settings.temperature = temperature
    if timeout is not None:
        settings.http_timeout_seconds = timeout
    if build_pass is not None:
        settings.build_pass = build_pass

    # Provider-dependent overrides
    if api_key:
        setattr(settings, f"{settings.provider}_api_key", api_key)
    if model:
        setattr(settings, f"{settings.provider}_model", model)

    return settings
