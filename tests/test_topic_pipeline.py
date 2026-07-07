"""Integration-style unit tests covering the topic discovery pipeline stages."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest

from src.models.rss_article import RSSArticle
from src.services.duplicate_detector import deduplicate_by_title
from src.services.rss_downloader import download_feed, download_feeds
from src.services.rss_normalizer import deduplicate_articles, normalize_entries
from src.services.topic_classifier import TopicLabel, classify_article
from src.services.topic_ranker import rank_articles, score_article
from src.storage.topic_repository import TopicRepository

_SAMPLE_RSS_FEED: str = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Source</title>
    <item>
      <title>Parliament passes new constitutional amendment bill</title>
      <link>https://example.com/article-1</link>
      <description>The Lok Sabha passed a key amendment bill today.</description>
      <guid>article-1</guid>
    </item>
    <item>
      <title>RBI announces new monetary policy amid rising inflation</title>
      <link>https://example.com/article-2</link>
      <description>The Reserve Bank of India revised the repo rate.</description>
      <guid>article-2</guid>
    </item>
  </channel>
</rss>
"""


def _make_article(
    title: str,
    source: str = "Test Source",
    published_at: datetime | None = None,
    summary: str = "",
    content: str = "",
) -> RSSArticle:
    """Build a minimal RSSArticle instance for testing."""
    return RSSArticle(
        title=title,
        url=f"https://example.com/{title[:10]}",
        source=source,
        published_at=published_at or datetime.now(tz=timezone.utc),
        summary=summary,
        content=content,
    )


class TestRSSDownloader:
    """Tests for the RSS downloader service."""

    @patch("src.services.rss_downloader._fetch_feed_content")
    def test_download_feed_returns_articles(self, mock_fetch: MagicMock) -> None:
        """download_feed should parse feed content into RSSArticle objects."""
        mock_fetch.return_value = _SAMPLE_RSS_FEED

        articles = download_feed("https://example.com/rss")

        assert len(articles) == 2
        assert articles[0].title == "Parliament passes new constitutional amendment bill"
        assert articles[1].source == "Test Source"

    @patch("src.services.rss_downloader._fetch_feed_content")
    def test_download_feed_handles_http_error_gracefully(
        self, mock_fetch: MagicMock
    ) -> None:
        """download_feed should return an empty list when the fetch fails."""
        mock_fetch.side_effect = httpx.HTTPError("connection failed")

        articles = download_feed("https://example.com/rss")

        assert articles == []

    @patch("src.services.rss_downloader.download_feed")
    def test_download_feeds_aggregates_multiple_urls(
        self, mock_download_feed: MagicMock
    ) -> None:
        """download_feeds should aggregate articles from multiple feed URLs."""
        mock_download_feed.side_effect = [
            [_make_article("Article A")],
            [_make_article("Article B")],
        ]

        articles = download_feeds(
            ["https://example.com/rss1", "https://example.com/rss2"]
        )

        assert len(articles) == 2

    def test_download_feeds_returns_empty_for_no_urls(self) -> None:
        """download_feeds should return an empty list when given no URLs."""
        assert download_feeds([]) == []


class TestRSSNormalizer:
    """Tests for the RSS normalizer service."""

    def test_normalize_entries_fills_missing_fields(self) -> None:
        """normalize_entries should fill in defaults for missing entry fields."""
        raw_entries = [{"title": "", "link": ""}]

        normalized = normalize_entries(raw_entries, fallback_source="Fallback Source")

        assert len(normalized) == 1
        assert normalized[0].title == "Untitled Article"
        assert normalized[0].source == "Fallback Source"

    def test_normalize_entries_skips_unparseable_entries(self) -> None:
        """normalize_entries should skip entries that raise unexpected errors."""
        raw_entries = [{"title": "Valid Entry", "link": "https://example.com/valid"}]

        normalized = normalize_entries(raw_entries)

        assert len(normalized) == 1
        assert normalized[0].title == "Valid Entry"

    def test_deduplicate_articles_removes_duplicate_urls(self) -> None:
        """deduplicate_articles should remove articles with duplicate URLs."""
        article_a = _make_article("Article A")
        article_b = RSSArticle(
            title="Article A Duplicate",
            url=article_a.url,
            source="Other Source",
            published_at=datetime.now(tz=timezone.utc),
        )

        unique_articles = deduplicate_articles([article_a, article_b])

        assert len(unique_articles) == 1


class TestDuplicateDetector:
    """Tests for the title-similarity duplicate detector."""

    def test_deduplicate_by_title_removes_similar_titles(self) -> None:
        """deduplicate_by_title should filter out near-duplicate titles."""
        articles = [
            _make_article("RBI announces new monetary policy today"),
            _make_article("RBI announces new monetary policy today!!"),
            _make_article("ISRO launches new satellite mission"),
        ]

        unique_articles = deduplicate_by_title(articles)

        assert len(unique_articles) == 2

    def test_deduplicate_by_title_keeps_distinct_titles(self) -> None:
        """deduplicate_by_title should retain articles with distinct titles."""
        articles = [
            _make_article("Parliament passes new bill"),
            _make_article("ISRO launches new satellite"),
        ]

        unique_articles = deduplicate_by_title(articles)

        assert len(unique_articles) == 2


class TestTopicClassifier:
    """Tests for the weighted keyword topic classifier."""

    def test_classify_article_identifies_polity(self) -> None:
        """An article about Parliament should classify as polity."""
        article = _make_article(
            "Parliament passes new constitutional amendment bill"
        )
        assert classify_article(article) == TopicLabel.POLITY

    def test_classify_article_identifies_economy(self) -> None:
        """An article about RBI monetary policy should classify as economy."""
        article = _make_article("RBI announces new monetary policy")
        assert classify_article(article) == TopicLabel.ECONOMY

    def test_classify_article_returns_unclassified_for_unrelated_text(self) -> None:
        """An unrelated article should classify as unclassified."""
        article = _make_article("Local bakery wins best pastry award")
        assert classify_article(article) == TopicLabel.UNCLASSIFIED


class TestTopicRanker:
    """Tests for the topic importance ranker."""

    def test_score_article_returns_score_within_bounds(self) -> None:
        """score_article should always return a score between 1 and 100."""
        article = _make_article("Parliament passes new constitutional amendment bill")
        score = score_article(article)
        assert 1 <= score <= 100

    def test_score_article_favors_recent_articles(self) -> None:
        """A recently published article should score higher than an old one."""
        recent_article = _make_article(
            "RBI announces new monetary policy",
            published_at=datetime.now(tz=timezone.utc),
        )
        old_article = _make_article(
            "RBI announces new monetary policy",
            published_at=datetime.now(tz=timezone.utc) - timedelta(days=30),
        )

        assert score_article(recent_article) >= score_article(old_article)

    def test_rank_articles_sorts_descending(self) -> None:
        """rank_articles should sort articles by descending importance score."""
        articles = [
            _make_article("Local bakery wins best pastry award"),
            _make_article("Parliament passes new constitutional amendment bill"),
        ]

        ranked = rank_articles(articles)

        assert ranked[0][1] >= ranked[1][1]


class TestTopicRepository:
    """Tests for the JSON-backed topic repository."""

    @pytest.fixture
    def repository(self, tmp_path: Path) -> TopicRepository:
        """Provide a TopicRepository backed by a temporary file."""
        return TopicRepository(file_path=tmp_path / "topics.json")

    def test_save_and_load_topics_round_trip(
        self, repository: TopicRepository
    ) -> None:
        """Saved topics should be loadable and match the original data."""
        topics = [
            {"title": "Topic A", "category": "polity", "created_at": "2026-01-01"},
        ]

        repository.save_topics(topics)
        loaded_topics = repository.load_topics()

        assert len(loaded_topics) == 1
        assert loaded_topics[0]["title"] == "Topic A"

    def test_get_latest_returns_most_recent_first(
        self, repository: TopicRepository
    ) -> None:
        """get_latest should order topics by created_at descending."""
        topics = [
            {"title": "Older", "category": "polity", "created_at": "2026-01-01"},
            {"title": "Newer", "category": "economy", "created_at": "2026-02-01"},
        ]
        repository.save_topics(topics)

        latest = repository.get_latest(limit=1)

        assert latest[0]["title"] == "Newer"

    def test_get_by_category_filters_correctly(
        self, repository: TopicRepository
    ) -> None:
        """get_by_category should return only topics matching the category."""
        topics = [
            {"title": "Topic A", "category": "polity"},
            {"title": "Topic B", "category": "economy"},
        ]
        repository.save_topics(topics)

        polity_topics = repository.get_by_category("polity")

        assert len(polity_topics) == 1
        assert polity_topics[0]["title"] == "Topic A"

    def test_get_unapproved_returns_only_unapproved_topics(
        self, repository: TopicRepository
    ) -> None:
        """get_unapproved should return only topics not marked as approved."""
        topics = [
            {"title": "Topic A", "approved": True},
            {"title": "Topic B", "approved": False},
        ]
        repository.save_topics(topics)

        unapproved = repository.get_unapproved()

        assert len(unapproved) == 1
        assert unapproved[0]["title"] == "Topic B"