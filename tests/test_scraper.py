import io
import json
import unittest
from unittest.mock import patch

import scraper


class _MockHeaders:
    def get_content_charset(self):
        return "utf-8"


class _MockResponse:
    def __init__(self, html):
        self.html = html.encode("utf-8")
        self.headers = _MockHeaders()

    def read(self):
        return self.html

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class ScraperTests(unittest.TestCase):
    def test_scrape_extracts_title_links_and_text(self):
        html = """
        <html>
          <head><title>Example Page</title></head>
          <body>
            <h1>Heading</h1>
            <p>Hello world</p>
            <a href="https://example.com/a">First</a>
            <a href="/relative">Second</a>
          </body>
        </html>
        """

        with patch("scraper.urlopen", return_value=_MockResponse(html)):
            data = scraper.scrape("https://example.com")

        self.assertEqual(data["url"], "https://example.com")
        self.assertEqual(data["title"], "Example Page")
        self.assertEqual(data["links"], ["https://example.com/a", "/relative"])
        self.assertIn("Heading", data["text"])
        self.assertIn("Hello world", data["text"])

    def test_main_prints_json(self):
        expected = {
            "url": "https://example.com",
            "title": "Example Page",
            "links": ["https://example.com/a"],
            "text": "Example Page Hello world First",
        }

        with patch("scraper.scrape", return_value=expected), patch(
            "sys.stdout", new_callable=io.StringIO
        ) as stdout:
            exit_code = scraper.main(["https://example.com"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(json.loads(stdout.getvalue()), expected)

    def test_main_requires_url(self):
        with patch("sys.stderr", new_callable=io.StringIO) as stderr:
            exit_code = scraper.main([])

        self.assertEqual(exit_code, 1)
        self.assertIn("Usage: python scraper.py <url>", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
