"""Playwright browser manager for the Pluralsight proof-of-concept."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

logger = logging.getLogger(__name__)


class BrowserManager:
    """Manage a visible Chromium browser instance for manual verification."""

    def __init__(self, *, headless: bool = False, slow_mo: int = 0, storage_state_path: str | Path | None = None) -> None:
        self.headless = headless
        self.slow_mo = slow_mo
        self.storage_state_path = Path(storage_state_path) if storage_state_path is not None else None
        self._playwright: Any | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None

    async def start(self) -> Browser:
        """Launch Chromium and create a new browser context."""
        logger.info("Starting browser")
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo,
        )
        self._context = await self._browser.new_context(viewport={"width": 1440, "height": 1200})
        logger.info("Browser started successfully")
        return self._browser

    async def start_persistent(self, user_data_dir: str | Path) -> BrowserContext:
        """Launch a persistent Playwright context for authenticated session reuse."""
        logger.info("Starting browser with persistent authentication state")
        self._playwright = await async_playwright().start()
        self._context = await self._playwright.chromium.launch_persistent_context(
            str(user_data_dir),
            headless=self.headless,
            viewport={"width": 1440, "height": 1200},
        )
        self._browser = self._context.browser
        logger.info("Persistent browser context started")
        return self._context

    async def save_session_state(self, file_path: str | Path) -> None:
        """Persist the authenticated browser state to disk without logging its contents."""
        if self._context is None:
            raise RuntimeError("Browser context is not available.")

        target = Path(file_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        await self._context.storage_state(path=str(target))
        logger.info("Authentication state saved")

    async def open_page(self, url: str) -> Page:
        """Open a page and navigate to the supplied URL."""
        if self._browser is None and self._context is None:
            raise RuntimeError("Browser has not been started. Call start() first.")

        if self._context is None:
            raise RuntimeError("Browser context is not available.")

        page = await self._context.new_page()
        logger.info("Opening Pluralsight page: %s", url)
        response = await page.goto(url, wait_until="load", timeout=60000)
        if response is not None and response.status >= 400:
            logger.warning("Page returned HTTP %s for %s", response.status, url)
        logger.info("Page ready: %s", page.url)
        return page

    async def close(self) -> None:
        """Close the browser and related resources cleanly."""
        if self._context is not None:
            await self._context.close()
            self._context = None

        if self._browser is not None:
            await self._browser.close()
            self._browser = None

        if self._playwright is not None:
            await self._playwright.stop()
            self._playwright = None

        logger.info("Browser closed cleanly")


async def run_browser_demo(url: str = "https://app.pluralsight.com/library/courses/prompt-engineering-human-resources") -> str:
    """Simple demonstration function for manual testing from VS Code."""
    manager = BrowserManager(headless=False)
    page = None
    try:
        await manager.start()
        page = await manager.open_page(url)
        logger.info("Current URL: %s", page.url)
        logger.info("Title: %s", await page.title())
        return page.url
    finally:
        await manager.close()
