from __future__ import annotations

from pluralsight_mcp.models.course import CourseMetadata
from pluralsight_mcp.scraper.pluralsight import duration_to_hhmmss, extract_course_metadata_from_html


def test_duration_to_hhmmss_normalizes_rendered_duration() -> None:
  assert duration_to_hhmmss("23m 44s") == "00:23:44"
  assert duration_to_hhmmss("1h 5m 9s") == "01:05:09"
  assert duration_to_hhmmss("PT23M44S") == "00:23:44"
  assert duration_to_hhmmss("N/A") == ""


SAMPLE_HTML = """
<html>
  <body>
    <main>
      <h1>Prompt Engineering for Human Resources</h1>
      <div class="course-duration">23m 44s</div>
      <span class="skill-level">Beginner</span>
    </main>
  </body>
</html>
"""

ROBUST_HTML = """
<html>
  <body>
    <main>
      <h2 data-testid="course-title">Prompt Engineering for Human Resources</h2>
      <div data-testid="course-duration"><span>23m 44s</span></div>
      <div aria-label="course level"><strong>Beginner</strong></div>
    </main>
  </body>
</html>
"""

ATTRIBUTE_HTML = """
<html>
  <body>
    <main>
      <h2 data-testid="course-title" aria-label="Prompt Engineering for Human Resources"></h2>
      <div data-testid="course-duration" aria-label="Duration 23m 44s"></div>
      <div data-testid="course-level" aria-label="Level Beginner"></div>
    </main>
  </body>
</html>
"""

CANDIDATE_ATTRIBUTE_HTML = """
<html>
  <body>
    <main>
      <h2 data-course-title="Prompt Engineering for Human Resources"></h2>
      <div data-course-duration="23m 44s"></div>
      <div data-course-level="Beginner"></div>
    </main>
  </body>
</html>
"""

INLINE_DATA_HTML = """
<html>
  <body>
    <script type="application/ld+json">
      {
        "name": "Prompt Engineering for Human Resources",
        "timeRequired": "PT23M44S",
        "educationalLevel": "Beginner"
      }
    </script>
  </body>
</html>
"""

META_TITLE_HTML = """
<html>
  <head>
    <meta property="og:title" content="Prompt Engineering for Human Resources" />
  </head>
  <body>
    <div aria-label="Duration PT23M44S"></div>
    <div>Beginner</div>
  </body>
</html>
"""

ITEMPROP_META_HTML = """
<html>
  <head>
    <meta itemprop="name" content="Prompt Engineering for Human Resources" />
    <meta itemprop="timeRequired" content="PT23M44S" />
    <meta itemprop="educationalLevel" content="Beginner" />
  </head>
  <body></body>
</html>
"""

ISO_DURATION_HTML = """
<html>
  <body>
    <main>
      <h2>Prompt Engineering for Human Resources</h2>
      <span>PT23M44S</span>
      <div>Beginner</div>
    </main>
  </body>
</html>
"""


def test_extract_course_metadata_from_html_returns_valid_model() -> None:
    metadata = extract_course_metadata_from_html(
        SAMPLE_HTML,
        source_url="https://app.pluralsight.com/library/courses/prompt-engineering-human-resources",
    )

    assert isinstance(metadata, CourseMetadata)
    assert metadata.training_name == "Prompt Engineering for Human Resources"
    assert metadata.duration == "23m 44s"
    assert metadata.level == "Beginner"
    assert str(metadata.source_url) == "https://app.pluralsight.com/library/courses/prompt-engineering-human-resources"


def test_extract_course_metadata_from_html_handles_attribute_based_markup() -> None:
    metadata = extract_course_metadata_from_html(
        ROBUST_HTML,
        source_url="https://app.pluralsight.com/library/courses/prompt-engineering-human-resources",
    )

    assert metadata.training_name == "Prompt Engineering for Human Resources"
    assert metadata.duration == "23m 44s"
    assert metadata.level == "Beginner"


def test_extract_course_metadata_from_html_handles_attribute_values() -> None:
    metadata = extract_course_metadata_from_html(
        ATTRIBUTE_HTML,
        source_url="https://app.pluralsight.com/library/courses/prompt-engineering-human-resources",
    )

    assert metadata.training_name == "Prompt Engineering for Human Resources"
    assert metadata.duration == "23m 44s"
    assert metadata.level == "Beginner"


def test_extract_course_metadata_from_html_handles_data_attribute_values() -> None:
    metadata = extract_course_metadata_from_html(
        CANDIDATE_ATTRIBUTE_HTML,
        source_url="https://app.pluralsight.com/library/courses/prompt-engineering-human-resources",
    )

    assert metadata.training_name == "Prompt Engineering for Human Resources"
    assert metadata.duration == "23m 44s"
    assert metadata.level == "Beginner"


def test_extract_course_metadata_from_html_handles_inline_json_data() -> None:
    metadata = extract_course_metadata_from_html(
        INLINE_DATA_HTML,
        source_url="https://app.pluralsight.com/library/courses/prompt-engineering-human-resources",
    )

    assert metadata.training_name == "Prompt Engineering for Human Resources"
    assert metadata.duration == "PT23M44S"
    assert metadata.level == "Beginner"


def test_extract_course_metadata_from_html_handles_meta_title_values() -> None:
    metadata = extract_course_metadata_from_html(
        META_TITLE_HTML,
        source_url="https://app.pluralsight.com/library/courses/prompt-engineering-human-resources",
    )

    assert metadata.training_name == "Prompt Engineering for Human Resources"
    assert metadata.duration == "PT23M44S"
    assert metadata.level == "Beginner"


def test_extract_course_metadata_from_html_handles_itemprop_meta_values() -> None:
    metadata = extract_course_metadata_from_html(
        ITEMPROP_META_HTML,
        source_url="https://app.pluralsight.com/library/courses/prompt-engineering-human-resources",
    )

    assert metadata.training_name == "Prompt Engineering for Human Resources"
    assert metadata.duration == "PT23M44S"
    assert metadata.level == "Beginner"


def test_extract_course_metadata_from_html_handles_iso_duration_values() -> None:
    metadata = extract_course_metadata_from_html(
        ISO_DURATION_HTML,
        source_url="https://app.pluralsight.com/library/courses/prompt-engineering-human-resources",
    )

    assert metadata.training_name == "Prompt Engineering for Human Resources"
    assert metadata.duration == "PT23M44S"
    assert metadata.level == "Beginner"


def test_extract_course_metadata_from_html_handles_missing_values() -> None:
    metadata = extract_course_metadata_from_html(
        "<html><body><h1>Sample</h1></body></html>",
        source_url="https://app.pluralsight.com/library/courses/sample-course",
    )

    assert metadata.training_name == "Sample"
    assert metadata.duration == "unknown"
    assert metadata.level == "unknown"
