"""Development script for manual Pluralsight authentication and session reuse."""

from __future__ import annotations

import asyncio
import logging

from pluralsight_mcp.browser.authentication import DEFAULT_URL, ensure_authenticated_session

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


async def main() -> None:
    """Open a visible browser for first-time login and save the session state."""
    print(f"Opening: {DEFAULT_URL}")
    await ensure_authenticated_session(DEFAULT_URL)
    print("Authentication workflow complete.")


if __name__ == "__main__":
    asyncio.run(main())
