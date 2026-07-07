"""Reusable manager for accessing and toggling categorized RSS feed sources."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.config.rss_feeds import ALL_FEED_CATEGORIES
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass(slots=True)
class RSSFeedManager:
    """Manages categorized RSS feed URLs with enable/disable support."""

    _categorized_feeds: dict[str, tuple[str, ...]] = field(
        default_factory=lambda: dict(ALL_FEED_CATEGORIES)
    )
    _disabled_urls: set[str] = field(default_factory=set)
    _disabled_categories: set[str] = field(default_factory=set)

    def get_categories(self) -> tuple[str, ...]:
        """Return all available feed category names."""
        return tuple(self._categorized_feeds.keys())

    def get_feeds_by_category(self, category: str) -> tuple[str, ...]:
        """Return enabled feed URLs for a specific category."""
        if category not in self._categorized_feeds:
            logger.warning("Unknown feed category requested: {}", category)
            return ()

        if category in self._disabled_categories:
            return ()

        return tuple(
            url
            for url in self._categorized_feeds[category]
            if url not in self._disabled_urls
        )

    def get_all_categorized_feeds(self) -> dict[str, tuple[str, ...]]:
        """Return all enabled feed URLs grouped by category."""
        return {
            category: self.get_feeds_by_category(category)
            for category in self._categorized_feeds
        }

    def get_all_feeds(self) -> tuple[str, ...]:
        """Return a flat tuple of all enabled feed URLs across categories."""
        all_urls: list[str] = []
        for category in self._categorized_feeds:
            all_urls.extend(self.get_feeds_by_category(category))
        return tuple(all_urls)

    def disable_url(self, url: str) -> None:
        """Disable a specific feed URL regardless of its category."""
        self._disabled_urls.add(url)
        logger.info("Disabled feed URL: {}", url)

    def enable_url(self, url: str) -> None:
        """Re-enable a previously disabled feed URL."""
        self._disabled_urls.discard(url)
        logger.info("Enabled feed URL: {}", url)

    def disable_category(self, category: str) -> None:
        """Disable an entire feed category."""
        if category not in self._categorized_feeds:
            logger.warning("Cannot disable unknown category: {}", category)
            return
        self._disabled_categories.add(category)
        logger.info("Disabled feed category: {}", category)

    def enable_category(self, category: str) -> None:
        """Re-enable a previously disabled feed category."""
        self._disabled_categories.discard(category)
        logger.info("Enabled feed category: {}", category)

    def is_url_enabled(self, url: str) -> bool:
        """Return whether a specific feed URL is currently enabled."""
        return url not in self._disabled_urls

    def is_category_enabled(self, category: str) -> bool:
        """Return whether a specific feed category is currently enabled."""
        return category not in self._disabled_categories