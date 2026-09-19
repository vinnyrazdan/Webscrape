"""Project-specific exceptions."""

from __future__ import annotations


class CourseMetadataError(ValueError):
    """Base exception for course metadata issues."""


class InvalidCourseUrlError(CourseMetadataError):
    """Raised when a course URL is invalid."""


class CourseMetadataNotFoundError(CourseMetadataError):
    """Raised when required metadata cannot be found on a page."""


class CoursePageLoadError(CourseMetadataError):
    """Raised when the course page cannot be loaded."""


class AuthenticationRequiredError(CourseMetadataError):
    """Raised when a saved Playwright session is missing or no longer valid."""
