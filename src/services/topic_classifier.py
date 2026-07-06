"""Keyword-rule based classifier for categorizing RSS articles by topic."""

from __future__ import annotations

import re
from collections import Counter
from enum import StrEnum

from src.models.rss_article import RSSArticle
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TopicLabel(StrEnum):
    """Supported topic classification labels."""

    IR = "international_relations"
    POLITY = "polity"
    ECONOMY = "economy"
    SCIENCE = "science"
    ENVIRONMENT = "environment"
    HISTORY = "history"
    SOCIETY = "society"
    ETHICS = "ethics"
    REPORTS = "reports"
    PLACES = "places"
    PERSONS = "persons"
    SPECIES = "species"
    UNCLASSIFIED = "unclassified"


_KEYWORD_RULES: dict[TopicLabel, tuple[str, ...]] = {
    TopicLabel.IR: (
        "bilateral",
        "diplomacy",
        "diplomatic",
        "foreign policy",
        "united nations",
        "un security council",
        "treaty",
        "embassy",
        "g20",
        "g7",
        "brics",
        "saarc",
        "asean",
        "nato",
        "cross-border",
        "border dispute",
        "trade agreement",
        "sanctions",
        "geopolitics",
        "external affairs",
    ),
    TopicLabel.POLITY: (
        "parliament",
        "lok sabha",
        "rajya sabha",
        "constitution",
        "amendment bill",
        "supreme court",
        "high court",
        "judiciary",
        "president",
        "governor",
        "election commission",
        "fundamental rights",
        "directive principles",
        "cabinet",
        "ordinance",
        "legislation",
        "assembly election",
        "panchayati raj",
    ),
    TopicLabel.ECONOMY: (
        "gdp",
        "inflation",
        "reserve bank",
        "rbi",
        "monetary policy",
        "fiscal deficit",
        "union budget",
        "repo rate",
        "stock market",
        "sensex",
        "nifty",
        "trade deficit",
        "exports",
        "imports",
        "economic survey",
        "disinvestment",
        "gst",
        "npa",
        "inflation rate",
    ),
    TopicLabel.SCIENCE: (
        "isro",
        "satellite",
        "artificial intelligence",
        "quantum",
        "vaccine",
        "research",
        "technology",
        "space mission",
        "nuclear",
        "biotechnology",
        "supercomputer",
        "telescope",
        "spacecraft",
        "clinical trial",
        "genome",
    ),
    TopicLabel.ENVIRONMENT: (
        "climate change",
        "global warming",
        "biodiversity",
        "wildlife sanctuary",
        "national park",
        "pollution",
        "carbon emission",
        "renewable energy",
        "deforestation",
        "cop28",
        "cop29",
        "unfccc",
        "wetland",
        "ecosystem",
        "conservation",
        "environment ministry",
    ),
    TopicLabel.HISTORY: (
        "freedom struggle",
        "independence movement",
        "ancient india",
        "medieval india",
        "mughal",
        "colonial",
        "british raj",
        "archaeological",
        "heritage site",
        "inscription",
        "dynasty",
        "historical",
    ),
    TopicLabel.SOCIETY: (
        "gender",
        "caste",
        "poverty",
        "literacy",
        "social justice",
        "reservation",
        "minority",
        "tribal",
        "urbanization",
        "migration",
        "education policy",
        "healthcare",
        "malnutrition",
        "women empowerment",
        "child labour",
    ),
    TopicLabel.ETHICS: (
        "ethics",
        "integrity",
        "corruption",
        "whistleblower",
        "moral",
        "accountability",
        "transparency",
        "code of conduct",
        "governance ethics",
        "probity",
    ),
    TopicLabel.REPORTS: (
        "report released",
        "index ranking",
        "world bank report",
        "global report",
        "survey report",
        "annual report",
        "niti aayog report",
        "who report",
        "unesco report",
        "human development index",
        "ranking index",
    ),
    TopicLabel.PLACES: (
        "district",
        "state government",
        "border region",
        "coastal area",
        "himalayan",
        "island",
        "valley",
        "plateau",
        "river basin",
        "strait",
        "peninsula",
    ),
    TopicLabel.PERSONS: (
        "awarded to",
        "appointed as",
        "chief justice",
        "prime minister",
        "chief minister",
        "nobel laureate",
        "president of india",
        "governor of",
        "scientist",
        "author of",
        "padma award",
    ),
    TopicLabel.SPECIES: (
        "species",
        "endangered",
        "iucn red list",
        "tiger reserve",
        "bird sanctuary",
        "flora and fauna",
        "extinct",
        "habitat",
        "wildlife",
        "endemic species",
        "critically endangered",
    ),
}

_WORD_BOUNDARY_PATTERN = re.compile(r"[^a-z0-9\s]")


def _normalize_text(text: str) -> str:
    """Lowercase and strip punctuation from text for keyword matching."""
    return _WORD_BOUNDARY_PATTERN.sub(" ", text.lower())


def _article_text(article: RSSArticle) -> str:
    """Combine relevant article fields into a single text blob."""
    return " ".join(
        (
            article.title,
            article.summary,
            article.content,
            " ".join(article.tags),
        )
    )


def _count_keyword_matches(text: str, keywords: tuple[str, ...]) -> int:
    """Count how many keywords appear in the given text."""
    return sum(1 for keyword in keywords if keyword in text)


def classify_text(text: str) -> TopicLabel:
    """Classify a raw text string into a topic label using keyword rules."""
    normalized_text = _normalize_text(text)
    scores: Counter[TopicLabel] = Counter()

    for label, keywords in _KEYWORD_RULES.items():
        match_count = _count_keyword_matches(normalized_text, keywords)
        if match_count > 0:
            scores[label] = match_count

    if not scores:
        return TopicLabel.UNCLASSIFIED

    best_label, _ = scores.most_common(1)[0]
    return best_label


def classify_article(article: RSSArticle) -> TopicLabel:
    """Classify an RSSArticle into a topic label using keyword rules."""
    combined_text = _article_text(article)
    label = classify_text(combined_text)
    logger.debug("Classified article '{}' as {}", article.title, label.value)
    return label


def classify_articles(
    articles: list[RSSArticle],
) -> dict[TopicLabel, list[RSSArticle]]:
    """Classify a batch of articles, grouping them by topic label."""
    grouped: dict[TopicLabel, list[RSSArticle]] = {
        label: [] for label in TopicLabel
    }
    for article in articles:
        label = classify_article(article)
        grouped[label].append(article)

    for label, matched_articles in grouped.items():
        if matched_articles:
            logger.info(
                "Category '{}' matched {} articles", label.value, len(matched_articles)
            )

    return grouped