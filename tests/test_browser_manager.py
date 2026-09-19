from __future__ import annotations

import asyncio

import pytest

from pluralsight_mcp.browser.manager import BrowserManager


def test_browser_manager_initial_state() -> None:
    manager = BrowserManager(headless=False)

    assert manager.headless is False
    assert manager._playwright is None
    assert manager._browser is None
    assert manager._context is None


def test_browser_manager_has_expected_methods() -> None:
    manager = BrowserManager()

    assert hasattr(manager, "start")
    assert hasattr(manager, "open_page")
    assert hasattr(manager, "close")


def test_open_page_requires_started_browser() -> None:
    manager = BrowserManager()

    with pytest.raises(RuntimeError, match="Browser has not been started"):
        asyncio.run(manager.open_page("https://example.com"))
