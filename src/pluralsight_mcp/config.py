"""Configuration helpers for the Pluralsight MCP project."""

from __future__ import annotations

import os
from pathlib import Path


def get_project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).resolve().parents[2]


def get_env_value(name: str, default: str | None = None) -> str | None:
    """Read a value from environment variables."""
    return os.getenv(name, default)
