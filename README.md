# Pluralsight Metadata MCP Server

This project provides the initial foundation for a Python MCP server that extracts course metadata from Pluralsight pages.

## Phase status

- Project scaffold is working.
- Playwright browser proof-of-concept is implemented.
- Authentication flow is in place.
- Course metadata extraction is working and validated.
- MCP server, multi-course tooling, and export helpers are implemented.

## MCP server usage

Run the server with:

```powershell
Set-Location "c:\Learning\2026 - Python Bootcamp\Experiments\Web_Scrapping_PluralSight"
.\.venv\Scripts\python.exe -m pluralsight_mcp.server
```

Available MCP tools:

- `get_course_metadata(url: str)`
- `get_multiple_courses(urls: list[str])`
- `export_courses(courses: list[dict], file_format: str = "json")`

## Setup

1. Create a virtual environment:
   `uv venv`

2. Install dependencies:
   `uv pip install --python .\.venv\Scripts\python.exe -e .[dev]`

3. Install Chromium for Playwright:
   `.\.venv\Scripts\python.exe -m playwright install chromium`

4. Run the tests:
   `.\.venv\Scripts\python.exe -m pytest -q`

## Phase 3: authenticated browser session

Authentication state is stored under:

`playwright/.auth/pluralsight_state.json`

This directory is ignored by Git via `.gitignore`.

### First-time login workflow

Run:

```powershell
Set-Location "c:\Learning\2026 - Python Bootcamp\Experiments\Web_Scrapping_PluralSight"
.\.venv\Scripts\python.exe demo_auth.py
```

Then:

1. A visible Chromium browser opens.
2. The Pluralsight page opens.
3. You log in manually using your normal SSO/MFA flow.
4. After successful login, press Enter in the terminal to save the session.
5. Browser closes and the authenticated state is saved.

### Existing session reuse

On later runs, the script detects the saved authentication state and reuses it instead of asking for login again.

### Manual integration path

For a manual browser-only check:

```powershell
Set-Location "c:\Learning\2026 - Python Bootcamp\Experiments\Web_Scrapping_PluralSight"
.\.venv\Scripts\python.exe -c "import asyncio; from pluralsight_mcp.browser.authentication import run_authentication_demo; asyncio.run(run_authentication_demo())"
```

### Notes

- No username, password, cookies, tokens, or auth headers are stored in source code.
- Authentication state is persisted only under `playwright/.auth/`.
- If the saved session is invalid, `AuthenticationRequiredError` is raised.
- This phase intentionally does not scrape metadata or expose selectors.
