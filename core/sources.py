"""Loads articles from RSS/Atom feeds (live) or a local JSON file (offline)."""
import json
import os
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from .models import Article

SAMPLE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sample_articles.json")

DEFAULT_FEEDS = {
    "BBC Top Stories": "https://feeds.bbci.co.uk/news/rss.xml",
    "BBC Technology": "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "BBC Science": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
    "BBC Business": "https://feeds.bbci.co.uk/news/business/rss.xml",
    "BBC Health": "https://feeds.bbci.co.uk/news/health/rss.xml",
}

ATOM = "{http://www.w3.org/2005/Atom}"


def _parse_date(value):
    if not value:
        return None
    try:
        dt = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _text(el, tag):
    node = el.find(tag)
    return (node.text or "").strip() if node is not None and node.text else ""


def parse_feed(xml_text, source=""):
    """Parses RSS 2.0 or Atom XML into Article objects."""
    root = ET.fromstring(xml_text)
    articles = []
    items = root.findall(".//item")
    if items:
        for it in items:
            articles.append(Article(
                title=_text(it, "title"),
                link=_text(it, "link"),
                source=source,
                published=_parse_date(_text(it, "pubDate")),
                description=_text(it, "description"),
            ))
    else:
        for entry in root.findall(f".//{ATOM}entry"):
            link_el = entry.find(f"{ATOM}link")
            articles.append(Article(
                title=_text(entry, f"{ATOM}title"),
                link=link_el.get("href", "") if link_el is not None else "",
                source=source,
                published=_parse_date(_text(entry, f"{ATOM}updated")),
                description=_text(entry, f"{ATOM}summary"),
            ))
    return [a for a in articles if a.title]


def fetch_feed(url, source="", timeout=10):
    request = urllib.request.Request(url, headers={"User-Agent": "NewsDigest/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return parse_feed(response.read(), source or url)


def load_sample(path=SAMPLE_PATH):
    with open(path, encoding="utf-8") as f:
        rows = json.load(f)
    return [Article(**{**row, "published": _parse_date(row.get("published"))}) for row in rows]
