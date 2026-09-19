from __future__ import annotations

import pytest

from pluralsight_mcp.server import export_courses, get_course_metadata, get_multiple_courses, validate_course_url


def test_validate_course_url_accepts_valid_pluralsight_urls() -> None:
    url = "https://app.pluralsight.com/library/courses/prompt-engineering-human-resources"
    assert validate_course_url(url) == url


def test_validate_course_url_rejects_non_pluralsight_url() -> None:
    with pytest.raises(ValueError):
        validate_course_url("https://example.com/course")


def test_get_course_metadata_returns_expected_fields() -> None:
    result = get_course_metadata("https://app.pluralsight.com/library/courses/prompt-engineering-human-resources")

    assert set(result) >= {"training_name", "duration", "level", "source_url", "scraped_at"}
    assert result["training_name"] == "Prompt Engineering for Human Resources"
    assert result["duration"] == "23m 44s"
    assert result["level"] == "Beginner"
    assert str(result["source_url"]).startswith("https://")


def test_get_multiple_courses_returns_multiple_results() -> None:
    urls = [
        "https://app.pluralsight.com/library/courses/prompt-engineering-human-resources",
        "https://app.pluralsight.com/library/courses/prompt-engineering-human-resources",
    ]

    results = get_multiple_courses(urls)

    assert len(results) == 2
    assert all(item["training_name"] == "Prompt Engineering for Human Resources" for item in results)


def test_export_courses_supports_json_and_csv() -> None:
    courses = [
        {
            "training_name": "Prompt Engineering for Human Resources",
            "duration": "23m 44s",
            "level": "Beginner",
            "source_url": "https://app.pluralsight.com/library/courses/prompt-engineering-human-resources",
            "scraped_at": "2026-09-19T00:00:00+00:00",
        }
    ]

    json_export = export_courses(courses, file_format="json")
    assert '"training_name"' in json_export

    csv_export = export_courses(courses, file_format="csv")
    assert "training_name" in csv_export
    assert "Prompt Engineering for Human Resources" in csv_export
