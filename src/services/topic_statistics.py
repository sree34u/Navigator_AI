"""Service for computing aggregate statistics over persisted topics."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from src.utils.logger import get_logger

logger = get_logger(__name__)

_RELEVANCE_SCORE_PATTERN = re.compile(r"(\d+)")


@dataclass(slots=True)
class TopicStatistics:
    """Aggregate statistics computed over a collection of topics."""

    total_topics: int = 0
    topics_per_category: dict[str, int] = field(default_factory=dict)
    average_score: float = 0.0
    highest_score: int = 0
    highest_score_topic_title: str | None = None
    source_distribution: dict[str, int] = field(default_factory=dict)


def _extract_score(topic: dict[str, Any]) -> int | None:
    """Extract the numeric importance score from a topic's relevance field."""
    relevance = topic.get("relevance", "")
    if not relevance:
        return None

    match = _RELEVANCE_SCORE_PATTERN.search(str(relevance))
    if not match:
        return None

    return int(match.group(1))


def _extract_sources(topic: dict[str, Any]) -> list[str]:
    """Extract source names from a topic's source articles."""
    source_articles = topic.get("source_articles", [])
    return [
        article.get("source", "unknown")
        for article in source_articles
        if isinstance(article, dict)
    ]


def compute_topics_per_category(topics: list[dict[str, Any]]) -> dict[str, int]:
    """Compute the number of topics grouped by category."""
    counter = Counter(topic.get("category", "unknown") for topic in topics)
    return dict(counter)


def compute_score_metrics(topics: list[dict[str, Any]]) -> tuple[float, int, str | None]:
    """Compute average score, highest score, and the top-scoring topic title."""
    scores: list[tuple[int, str]] = []

    for topic in topics:
        score = _extract_score(topic)
        if score is not None:
            scores.append((score, topic.get("title", "Untitled")))

    if not scores:
        return 0.0, 0, None

    total_score = sum(score for score, _ in scores)
    average_score = round(total_score / len(scores), 2)
    highest_score, highest_score_title = max(scores, key=lambda pair: pair[0])

    return average_score, highest_score, highest_score_title


def compute_source_distribution(topics: list[dict[str, Any]]) -> dict[str, int]:
    """Compute the distribution of source articles across publishers."""
    counter: Counter[str] = Counter()
    for topic in topics:
        counter.update(_extract_sources(topic))
    return dict(counter)


def compute_statistics(topics: list[dict[str, Any]]) -> TopicStatistics:
    """Compute full aggregate statistics for a collection of topics."""
    if not topics:
        logger.info("No topics provided, returning empty statistics")
        return TopicStatistics()

    topics_per_category = compute_topics_per_category(topics)
    average_score, highest_score, highest_score_title = compute_score_metrics(topics)
    source_distribution = compute_source_distribution(topics)

    statistics = TopicStatistics(
        total_topics=len(topics),
        topics_per_category=topics_per_category,
        average_score=average_score,
        highest_score=highest_score,
        highest_score_topic_title=highest_score_title,
        source_distribution=source_distribution,
    )

    logger.info(
        "Computed statistics: {} topics, avg score {}, highest score {}",
        statistics.total_topics,
        statistics.average_score,
        statistics.highest_score,
    )
    return statistics