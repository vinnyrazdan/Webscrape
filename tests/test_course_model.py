from __future__ import annotations

from datetime import datetime

import pytest

from pluralsight_mcp.models.course import CourseMetadata


def test_course_metadata_accepts_valid_payload() -> None:
    payload = {
        "training_name": "Prompt Engineering for Human Resources",
        "duration": "23m 44s",
        "level": "Beginner",
        "source_url": "https://app.pluralsight.com/library/courses/prompt-engineering-human-resources",
        "scraped_at": "2026-09-19T10:00:00Z",
    }

    metadata = CourseMetadata.model_validate(payload)

    assert metadata.training_name == "Prompt Engineering for Human Resources"
    assert metadata.duration == "23m 44s"
    assert metadata.level == "Beginner"
    assert isinstance(metadata.scraped_at, datetime)


def test_course_metadata_rejects_invalid_url() -> None:
    with pytest.raises(ValueError):
        CourseMetadata.model_validate(
            {
                "training_name": "Broken course",
                "duration": "10m",
                "level": "Intermediate",
                "source_url": "not-a-valid-url",
                "scraped_at": "2026-09-19T00:00:00Z",
            }
        )
