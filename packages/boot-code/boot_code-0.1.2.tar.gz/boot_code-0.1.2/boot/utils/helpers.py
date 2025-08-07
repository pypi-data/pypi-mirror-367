# FILE: boot/utils/helpers.py
"""
This module provides utility functions for file system operations,
data loading, and other miscellaneous tasks.
"""

from __future__ import annotations

import re
import tomllib
from datetime import datetime
from pathlib import Path
from typing import Any, cast

import yaml

# Markers that define the project root
ROOT_MARKERS = (".git", "pyproject.toml")


def get_timestamp() -> str:
    """Returns a formatted timestamp string like '20250726-193000'."""
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def slugify(text: str) -> str:
    """
    Converts a string into a URL-friendly "slug".
    Example: "Subscription Attribution" -> "subscription-attribution"
    """
    # Replace invalid chars with a space first to prevent words from merging.
    text = re.sub(r"[^\w\s-]", " ", text.lower())
    # Then, collapse whitespace and dashes into a single dash.
    return re.sub(r"[\s-]+", "-", text).strip(" -")


def find_project_root(current_path: Path | None = None) -> Path:
    """
    Walk upward until a directory containing one of the root markers
    ('.git' or 'pyproject.toml') is found.
    """
    if current_path is None:
        current_path = Path.cwd()

    path = current_path.resolve()
    if path.is_file():
        path = path.parent

    while True:
        if any((path / marker).exists() for marker in ROOT_MARKERS):
            return path
        if path.parent == path:
            break
        path = path.parent

    raise FileNotFoundError(
        f"Could not find project root starting from: {current_path}"
    )


def get_user_configs_dir() -> Path:
    """Gets the user-specific configuration directory for Spex."""
    return Path.home() / ".config" / "boot"


def get_local_plugins_dir() -> Path:
    """
    Gets the local directory for storing managed plugins, ensuring it exists.
    e.g., ~/.boot/plugins
    """
    plugins_dir = Path.home() / ".boot" / "plugins"
    plugins_dir.mkdir(parents=True, exist_ok=True)
    return plugins_dir


def load_yaml_file(file_path: Path) -> dict[str, Any]:
    """
    Load a dictionary from a YAML or TOML file based on extension.
    Returns {} if the file doesn't exist or doesn't parse to a mapping.
    """
    if not file_path.exists():
        return {}

    if file_path.suffix.lower() == ".toml":
        return load_toml_file(file_path)

    with file_path.open("r", encoding="utf-8") as f:
        data: Any = yaml.safe_load(f)

    if data is None:
        return {}

    # YAML can legally be a list/scalar; only accept mappings
    if isinstance(data, dict):
        # Keys should be strings for our use; cast for mypy
        return cast(dict[str, Any], data)

    return {}


def load_toml_file(file_path: Path) -> dict[str, Any]:
    """Load a dictionary from a TOML file.
    Returns {} if not found."""
    if not file_path.exists():
        return {}

    with file_path.open("rb") as f:
        data = tomllib.load(f)
        return data


def get_template_files(templates_dir: Path) -> list[Path]:
    """Recursively list files in the given templates directory."""
    if not templates_dir.is_dir():
        return []
    return [p for p in templates_dir.rglob("*") if p.is_file()]
