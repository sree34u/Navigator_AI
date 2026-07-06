"""Service for converting raw RSS feed entries into RSSArticle objects."""

from __future__ import annotations

from datetime import datetime, timezone
from time import struct_time

import feedparser

from src.constants import ArticleFormat
from src.models.rss_article import RSSArticle
from src.utils.logger import get_logger

logger = get_logger(__name__)


def parse_published_date(entry: feedparser.FeedParserDict) -> datetime:
    """Extract and normalize the published date from a feed entry."""
    parsed_time: struct_time | None = entry.get("published_parsed") or entry.get(
        "updated_parsed"
    )
    if parsed_time is None:
        return datetime.now(tz=timezone.utc)
    return datetime(*parsed_time[:6], tzinfo=timezone.utc)


def extract_image_url(entry: feedparser.FeedParserDict) -> str | None:
    """Extract a representative image URL from a feed entry, if present."""
    media_content = entry.get("media_content")
    if media_content:
        url = media_content[0].get("url")
        if url:
            return str(url)
    links = entry.get("links", [])
    for link in links:
        if str(link.get("type", "")).startswith("image/"):
            return str(link.get("href"))
    return None


def extract_tags(entry: feedparser.FeedParserDict) -> list[str]:
    """Extract tag terms from a feed entry."""
    return [
        tag.get("term", "") for tag in entry.get("tags", []) if tag.get("term")
    ]


def entry_to_article(entry: feedparser.FeedParserDict, source: str) -> RSSArticle:
    """Convert a single feedparser entry into an RSSArticle instance."""
    return RSSArticle(
        title=entry.get("title", "").strip(),
        url=entry.get("link", "").strip(),
        source=source,
        published_at=parse_published_date(entry),
        summary=entry.get("summary", "").strip(),
        author=entry.get("author"),
        format=ArticleFormat.HTML,
        tags=extract_tags(entry),
        image_url=extract_image_url(entry),
        guid=entry.get("id") or entry.get("guid"),
    )


def parse_feed_content(raw_content: str, source: str | None = None) -> list[RSSArticle]:
    """Parse raw RSS/Atom feed content into a list of RSSArticle objects."""
    parsed_feed = feedparser.parse(raw_content)

    if parsed_feed.bozo and not parsed_feed.entries:
        logger.error(
            "Failed to parse feed content: {}", parsed_feed.get("bozo_exception")
        )
        return []

    feed_source = source or parsed_feed.feed.get("title", "unknown")
    articles = [
        entry_to_article(entry, source=feed_source) for entry in parsed_feed.entries
    ]
    logger.debug("Parsed {} articles from source: {}", len(articles), feed_source)
    return articles


def entries_to_articles(
    entries: list[feedparser.FeedParserDict], source: str
) -> list[RSSArticle]:
    """Convert a list of feedparser entries into RSSArticle objects."""
    articles: list[RSSArticle] = []
    for entry in entries:
        try:
            articles.append(entry_to_article(entry, source=source))
        except Exception as exc:
            logger.warning("Skipping malformed entry from {}: {}", source, exc)
            continue
    return articles