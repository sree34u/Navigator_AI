"""Service for normalizing RSS entries from varied publishers into a common structure."""

from __future__ import annotations

from datetime import datetime, timezone
from time import struct_time
from typing import Any

import feedparser

from src.constants import ArticleFormat
from src.models.rss_article import RSSArticle
from src.utils.logger import get_logger

logger = get_logger(__name__)

_UNKNOWN_TITLE: str = "Untitled Article"
_UNKNOWN_SOURCE: str = "Unknown Source"
_EMPTY_STRING: str = ""


def _safe_get(entry: Any, key: str, default: Any = None) -> Any:
    """Safely retrieve a key from a feedparser entry or dict-like object."""
    try:
        value = entry.get(key, default)
    except AttributeError:
        value = getattr(entry, key, default)
    return value if value is not None else default


def _normalize_title(entry: Any) -> str:
    """Normalize and clean the article title, falling back to a default."""
    title = _safe_get(entry, "title", _EMPTY_STRING)
    cleaned = str(title).strip()
    return cleaned if cleaned else _UNKNOWN_TITLE


def _normalize_url(entry: Any) -> str:
    """Normalize the article URL, falling back to an empty string."""
    url = _safe_get(entry, "link", _EMPTY_STRING)
    return str(url).strip()


def _normalize_source(entry: Any, fallback_source: str | None) -> str:
    """Normalize the source name, preferring an explicit fallback if provided."""
    if fallback_source:
        return fallback_source.strip() or _UNKNOWN_SOURCE

    source_field = _safe_get(entry, "source", None)
    if isinstance(source_field, dict):
        title = source_field.get("title", _EMPTY_STRING)
        if title:
            return str(title).strip()

    return _UNKNOWN_SOURCE


def _normalize_published_date(entry: Any) -> datetime:
    """Normalize the published date, defaulting to the current UTC time."""
    parsed_time: struct_time | None = _safe_get(
        entry, "published_parsed", None
    ) or _safe_get(entry, "updated_parsed", None)

    if parsed_time is None:
        return datetime.now(tz=timezone.utc)

    try:
        return datetime(*parsed_time[:6], tzinfo=timezone.utc)
    except (TypeError, ValueError) as exc:
        logger.warning("Failed to parse published date, using current time: {}", exc)
        return datetime.now(tz=timezone.utc)


def _normalize_summary(entry: Any) -> str:
    """Normalize the article summary, falling back to an empty string."""
    summary = _safe_get(entry, "summary", _EMPTY_STRING)
    return str(summary).strip()


def _normalize_author(entry: Any) -> str | None:
    """Normalize the author field, returning None when absent."""
    author = _safe_get(entry, "author", None)
    if author is None:
        return None
    cleaned = str(author).strip()
    return cleaned or None


def _normalize_tags(entry: Any) -> list[str]:
    """Normalize tag terms from a feed entry, ignoring malformed entries."""
    raw_tags = _safe_get(entry, "tags", [])
    if not isinstance(raw_tags, list):
        return []

    tags: list[str] = []
    for tag in raw_tags:
        if isinstance(tag, dict):
            term = tag.get("term")
            if term:
                tags.append(str(term).strip())
    return tags


def _normalize_image_url(entry: Any) -> str | None:
    """Normalize a representative image URL from a feed entry, if present."""
    media_content = _safe_get(entry, "media_content", None)
    if isinstance(media_content, list) and media_content:
        url = media_content[0].get("url")
        if url:
            return str(url)

    links = _safe_get(entry, "links", [])
    if isinstance(links, list):
        for link in links:
            if isinstance(link, dict) and str(link.get("type", "")).startswith(
                "image/"
            ):
                href = link.get("href")
                if href:
                    return str(href)

    return None


def _normalize_guid(entry: Any) -> str | None:
    """Normalize the unique identifier for a feed entry."""
    guid = _safe_get(entry, "id", None) or _safe_get(entry, "guid", None)
    if guid is None:
        return None
    cleaned = str(guid).strip()
    return cleaned or None


def normalize_entry(
    entry: feedparser.FeedParserDict | dict[str, Any],
    fallback_source: str | None = None,
) -> RSSArticle:
    """Normalize a single raw feed entry into a common RSSArticle structure."""
    return RSSArticle(
        title=_normalize_title(entry),
        url=_normalize_url(entry),
        source=_normalize_source(entry, fallback_source),
        published_at=_normalize_published_date(entry),
        summary=_normalize_summary(entry),
        author=_normalize_author(entry),
        format=ArticleFormat.HTML,
        tags=_normalize_tags(entry),
        image_url=_normalize_image_url(entry),
        guid=_normalize_guid(entry),
    )


def normalize_entries(
    entries: list[feedparser.FeedParserDict | dict[str, Any]],
    fallback_source: str | None = None,
) -> list[RSSArticle]:
    """Normalize a batch of raw feed entries, skipping any that fail entirely."""
    normalized_articles: list[RSSArticle] = []

    for entry in entries:
        try:
            normalized_articles.append(normalize_entry(entry, fallback_source))
        except Exception as exc:
            logger.warning("Skipping unnormalizable entry: {}", exc)
            continue

    logger.debug(
        "Normalized {} of {} entries into RSSArticle objects",
        len(normalized_articles),
        len(entries),
    )
    return normalized_articles


def deduplicate_articles(articles: list[RSSArticle]) -> list[RSSArticle]:
    """Remove duplicate articles based on URL or GUID, preserving first occurrence."""
    seen_keys: set[str] = set()
    unique_articles: list[RSSArticle] = []

    for article in articles:
        key = article.guid or article.url
        if not key or key in seen_keys:
            continue
        seen_keys.add(key)
        unique_articles.append(article)

    logger.debug(
        "Deduplicated {} articles down to {} unique articles",
        len(articles),
        len(unique_articles),
    )
    return unique_articles