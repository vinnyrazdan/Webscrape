"""Browser utilities for the Playwright proof-of-concept."""

from .authentication import AuthenticationRequiredError, get_auth_state_path, has_authentication_state
from .manager import BrowserManager

__all__ = [
    "AuthenticationRequiredError",
    "BrowserManager",
    "get_auth_state_path",
    "has_authentication_state",
]
