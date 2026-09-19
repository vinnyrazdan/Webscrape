"""Course metadata domain model."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class CourseMetadata(BaseModel):
    """Validated metadata representing a Pluralsight course."""

    model_config = ConfigDict(str_strip_whitespace=True)

    training_name: str = Field(..., min_length=1)
    duration: str = Field(..., min_length=1)
    level: str = Field(..., min_length=1)
    source_url: HttpUrl
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("training_name", "duration", "level")
    @classmethod
    def validate_text_fields(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Field cannot be blank.")
        return cleaned

    @classmethod
    def model_validate(cls, obj: Any, *, strict: bool | None = None, from_attributes: bool | None = None) -> "CourseMetadata":
        """Compatibility wrapper for pydantic validation."""
        return super().model_validate(obj, strict=strict, from_attributes=from_attributes)
