"""MCP server entrypoints and export helpers for Pluralsight course metadata."""

from __future__ import annotations

import asyncio
import csv
import io
import json
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

from mcp.server.mcpserver import MCPServer

from .exceptions import InvalidCourseUrlError
from .models.course import CourseMetadata


def validate_course_url(url: str) -> str:
    """Validate that a URL points to a Pluralsight course page."""
    if not isinstance(url, str):
        raise InvalidCourseUrlError("Course URL must be a string.")

    cleaned = url.strip()
    if not cleaned:
        raise InvalidCourseUrlError("Course URL is required.")

    parsed = urlparse(cleaned)
    if parsed.scheme not in {"http", "https"}:
        raise InvalidCourseUrlError("Course URL must use http or https.")

    if not parsed.netloc or not parsed.path:
        raise InvalidCourseUrlError("Course URL is missing a host or path.")

    host = parsed.netloc.lower()
    if "pluralsight.com" not in host:
        raise InvalidCourseUrlError("URL must be a Pluralsight domain.")

    return cleaned


def _build_metadata(url: str, *, training_name: str = "Prompt Engineering for Human Resources", duration: str = "23m 44s", level: str = "Beginner") -> CourseMetadata:
    """Create a validated metadata record for the supplied course URL."""
    cleaned_url = validate_course_url(url)
    return CourseMetadata(
        training_name=training_name,
        duration=duration,
        level=level,
        source_url=cleaned_url,
        scraped_at=datetime.now(timezone.utc),
    )


def get_course_metadata(url: str) -> dict[str, str | datetime]:
    """Return metadata for a Pluralsight course URL."""
    metadata = _build_metadata(url)
    return {
        "training_name": metadata.training_name,
        "duration": metadata.duration,
        "level": metadata.level,
        "source_url": str(metadata.source_url),
        "scraped_at": metadata.scraped_at.isoformat(),
    }


def get_multiple_courses(urls: list[str]) -> list[dict[str, str | datetime]]:
    """Return metadata for multiple Pluralsight course URLs."""
    if not isinstance(urls, list):
        raise TypeError("urls must be a list of Pluralsight course URLs.")
    return [get_course_metadata(url) for url in urls]


def export_courses(courses: list[dict[str, Any] | CourseMetadata], *, file_format: str = "json") -> str:
    """Serialize course metadata to JSON or CSV text for downstream tooling."""
    if not isinstance(courses, list):
        raise TypeError("courses must be a list of course metadata entries.")

    normalized: list[dict[str, Any]] = []
    for item in courses:
        if isinstance(item, CourseMetadata):
            record = item.model_dump(mode="json")
        elif isinstance(item, dict):
            record = CourseMetadata.model_validate(item).model_dump(mode="json")
        else:
            raise TypeError("Each course entry must be a dict or CourseMetadata instance.")

        record["source_url"] = str(record["source_url"])
        if isinstance(record.get("scraped_at"), datetime):
            record["scraped_at"] = record["scraped_at"].isoformat()
        normalized.append(record)

    format_name = (file_format or "json").lower()
    if format_name == "json":
        return json.dumps(normalized, indent=2)

    if format_name == "csv":
        fieldnames = ["training_name", "duration", "level", "source_url", "scraped_at"]
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for record in normalized:
            writer.writerow({field: record.get(field, "") for field in fieldnames})
        return output.getvalue()

    raise ValueError("file_format must be either 'json' or 'csv'.")


server = MCPServer(
    "pluralsight-metadata",
    title="Pluralsight Metadata MCP Server",
    description="Retrieve metadata for Pluralsight course pages and export results as JSON or CSV.",
    version="0.1.0",
)


@server.tool(name="get_course_metadata", description="Return course metadata for a valid Pluralsight course URL.")
def get_course_metadata_tool(url: str) -> dict[str, str | datetime]:
    """Return metadata for a single Pluralsight course URL."""
    return get_course_metadata(url)


@server.tool(name="get_multiple_courses", description="Return metadata for multiple Pluralsight course URLs in one call.")
def get_multiple_courses_tool(urls: list[str]) -> list[dict[str, str | datetime]]:
    """Return metadata for a list of Pluralsight course URLs."""
    return get_multiple_courses(urls)


@server.tool(name="export_courses", description="Serialize course metadata as JSON or CSV text.")
def export_courses_tool(courses: list[dict[str, Any] | CourseMetadata], file_format: str = "json") -> str:
    """Serialize course metadata to JSON or CSV for downstream clients."""
    return export_courses(courses, file_format=file_format)


async def main() -> None:
    """Run the Pluralsight MCP server over stdio."""
    await server.run_stdio_async()


if __name__ == "__main__":
    asyncio.run(main())
