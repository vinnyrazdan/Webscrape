"""Manual browser demo for the Pluralsight Playwright proof-of-concept."""

from __future__ import annotations

import asyncio
import logging

from pluralsight_mcp.browser.manager import run_browser_demo

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


async def main() -> None:
    """Open a Pluralsight page in visible Chromium for manual inspection."""
    url = "https://app.pluralsight.com/library/courses/prompt-engineering-human-resources"
    final_url = await run_browser_demo(url)
    print(f"Opened: {final_url}")


if __name__ == "__main__":
    asyncio.run(main())
