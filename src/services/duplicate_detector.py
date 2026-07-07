"""Service for detecting duplicate news articles using title similarity."""

from __future__ import annotations

import re
from difflib import SequenceMatcher

from src.models.rss_article import RSSArticle
from src.utils.logger import get_logger

logger = get_logger(__name__)

_DEFAULT_SIMILARITY_THRESHOLD: float = 0.85
_WORD_BOUNDARY_PATTERN = re.compile(r"[^a-z0-9\s]")


def _normalize_title(title: str) -> str:
    """Lowercase and strip punctuation from a title for comparison."""
    normalized = _WORD_BOUNDARY_PATTERN.sub(" ", title.lower())
    return " ".join(normalized.split())


def compute_similarity(title_a: str, title_b: str) -> float:
    """Compute a similarity ratio between two titles, between 0.0 and 1.0."""
    normalized_a = _normalize_title(title_a)
    normalized_b = _normalize_title(title_b)

    if not normalized_a or not normalized_b:
        return 0.0

    return SequenceMatcher(None, normalized_a, normalized_b).ratio()


def is_duplicate_title(
    title: str,
    existing_titles: list[str],
    threshold: float = _DEFAULT_SIMILARITY_THRESHOLD,
) -> bool:
    """Return whether a title is a near-duplicate of any existing title."""
    return any(
        compute_similarity(title, existing_title) >= threshold
        for existing_title in existing_titles
    )


def deduplicate_by_title(
    articles: list[RSSArticle],
    threshold: float = _DEFAULT_SIMILARITY_THRESHOLD,
) -> list[RSSArticle]:
    """Return only unique articles, filtering out near-duplicate titles."""
    unique_articles: list[RSSArticle] = []
    seen_titles: list[str] = []

    for article in articles:
        if is_duplicate_title(article.title, seen_titles, threshold):
            logger.debug("Filtered duplicate article: {}", article.title)
            continue

        unique_articles.append(article)
        seen_titles.append(article.title)

    logger.info(
        "Duplicate detection reduced {} articles to {} unique articles",
        len(articles),
        len(unique_articles),
    )
    return unique_articles