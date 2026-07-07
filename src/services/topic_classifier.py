"""Weighted keyword-rule based classifier for categorizing RSS articles by topic."""

from __future__ import annotations

import re
from enum import StrEnum

from src.models.rss_article import RSSArticle
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TopicLabel(StrEnum):
    """Supported topic classification labels."""

    IR = "international_relations"
    POLITY = "polity"
    GOVERNANCE = "governance"
    ECONOMY = "economy"
    ENVIRONMENT = "environment"
    SCIENCE = "science"
    HISTORY = "history"
    ART_AND_CULTURE = "art_and_culture"
    SOCIETY = "society"
    ETHICS = "ethics"
    REPORTS = "reports"
    PLACES = "places"
    PERSONS = "persons"
    SPECIES = "species"
    INTERNAL_SECURITY = "internal_security"
    UNCLASSIFIED = "unclassified"


_KEYWORD_WEIGHTS: dict[TopicLabel, dict[str, float]] = {
    TopicLabel.IR: {
        "bilateral": 2.0,
        "diplomacy": 2.5,
        "diplomatic": 2.0,
        "foreign policy": 3.0,
        "united nations": 3.0,
        "un security council": 3.5,
        "treaty": 2.0,
        "embassy": 1.5,
        "g20": 2.5,
        "g7": 2.0,
        "brics": 2.5,
        "saarc": 2.5,
        "asean": 2.5,
        "nato": 2.5,
        "cross-border": 1.5,
        "border dispute": 2.5,
        "trade agreement": 2.5,
        "sanctions": 2.0,
        "geopolitics": 2.5,
        "external affairs": 2.5,
        "visa policy": 1.5,
        "extradition": 2.0,
    },
    TopicLabel.POLITY: {
        "parliament": 3.0,
        "lok sabha": 3.0,
        "rajya sabha": 3.0,
        "constitution": 3.0,
        "amendment bill": 3.0,
        "supreme court": 2.5,
        "high court": 2.0,
        "judiciary": 2.0,
        "president": 1.5,
        "governor": 1.5,
        "election commission": 2.5,
        "fundamental rights": 2.5,
        "directive principles": 2.5,
        "cabinet": 1.5,
        "ordinance": 2.0,
        "legislation": 2.0,
        "assembly election": 2.5,
        "panchayati raj": 2.0,
        "federalism": 2.0,
        "separation of powers": 2.5,
    },
    TopicLabel.GOVERNANCE: {
        "e-governance": 3.0,
        "public administration": 2.5,
        "civil services": 2.5,
        "policy implementation": 2.0,
        "welfare scheme": 2.5,
        "digital india": 2.5,
        "aadhaar": 2.0,
        "right to information": 2.5,
        "administrative reform": 2.5,
        "bureaucracy": 2.0,
        "governance model": 2.0,
        "public service delivery": 2.5,
        "citizen charter": 2.0,
        "good governance": 2.5,
        "decentralization": 2.0,
    },
    TopicLabel.ECONOMY: {
        "gdp": 3.0,
        "inflation": 2.5,
        "reserve bank": 3.0,
        "rbi": 3.0,
        "monetary policy": 3.0,
        "fiscal deficit": 2.5,
        "union budget": 3.0,
        "repo rate": 2.5,
        "stock market": 2.0,
        "sensex": 1.5,
        "nifty": 1.5,
        "trade deficit": 2.5,
        "exports": 1.5,
        "imports": 1.5,
        "economic survey": 3.0,
        "disinvestment": 2.0,
        "gst": 2.5,
        "npa": 2.0,
        "inflation rate": 2.5,
        "fdi": 2.0,
        "current account deficit": 2.5,
    },
    TopicLabel.ENVIRONMENT: {
        "climate change": 3.0,
        "global warming": 3.0,
        "biodiversity": 2.5,
        "wildlife sanctuary": 2.0,
        "national park": 2.0,
        "pollution": 2.0,
        "carbon emission": 2.5,
        "renewable energy": 2.5,
        "deforestation": 2.5,
        "cop28": 2.5,
        "cop29": 2.5,
        "unfccc": 2.5,
        "wetland": 2.0,
        "ecosystem": 2.0,
        "conservation": 2.0,
        "environment ministry": 2.5,
        "green energy": 2.0,
        "sustainable development": 2.5,
    },
    TopicLabel.SCIENCE: {
        "isro": 3.0,
        "satellite": 2.0,
        "artificial intelligence": 2.5,
        "quantum": 2.5,
        "vaccine": 2.0,
        "research": 1.5,
        "technology": 1.5,
        "space mission": 3.0,
        "nuclear": 2.0,
        "biotechnology": 2.5,
        "supercomputer": 2.5,
        "telescope": 2.0,
        "spacecraft": 2.5,
        "clinical trial": 2.0,
        "genome": 2.5,
        "chandrayaan": 3.0,
        "gaganyaan": 3.0,
    },
    TopicLabel.HISTORY: {
        "freedom struggle": 3.0,
        "independence movement": 3.0,
        "ancient india": 2.5,
        "medieval india": 2.5,
        "mughal": 2.0,
        "colonial": 2.0,
        "british raj": 2.5,
        "archaeological": 2.0,
        "heritage site": 2.0,
        "inscription": 2.0,
        "dynasty": 2.0,
        "historical": 1.5,
    },
    TopicLabel.ART_AND_CULTURE: {
        "classical dance": 3.0,
        "folk art": 2.5,
        "handicraft": 2.0,
        "sculpture": 2.0,
        "painting": 1.5,
        "temple architecture": 2.5,
        "unesco world heritage": 3.0,
        "festival": 1.5,
        "classical music": 2.5,
        "literature award": 2.0,
        "cultural heritage": 2.5,
        "tribal art": 2.0,
        "handloom": 2.0,
        "intangible heritage": 2.5,
    },
    TopicLabel.SOCIETY: {
        "gender": 2.0,
        "caste": 2.5,
        "poverty": 2.0,
        "literacy": 2.0,
        "social justice": 2.5,
        "reservation": 2.5,
        "minority": 2.0,
        "tribal": 2.0,
        "urbanization": 2.0,
        "migration": 2.0,
        "education policy": 2.5,
        "healthcare": 2.0,
        "malnutrition": 2.5,
        "women empowerment": 2.5,
        "child labour": 2.5,
        "demographic dividend": 2.0,
    },
    TopicLabel.ETHICS: {
        "ethics": 3.0,
        "integrity": 2.5,
        "corruption": 2.5,
        "whistleblower": 2.5,
        "moral": 1.5,
        "accountability": 2.0,
        "transparency": 2.0,
        "code of conduct": 2.5,
        "governance ethics": 2.5,
        "probity": 2.5,
        "conflict of interest": 2.5,
    },
    TopicLabel.REPORTS: {
        "report released": 2.5,
        "index ranking": 2.5,
        "world bank report": 3.0,
        "global report": 2.5,
        "survey report": 2.0,
        "annual report": 2.0,
        "niti aayog report": 3.0,
        "who report": 2.5,
        "unesco report": 2.5,
        "human development index": 3.0,
        "ranking index": 2.5,
        "global hunger index": 3.0,
        "corruption perception index": 3.0,
    },
    TopicLabel.PLACES: {
        "district": 1.5,
        "state government": 1.5,
        "border region": 2.0,
        "coastal area": 2.0,
        "himalayan": 2.0,
        "island": 1.5,
        "valley": 1.5,
        "plateau": 2.0,
        "river basin": 2.5,
        "strait": 2.0,
        "peninsula": 2.0,
    },
    TopicLabel.PERSONS: {
        "awarded to": 2.0,
        "appointed as": 2.0,
        "chief justice": 2.5,
        "prime minister": 2.0,
        "chief minister": 2.0,
        "nobel laureate": 3.0,
        "president of india": 2.5,
        "governor of": 1.5,
        "scientist": 1.5,
        "author of": 1.5,
        "padma award": 3.0,
    },
    TopicLabel.SPECIES: {
        "species": 2.0,
        "endangered": 2.5,
        "iucn red list": 3.0,
        "tiger reserve": 2.5,
        "bird sanctuary": 2.5,
        "flora and fauna": 2.5,
        "extinct": 2.0,
        "habitat": 2.0,
        "wildlife": 2.0,
        "endemic species": 2.5,
        "critically endangered": 3.0,
    },
    TopicLabel.INTERNAL_SECURITY: {
        "terrorism": 3.0,
        "insurgency": 2.5,
        "naxalism": 2.5,
        "left wing extremism": 2.5,
        "cyber security": 2.5,
        "border security force": 2.5,
        "national investigation agency": 3.0,
        "unlawful activities prevention act": 3.0,
        "communal violence": 2.5,
        "internal security": 3.0,
        "counter terrorism": 2.5,
        "armed forces special powers act": 3.0,
        "smuggling": 2.0,
        "money laundering": 2.0,
        "organized crime": 2.0,
    },
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


def _weighted_score(text: str, keyword_weights: dict[str, float]) -> float:
    """Compute the total weighted score of matched keywords in the text."""
    return sum(
        weight for keyword, weight in keyword_weights.items() if keyword in text
    )


def classify_text(text: str) -> TopicLabel:
    """Classify a raw text string into a topic label using weighted keyword rules."""
    normalized_text = _normalize_text(text)
    scores: dict[TopicLabel, float] = {}

    for label, keyword_weights in _KEYWORD_WEIGHTS.items():
        score = _weighted_score(normalized_text, keyword_weights)
        if score > 0:
            scores[label] = score

    if not scores:
        return TopicLabel.UNCLASSIFIED

    best_label = max(scores, key=lambda label: scores[label])
    return best_label


def classify_text_with_scores(text: str) -> dict[TopicLabel, float]:
    """Return the full weighted score breakdown for a text across all labels."""
    normalized_text = _normalize_text(text)
    scores: dict[TopicLabel, float] = {}

    for label, keyword_weights in _KEYWORD_WEIGHTS.items():
        score = _weighted_score(normalized_text, keyword_weights)
        if score > 0:
            scores[label] = score

    return scores


def classify_article(article: RSSArticle) -> TopicLabel:
    """Classify an RSSArticle into a topic label using weighted keyword rules."""
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