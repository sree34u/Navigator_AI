"""Rule-based service for scoring RSSArticle importance from 1-100."""

from __future__ import annotations

import re
from datetime import datetime, timezone

from src.models.rss_article import RSSArticle
from src.services.topic_classifier import TopicLabel, classify_article
from src.utils.logger import get_logger

logger = get_logger(__name__)

_MAX_SCORE: int = 100
_MIN_SCORE: int = 1

_UPSC_RELEVANCE_WEIGHTS: dict[TopicLabel, int] = {
    TopicLabel.POLITY: 18,
    TopicLabel.GOVERNANCE: 16,
    TopicLabel.ECONOMY: 18,
    TopicLabel.IR: 14,
    TopicLabel.ENVIRONMENT: 14,
    TopicLabel.SCIENCE: 13,
    TopicLabel.INTERNAL_SECURITY: 14,
    TopicLabel.REPORTS: 12,
    TopicLabel.SOCIETY: 11,
    TopicLabel.ETHICS: 10,
    TopicLabel.ART_AND_CULTURE: 8,
    TopicLabel.SPECIES: 9,
    TopicLabel.PERSONS: 7,
    TopicLabel.HISTORY: 7,
    TopicLabel.PLACES: 6,
    TopicLabel.UNCLASSIFIED: 2,
}

_INTERNATIONAL_IMPORTANCE_KEYWORDS: tuple[str, ...] = (
    "united nations",
    "world bank",
    "international monetary fund",
    "g20",
    "g7",
    "brics",
    "nato",
    "asean",
    "saarc",
    "bilateral",
    "diplomatic",
    "un security council",
    "global summit",
    "international treaty",
    "cop28",
    "cop29",
    "world health organization",
    "trade agreement",
    "sanctions",
)

_HIGH_IMPACT_KEYWORDS: tuple[str, ...] = (
    "supreme court",
    "parliament",
    "union budget",
    "rbi",
    "national security",
    "amendment bill",
    "isro",
    "nobel",
    "climate change",
    "human development index",
    "constitution",
    "election commission",
)

_GOVERNMENT_SOURCE_KEYWORDS: tuple[str, ...] = (
    "pib",
    "press information bureau",
    "rbi",
    "reserve bank of india",
    "niti aayog",
    "mea",
    "ministry of",
    "sansad",
    "lok sabha",
    "rajya sabha",
    "government of india",
    "cabinet secretariat",
)

_WORD_BOUNDARY_PATTERN = re.compile(r"[^a-z0-9\s]")

_RECENCY_FULL_SCORE_HOURS: int = 24
_RECENCY_DECAY_HOURS: int = 168
_RECENCY_MAX_POINTS: int = 20

_KEYWORD_MAX_POINTS: int = 15
_KEYWORD_POINTS_PER_MATCH: int = 4

_INTERNATIONAL_MAX_POINTS: int = 15
_INTERNATIONAL_POINTS_PER_MATCH: int = 4

_GOVERNMENT_SOURCE_POINTS: int = 15

_UPSC_RELEVANCE_MAX_POINTS: int = 18


def _normalize_text(text: str) -> str:
    """Lowercase and strip punctuation for keyword matching."""
    return _WORD_BOUNDARY_PATTERN.sub(" ", text.lower())


def _upsc_relevance_score(article: RSSArticle) -> int:
    """Score based on the classified topic's weighted relevance to UPSC syllabus."""
    label = classify_article(article)
    return _UPSC_RELEVANCE_WEIGHTS.get(
        label, _UPSC_RELEVANCE_WEIGHTS[TopicLabel.UNCLASSIFIED]
    )


def _keyword_importance_score(article: RSSArticle) -> int:
    """Score based on presence of high-impact keywords in the article text."""
    text = _normalize_text(f"{article.title} {article.summary} {article.content}")
    match_count = sum(1 for keyword in _HIGH_IMPACT_KEYWORDS if keyword in text)
    points = match_count * _KEYWORD_POINTS_PER_MATCH
    return min(points, _KEYWORD_MAX_POINTS)


def _international_importance_score(article: RSSArticle) -> int:
    """Score based on presence of international-affairs keywords."""
    text = _normalize_text(f"{article.title} {article.summary} {article.content}")
    match_count = sum(
        1 for keyword in _INTERNATIONAL_IMPORTANCE_KEYWORDS if keyword in text
    )
    points = match_count * _INTERNATIONAL_POINTS_PER_MATCH
    return min(points, _INTERNATIONAL_MAX_POINTS)


def _recency_score(article: RSSArticle) -> int:
    """Score based on how recently the article was published."""
    published_at = article.published_at
    if published_at.tzinfo is None:
        published_at = published_at.replace(tzinfo=timezone.utc)

    now = datetime.now(tz=timezone.utc)
    age_hours = max((now - published_at).total_seconds() / 3600, 0)

    if age_hours <= _RECENCY_FULL_SCORE_HOURS:
        return _RECENCY_MAX_POINTS

    if age_hours >= _RECENCY_DECAY_HOURS:
        return 0

    decay_ratio = 1 - (
        (age_hours - _RECENCY_FULL_SCORE_HOURS)
        / (_RECENCY_DECAY_HOURS - _RECENCY_FULL_SCORE_HOURS)
    )
    return round(_RECENCY_MAX_POINTS * decay_ratio)


def _government_source_score(article: RSSArticle) -> int:
    """Score based on whether the article originates from a government source."""
    normalized_source = _normalize_text(article.source)
    if any(keyword in normalized_source for keyword in _GOVERNMENT_SOURCE_KEYWORDS):
        return _GOVERNMENT_SOURCE_POINTS
    return 0


def score_article(article: RSSArticle) -> int:
    """Compute a weighted importance score from 1 to 100 for an article."""
    total_score = (
        _government_source_score(article)
        + _recency_score(article)
        + _keyword_importance_score(article)
        + _upsc_relevance_score(article)
        + _international_importance_score(article)
    )

    clamped_score = max(_MIN_SCORE, min(_MAX_SCORE, total_score))
    logger.debug(
        "Scored article '{}' with importance {}", article.title, clamped_score
    )
    return clamped_score


def rank_articles(articles: list[RSSArticle]) -> list[tuple[RSSArticle, int]]:
    """Score and sort articles by descending importance score."""
    scored_articles = [(article, score_article(article)) for article in articles]
    scored_articles.sort(key=lambda pair: pair[1], reverse=True)
    logger.info("Ranked {} articles by importance score", len(scored_articles))
    return scored_articles