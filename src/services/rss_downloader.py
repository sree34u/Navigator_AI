"""Service for downloading and parsing RSS feeds from multiple sources."""

from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from time import struct_time

import feedparser
import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.config import get_settings
from src.constants import ArticleFormat, DEFAULT_RSS_USER_AGENT
from src.models.rss_article import RSSArticle
from src.utils.logger import get_logger

logger = get_logger(__name__)

_DEFAULT_MAX_WORKERS: int = 8


class RSSDownloadError(Exception):
    """Raised when an RSS feed cannot be downloaded or parsed."""


@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((httpx.HTTPError, RSSDownloadError)),
)
def _fetch_feed_content(url: str, timeout_seconds: int) -> str:
    """Fetch raw RSS feed content from a URL with retries and timeout handling."""
    headers = {"User-Agent": DEFAULT_RSS_USER_AGENT}
    try:
        with httpx.Client(timeout=httpx.Timeout(timeout_seconds)) as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
    except httpx.TimeoutException as exc:
        logger.warning("Timeout while fetching feed {}: {}", url, exc)
        raise RSSDownloadError(f"Timeout while fetching feed: {url}") from exc
    except httpx.HTTPError as exc:
        logger.warning("HTTP error while fetching feed {}: {}", url, exc)
        raise
    return response.text


def _parse_published_date(entry: feedparser.FeedParserDict) -> datetime:
    """Extract and normalize the published date from a feed entry."""
    parsed_time: struct_time | None = entry.get("published_parsed") or entry.get(
        "updated_parsed"
    )
    if parsed_time is None:
        return datetime.now(tz=timezone.utc)
    return datetime(*parsed_time[:6], tzinfo=timezone.utc)


def _extract_image_url(entry: feedparser.FeedParserDict) -> str | None:
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


def _entry_to_article(entry: feedparser.FeedParserDict, source: str) -> RSSArticle:
    """Convert a single feed entry into an RSSArticle instance."""
    return RSSArticle(
        title=entry.get("title", "").strip(),
        url=entry.get("link", "").strip(),
        source=source,
        published_at=_parse_published_date(entry),
        summary=entry.get("summary", "").strip(),
        author=entry.get("author"),
        format=ArticleFormat.HTML,
        tags=[tag.get("term", "") for tag in entry.get("tags", [])],
        image_url=_extract_image_url(entry),
        guid=entry.get("id") or entry.get("guid"),
    )


def download_feed(url: str, max_articles: int | None = None) -> list[RSSArticle]:
    """Download and parse a single RSS feed URL into a list of articles."""
    settings = get_settings()
    timeout_seconds = settings.rss_fetch_timeout_seconds
    limit = max_articles or settings.rss_max_articles_per_feed

    try:
        raw_content = _fetch_feed_content(url, timeout_seconds)
    except (httpx.HTTPError, RSSDownloadError) as exc:
        logger.error("Failed to download feed {}: {}", url, exc)
        return []

    parsed_feed = feedparser.parse(raw_content)
    if parsed_feed.bozo and not parsed_feed.entries:
        logger.error(
            "Failed to parse feed {}: {}", url, parsed_feed.get("bozo_exception")
        )
        return []

    feed_title = parsed_feed.feed.get("title", url)
    articles = [
        _entry_to_article(entry, source=feed_title)
        for entry in parsed_feed.entries[:limit]
    ]
    logger.info("Fetched {} articles from feed: {}", len(articles), feed_title)
    return articles


def download_feeds(
    urls: list[str],
    max_articles: int | None = None,
    max_workers: int = _DEFAULT_MAX_WORKERS,
) -> list[RSSArticle]:
    """Download and parse multiple RSS feed URLs in parallel, aggregating articles."""
    all_articles: list[RSSArticle] = []

    if not urls:
        return all_articles

    worker_count = min(max_workers, len(urls))

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        future_to_url: dict[Future[list[RSSArticle]], str] = {
            executor.submit(download_feed, url, max_articles): url for url in urls
        }

        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                articles = future.result()
                all_articles.extend(articles)
            except Exception as exc:
                logger.exception("Unexpected error processing feed {}: {}", url, exc)
                continue

    logger.info(
        "Downloaded a total of {} articles from {} feeds", len(all_articles), len(urls)
    )
    return all_articles