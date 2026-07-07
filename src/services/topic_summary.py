"""Service for generating concise rule-based summaries from RSS descriptions."""

from __future__ import annotations

import re

from src.models.rss_article import RSSArticle
from src.utils.logger import get_logger

logger = get_logger(__name__)

_MAX_SUMMARY_WORDS: int = 50

_HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
_HTML_ENTITY_PATTERN = re.compile(r"&[a-zA-Z#0-9]+;")
_WHITESPACE_PATTERN = re.compile(r"\s+")
_URL_PATTERN = re.compile(r"https?://\S+")

_HTML_ENTITY_MAP: dict[str, str] = {
    "&amp;": "&",
    "&quot;": '"',
    "&apos;": "'",
    "&lt;": "<",
    "&gt;": ">",
    "&nbsp;": " ",
    "&#39;": "'",
    "&#8217;": "'",
    "&#8216;": "'",
    "&#8220;": '"',
    "&#8221;": '"',
    "&#8211;": "-",
    "&#8212;": "-",
}


def _replace_known_entities(text: str) -> str:
    """Replace known HTML entities with their plain-text equivalents."""
    for entity, replacement in _HTML_ENTITY_MAP.items():
        text = text.replace(entity, replacement)
    return text


def _strip_html_tags(text: str) -> str:
    """Remove HTML tags from the given text."""
    return _HTML_TAG_PATTERN.sub(" ", text)


def _strip_urls(text: str) -> str:
    """Remove raw URLs from the given text."""
    return _URL_PATTERN.sub("", text)


def _strip_remaining_entities(text: str) -> str:
    """Remove any remaining unrecognized HTML entities."""
    return _HTML_ENTITY_PATTERN.sub(" ", text)


def _collapse_whitespace(text: str) -> str:
    """Collapse repeated whitespace into single spaces and trim the result."""
    return _WHITESPACE_PATTERN.sub(" ", text).strip()


def clean_text(raw_text: str) -> str:
    """Clean raw RSS description text by removing HTML, URLs, and extra whitespace."""
    if not raw_text:
        return ""

    text = _replace_known_entities(raw_text)
    text = _strip_html_tags(text)
    text = _strip_urls(text)
    text = _strip_remaining_entities(text)
    text = _collapse_whitespace(text)
    return text


def truncate_to_word_limit(text: str, max_words: int = _MAX_SUMMARY_WORDS) -> str:
    """Truncate text to a maximum number of words, appending an ellipsis if cut."""
    words = text.split()
    if len(words) <= max_words:
        return text

    truncated = " ".join(words[:max_words]).rstrip(".,;: ")
    return f"{truncated}..."


def generate_summary(
    description: str, max_words: int = _MAX_SUMMARY_WORDS
) -> str:
    """Generate a concise summary from a raw RSS description using text cleanup."""
    cleaned_text = clean_text(description)
    summary = truncate_to_word_limit(cleaned_text, max_words)
    logger.debug("Generated summary of {} words", len(summary.split()))
    return summary


def generate_summary_for_article(
    article: RSSArticle, max_words: int = _MAX_SUMMARY_WORDS
) -> str:
    """Generate a concise summary for an RSSArticle from its summary or content."""
    source_text = article.summary or article.content
    return generate_summary(source_text, max_words)