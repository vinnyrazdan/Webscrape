"""Playwright authentication flow for a reusable Pluralsight session."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from playwright.async_api import async_playwright

from pluralsight_mcp.browser.manager import BrowserManager
from pluralsight_mcp.exceptions import AuthenticationRequiredError

logger = logging.getLogger(__name__)

DEFAULT_AUTH_PATH = Path("playwright") / ".auth" / "pluralsight_state.json"
DEFAULT_URL = "https://app.pluralsight.com/library/courses/prompt-engineering-human-resources"


def get_auth_state_path() -> Path:
    """Return the path used for the saved Playwright authentication state."""
    return DEFAULT_AUTH_PATH


def has_authentication_state() -> bool:
    """Return whether a saved authenticated state exists."""
    return get_auth_state_path().exists()


async def ensure_authenticated_session(url: str = DEFAULT_URL, *, force_login: bool = False) -> bool:
    """Ensure an authenticated session exists and is reused when available.

    Returns True when a valid session is available or was saved, and False when the user must log in manually.
    """
    auth_path = get_auth_state_path()
    auth_path.parent.mkdir(parents=True, exist_ok=True)

    if has_authentication_state() and not force_login:
        logger.info("Authentication state found")
        manager = BrowserManager(headless=False)
        try:
            await manager.start_persistent(auth_path.parent)
            page = await manager.open_page(url)
            if page.url and "login" not in page.url.lower():
                logger.info("Existing session reused")
                return True
            logger.warning("Authentication required")
            raise AuthenticationRequiredError("Saved authentication is missing or no longer valid.")
        except AuthenticationRequiredError:
            raise
        finally:
            await manager.close()

    logger.info("Authentication required")
    logger.info("Waiting for manual login")
    manager = BrowserManager(headless=False)
    page = None
    try:
        await manager.start()
        page = await manager.open_page(url)
        logger.info("Open the browser and complete the Pluralsight login manually.")
        await asyncio.to_thread(input, "Press Enter after you have successfully authenticated: ")
        await manager.save_session_state(auth_path)
        logger.info("Authentication state saved")
        return True
    finally:
        if page is not None:
            await page.close()
        await manager.close()


async def run_authentication_demo(url: str = DEFAULT_URL) -> bool:
    """Development helper for manual first-time authentication and session reuse."""
    try:
        return await ensure_authenticated_session(url)
    except AuthenticationRequiredError:
        logger.error("Authentication is required before using the project browser session.")
        raise
