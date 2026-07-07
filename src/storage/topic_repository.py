"""Repository for persisting and querying UPSC topics using JSON storage."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.config import get_settings
from src.storage.json_storage import load_json_or_default, save_json
from src.utils.logger import get_logger

logger = get_logger(__name__)

_DEFAULT_FILENAME: str = "topics.json"
_APPROVED_KEY: str = "approved"
_CATEGORY_KEY: str = "category"
_CREATED_AT_KEY: str = "created_at"


def _default_repository_path() -> Path:
    """Return the default file path used for topic persistence."""
    settings = get_settings()
    return settings.processed_data_dir / _DEFAULT_FILENAME


class TopicRepository:
    """Repository providing save, load, and query operations for topics."""

    def __init__(self, file_path: Path | None = None) -> None:
        """Initialize the repository with an optional custom file path."""
        self._file_path: Path = file_path or _default_repository_path()

    def save_topics(self, topics: list[dict[str, Any]]) -> None:
        """Persist a list of topic dictionaries, defaulting missing fields."""
        normalized_topics = [self._normalize_topic(topic) for topic in topics]
        save_json(normalized_topics, self._file_path)
        logger.info(
            "Saved {} topics to {}", len(normalized_topics), self._file_path
        )

    def load_topics(self) -> list[dict[str, Any]]:
        """Load all persisted topic dictionaries from storage."""
        topics = load_json_or_default(self._file_path, default=[])
        if not isinstance(topics, list):
            logger.error("Topic storage at {} is malformed", self._file_path)
            return []
        return topics

    def get_latest(self, limit: int = 10) -> list[dict[str, Any]]:
        """Return the most recently created topics, up to the given limit."""
        topics = self.load_topics()
        sorted_topics = sorted(
            topics,
            key=lambda topic: topic.get(_CREATED_AT_KEY, ""),
            reverse=True,
        )
        return sorted_topics[:limit]

    def get_by_category(self, category: str) -> list[dict[str, Any]]:
        """Return all topics matching the given category."""
        topics = self.load_topics()
        matched_topics = [
            topic for topic in topics if topic.get(_CATEGORY_KEY) == category
        ]
        logger.debug(
            "Found {} topics for category '{}'", len(matched_topics), category
        )
        return matched_topics

    def get_unapproved(self) -> list[dict[str, Any]]:
        """Return all topics that have not yet been approved."""
        topics = self.load_topics()
        unapproved_topics = [
            topic for topic in topics if not topic.get(_APPROVED_KEY, False)
        ]
        logger.debug("Found {} unapproved topics", len(unapproved_topics))
        return unapproved_topics

    @staticmethod
    def _normalize_topic(topic: dict[str, Any]) -> dict[str, Any]:
        """Ensure a topic dictionary has all expected repository fields."""
        normalized = dict(topic)
        normalized.setdefault(_APPROVED_KEY, False)
        return normalized