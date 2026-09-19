# Copilot Instructions
# Pluralsight Training Metadata MCP Server

## Project Objective

Build a Python MCP server that accesses an authorized Pluralsight
account through Playwright and extracts course metadata.

The initial metadata fields are:

1. Training Name
2. Duration
3. Level

Example:

{
    "training_name": "Prompt Engineering for Human Resources",
    "duration": "23m 44s",
    "level": "Beginner"
}

---

## Development Philosophy

Implement the project incrementally.

DO NOT build the entire application in one step.

Complete and test each phase before moving to the next phase.

The implementation order is:

Phase 1:
Python project setup

Phase 2:
Playwright browser proof of concept

Phase 3:
Authenticated browser session

Phase 4:
Course metadata extraction

Phase 5:
Robust scraper

Phase 6:
Data models and validation

Phase 7:
MCP server

Phase 8:
MCP tool integration

Phase 9:
Multiple-course support

Phase 10:
CSV/JSON export

Phase 11:
Testing

Phase 12:
Documentation

---

## Technology Stack

Python 3.13+

uv

Playwright

MCP Python SDK v2

Pydantic

pytest

python-dotenv

SQLite may be introduced later.

---

## Coding Standards

Use:

- type hints
- async/await where appropriate
- pathlib.Path
- Pydantic models
- environment variables
- structured logging
- meaningful exceptions
- small functions
- modular architecture

Avoid:

- hard-coded credentials
- hard-coded passwords
- global mutable state
- unnecessary dependencies
- giant functions
- duplicated browser logic

---

## Security Rules

NEVER hard-code:

- username
- password
- API keys
- cookies
- session tokens
- authentication state

Use environment variables where credentials are actually required.

Authenticated browser state must never be committed to Git.

Add authentication files to .gitignore.

Example:

playwright/.auth/
storage_state.json
.env

---

## Authentication

Prefer persistent Playwright browser state or an authorized
existing browser session.

Do not repeatedly automate login if an authenticated session
can safely be reused.

Support manual login when required by SSO/MFA.

---

## Scraping Rules

Do not depend on fragile CSS selectors if a stable semantic
selector is available.

Prefer:

- accessible roles
- labels
- semantic selectors
- stable attributes
- data-testid when available

Avoid:

- random generated class names
- nth-child selectors
- pixel coordinates

The scraper must fail gracefully when metadata cannot be found.

---

## Data Model

Use a Pydantic model similar to:

CourseMetadata

Fields:

training_name: str
duration: str
level: str
source_url: str
scraped_at: datetime

---

## MCP

Expose functionality through MCP tools.

Initial MCP tool:

get_course_metadata(url: str)

Later:

get_multiple_courses(urls: list[str])

export_courses(...)

MCP tools must have clear docstrings because their descriptions
are used by the AI client.

---

## Testing

Every major component should have tests.

At minimum:

- metadata model validation
- URL validation
- scraper parsing
- missing metadata handling
- MCP tool behavior

Do not require a live Pluralsight login for unit tests.

Use mocked/sample HTML where possible.

---

## Logging

Use Python logging.

Do not log:

- passwords
- cookies
- session tokens
- authorization headers
- authentication state contents

---

## Error Handling

Use specific exceptions.

Examples:

CoursePageLoadError
AuthenticationRequiredError
CourseMetadataNotFoundError
InvalidCourseUrlError

Never silently swallow exceptions.

---

## Project Structure

Prefer:

pluralsight-mcp/
│
├── src/
│   └── pluralsight_mcp/
│       ├── __init__.py
│       ├── server.py
│       ├── config.py
│       │
│       ├── browser/
│       │   ├── __init__.py
│       │   ├── manager.py
│       │   └── authentication.py
│       │
│       ├── scraper/
│       │   ├── __init__.py
│       │   ├── pluralsight.py
│       │   └── selectors.py
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   └── course.py
│       │
│       └── exceptions.py
│
├── tests/
│
├── playwright/
│   └── .auth/
│
├── .env
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
└── uv.lock

---

## Copilot Behaviour

Before modifying files:

1. Explain what will change.
2. Identify the files involved.
3. Make the smallest reasonable change.
4. Run or explain the relevant test.
5. Report the result.
6. Do not proceed to the next phase automatically.

If a website selector is unknown, inspect the page first rather
than guessing selectors.

If authentication is required, stop and ask the user to perform
manual authentication.

Never invent DOM selectors.

---

## Final Goal

The final MCP server should allow an AI client to execute:

get_course_metadata(
    "https://app.pluralsight.com/ilx/video-courses/..."
)

and receive structured data:

{
    "training_name": "...",
    "duration": "...",
    "level": "...",
    "source_url": "...",
    "scraped_at": "..."
}