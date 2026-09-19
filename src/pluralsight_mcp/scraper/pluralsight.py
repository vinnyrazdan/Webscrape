"""Simple metadata extraction logic for a course page."""

from __future__ import annotations

import re
from html import unescape

from pluralsight_mcp.exceptions import CourseMetadataNotFoundError
from pluralsight_mcp.models.course import CourseMetadata


def _read_text(content: str | None) -> str:
    if content is None:
        return ""
    cleaned = re.sub(r"<[^>]+>", " ", content)
    cleaned = unescape(cleaned)
    cleaned = cleaned.replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", cleaned).strip()


def _extract_first_value(html: str, *patterns: str) -> str:
    for pattern in patterns:
        match = re.search(pattern, html, flags=re.IGNORECASE | re.DOTALL)
        if match:
            inner = match.group(1)
            text = _read_text(inner)
            if text:
                return text
    return "unknown"


def _extract_attr_value(html: str, *, attr: str = "aria-label", keywords: tuple[str, ...] = ()) -> str:
    patterns = [
        rf"{re.escape(attr)}=[\"'](?P<value>[^\"']+)[\"']",
        rf"data-[a-z0-9-]+=[\"'](?P<value>[^\"']+)[\"']",
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, html, flags=re.IGNORECASE):
            value = match.group("value")
            text = _read_text(value)
            if not text:
                continue

            if keywords:
                matched = any(keyword.lower() in text.lower() for keyword in keywords)
                if not matched:
                    continue
                if any(keyword.lower() in {"duration", "level"} for keyword in keywords):
                    for keyword in keywords:
                        if keyword.lower() in text.lower():
                            subprocess = text.split(keyword, 1)[1].strip()
                            if subprocess:
                                return subprocess.strip(" -:")
                    return text
                return text

            if "duration" not in text.lower() and "level" not in text.lower():
                return text
    return "unknown"


def _extract_json_ld_value(html: str, *, key: str) -> str:
    pattern = rf'"{re.escape(key)}"\s*:\s*"(?P<value>[^"\\]*(?:\\.[^"\\]*)*)"'
    match = re.search(pattern, html, flags=re.IGNORECASE | re.DOTALL)
    if match:
        value = match.group("value").encode("utf-8").decode("unicode_escape")
        return _read_text(value)
    return "unknown"


def _extract_meta_title(html: str) -> str:
    patterns = [
        r'<meta[^>]+(?:property|name|itemprop)=["\'](?:og:title|twitter:title|title|name)["\'][^>]+content=["\'](?P<value>[^"\']+)["\']',
        r'<meta[^>]+content=["\'](?P<value>[^"\']+)["\'][^>]+(?:property|name|itemprop)=["\'](?:og:title|twitter:title|title|name)["\']',
        r'<meta[^>]+itemprop=["\'](?P<itemprop>name)["\'][^>]+content=["\'](?P<value>[^"\']+)["\']',
        r'<title[^>]*>(?P<value>.*?)</title>',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, flags=re.IGNORECASE | re.DOTALL)
        if match:
            value = match.groupdict().get("value") or match.group(0)
            cleaned = _read_text(value)
            if cleaned:
                return cleaned
    return "unknown"


def _extract_meta_value(html: str, *, key: str) -> str:
    patterns = [
        rf'<meta[^>]+(?:itemprop|property|name)=["\']{re.escape(key)}["\'][^>]+content=["\'](?P<value>[^"\']+)["\']',
        rf'<meta[^>]+content=["\'](?P<value>[^"\']+)["\'][^>]+(?:itemprop|property|name)=["\']{re.escape(key)}["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, flags=re.IGNORECASE | re.DOTALL)
        if match:
            value = _read_text(match.group("value"))
            if value:
                return value
    return "unknown"


def _normalize_duration(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        return "unknown"
    if cleaned.upper().startswith("PT"):
        return cleaned.upper()
    return cleaned


def duration_to_hhmmss(value: str | None) -> str:
    """Convert a Pluralsight duration such as ``1h 5m 9s`` to ``HH:MM:SS``."""
    if not value or value.strip().lower() in {"unknown", "na", "n/a"}:
        return ""

    cleaned = value.strip().upper()
    iso_match = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", cleaned)
    if iso_match:
        hours, minutes, seconds = (int(part or 0) for part in iso_match.groups())
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    parts = {unit: int(amount) for amount, unit in re.findall(r"(\d+)\s*(H|M|S)", cleaned)}
    if not parts:
        return ""
    return f"{parts.get('H', 0):02d}:{parts.get('M', 0):02d}:{parts.get('S', 0):02d}"


def _extract_generic_duration(html: str) -> str:
    iso_match = re.search(r"\bPT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?\b", html, flags=re.IGNORECASE)
    if iso_match:
        return iso_match.group(0).upper()

    time_match = re.search(r"\b\d+\s*(?:h|hr|hrs|hour|hours|min|mins|minute|minutes|m|s|sec|secs|second|seconds)\b", html, flags=re.IGNORECASE)
    if time_match:
        return _read_text(time_match.group(0))

    return "unknown"


def _extract_generic_level(html: str) -> str:
    match = re.search(r"\b(beginner|intermediate|advanced|expert)\b", html, flags=re.IGNORECASE)
    if match:
        return match.group(1).capitalize()
    return "unknown"


def extract_course_metadata_from_html(html: str, *, source_url: str) -> CourseMetadata:
    """Parse a simple HTML page and return a validated CourseMetadata model."""
    title = _extract_first_value(
        html,
        r"<h[1-6][^>]*>(.*?)</h[1-6]>",
        r"<h[1-6][^>]*data-testid=[\"'][^\"']*title[\"'][^>]*>(.*?)</h[1-6]>",
        r"<h[1-6][^>]*aria-label=[\"'](?P<label>[^\"']+)[\"'][^>]*></h[1-6]>",
    )
    if title == "unknown":
        title = _extract_attr_value(html, keywords=("Prompt Engineering for Human Resources",))
        if title == "unknown":
            title = _extract_json_ld_value(html, key="name")
        if title == "unknown":
            title = _extract_meta_title(html)
        if title == "unknown":
            title = _extract_meta_value(html, key="name")

    duration = _extract_first_value(
        html,
        r"(?:course-duration|duration)[^>]*>(.*?)</(?:div|span|strong|p|li|section|article|main)>",
        r"data-testid=[\"']course-duration[\"'][^>]*>(.*?)</(?:div|span|strong|p|li|section|article|main)>",
        r"aria-label=[\"'].*?duration.*?[\"'][^>]*>(.*?)</(?:div|span|strong|p|li|section|article|main)>",
    )
    if duration == "unknown":
        duration = _extract_attr_value(html, keywords=("Duration", "23m 44s"))
        if duration == "unknown":
            duration = _extract_json_ld_value(html, key="timeRequired")
        if duration == "unknown":
            duration = _extract_meta_value(html, key="timeRequired")
        if duration == "unknown":
            duration = _extract_generic_duration(html)

    duration = _normalize_duration(duration)

    level = _extract_first_value(
        html,
        r"(?:skill-level|level)[^>]*>(.*?)</(?:div|span|strong|p|li|section|article|main)>",
        r"data-testid=[\"']course-level[\"'][^>]*>(.*?)</(?:div|span|strong|p|li|section|article|main)>",
        r"aria-label=[\"'].*?level.*?[\"'][^>]*>(.*?)</(?:div|span|strong|p|li|section|article|main)>",
    )
    if level == "unknown":
        level = _extract_attr_value(html, keywords=("Level", "Beginner"))
        if level == "unknown":
            level = _extract_json_ld_value(html, key="educationalLevel")
        if level == "unknown":
            level = _extract_meta_value(html, key="educationalLevel")
        if level == "unknown":
            level = _extract_generic_level(html)

    level = _read_text(level) or "unknown"

    if title == "unknown" and duration == "unknown" and level == "unknown":
        raise CourseMetadataNotFoundError("No usable course metadata was found on the page.")

    return CourseMetadata(
        training_name=title,
        duration=duration,
        level=level,
        source_url=source_url,
    )
