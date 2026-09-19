import json
import sys
from html.parser import HTMLParser
from urllib.request import urlopen


class _HTMLScraper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.title_parts = []
        self.links = []
        self.text_parts = []

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self.in_title = True
        elif tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        cleaned = " ".join(data.split())
        if not cleaned:
            return
        if self.in_title:
            self.title_parts.append(cleaned)
        self.text_parts.append(cleaned)

    def data(self):
        return {
            "title": " ".join(self.title_parts).strip(),
            "links": self.links,
            "text": " ".join(self.text_parts).strip(),
        }


def scrape(url):
    with urlopen(url) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        html = response.read().decode(charset, errors="replace")

    parser = _HTMLScraper()
    parser.feed(html)

    data = parser.data()
    data["url"] = url
    return data


def main(argv=None):
    argv = argv or sys.argv[1:]
    if len(argv) != 1:
        print("Usage: python scraper.py <url>", file=sys.stderr)
        return 1

    print(json.dumps(scrape(argv[0]), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
