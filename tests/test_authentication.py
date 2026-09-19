from __future__ import annotations

from pathlib import Path

import pytest

from pluralsight_mcp.browser.authentication import DEFAULT_AUTH_PATH, get_auth_state_path, has_authentication_state
from pluralsight_mcp.exceptions import AuthenticationRequiredError


def test_auth_state_path_defaults_to_expected_location() -> None:
    path = get_auth_state_path()

    assert path == DEFAULT_AUTH_PATH
    assert path.name == "pluralsight_state.json"


def test_auth_state_path_is_under_playwright_auth_directory() -> None:
    path = get_auth_state_path()

    assert path.parts[0] == "playwright"
    assert path.parts[1] == ".auth"


def test_has_authentication_state_returns_bool() -> None:
    assert isinstance(has_authentication_state(), bool)


def test_authentication_exception_is_defined() -> None:
    with pytest.raises(AuthenticationRequiredError):
        raise AuthenticationRequiredError("Session is no longer valid.")
