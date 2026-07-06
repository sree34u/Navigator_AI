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

_CATEGORY_WEIGHTS: dict[TopicLabel, int] = {
    TopicLabel.POLITY: 20,
    TopicLabel.ECONOMY: 20,
    TopicLabel.IR: 18,
    TopicLabel.ENVIRONMENT: 15,
    TopicLabel.SCIENCE: 15,
    TopicLabel.REPORTS: 14,
    TopicLabel.SOCIETY: 12,
    TopicLabel.SPECIES: 10,
    TopicLabel.PERSONS: 8,
    TopicLabel.HISTORY: 8,
    TopicLabel.ETHICS: 8,
    TopicLabel.PLACES: 6,
    TopicLabel.UNCLASSIFIED: 2,
}

_HIGH_IMPACT_KEYWORDS: tuple[str, ...] = (
    "supreme court",
    "parliament",
    "union budget",
    "rbi",
    "united nations",
    "national security",
    "amendment bill",
    "cop28",
    "cop29",
    "g20",
    "isro",
    "nobel",
    "climate change",
    "world bank",
    "human development index",
)

_WORD_BOUNDARY_PATTERN = re.compile(r"[^a-z0-9\s]")

_RECENCY_FULL_SCORE_HOURS: int = 24
_RECENCY_DECAY_HOURS: int = 168
_RECENCY_MAX_POINTS: int = 25

_KEYWORD_MAX_POINTS: int = 20
_KEYWORD_POINTS_PER_MATCH: int = 5

_CONTENT_LENGTH_MAX_POINTS: int = 15
_CONTENT_LENGTH_IDEAL_WORDS: int = 400

_SOURCE_TRUST_MAX_POINTS: int = 10
_TRUSTED_SOURCE_KEYWORDS: tuple[str, ...] = (
    "the hindu",
    "pib",
    "livemint",
    "indian express",
    "business standard",
)


def _normalize_text(text: str) -> str:
    """Lowercase and strip punctuation for keyword matching."""
    return _WORD_BOUNDARY_PATTERN.sub(" ", text.lower())


def _category_score(article: RSSArticle) -> int:
    """Score based on the classified topic category weight."""
    label = classify_article(article)
    return _CATEGORY_WEIGHTS.get(label, _CATEGORY_WEIGHTS[TopicLabel.UNCLASSIFIED])


def _keyword_score(article: RSSArticle) -> int:
    """Score based on presence of high-impact keywords."""
    text = _normalize_text(f"{article.title} {article.summary} {article.content}")
    match_count = sum(1 for keyword in _HIGH_IMPACT_KEYWORDS if keyword in text)
    points = match_count * _KEYWORD_POINTS_PER_MATCH
    return min(points, _KEYWORD_MAX_POINTS)


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


def _content_length_score(article: RSSArticle) -> int:
    """Score based on how close the content length is to an ideal word count."""
    word_count = article.word_count()
    if word_count == 0:
        return 0

    ratio = min(word_count, _CONTENT_LENGTH_IDEAL_WORDS) / _CONTENT_LENGTH_IDEAL_WORDS
    return round(_CONTENT_LENGTH_MAX_POINTS * ratio)


def _source_trust_score(article: RSSArticle) -> int:
    """Score based on whether the article source is a recognized trusted outlet."""
    normalized_source = _normalize_text(article.source)
    if any(trusted in normalized_source for trusted in _TRUSTED_SOURCE_KEYWORDS):
        return _SOURCE_TRUST_MAX_POINTS
    return 0


def score_article(article: RSSArticle) -> int:
    """Compute a weighted importance score from 1 to 100 for an article."""
    total_score = (
        _category_score(article)
        + _keyword_score(article)
        + _recency_score(article)
        + _content_length_score(article)
        + _source_trust_score(article)
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