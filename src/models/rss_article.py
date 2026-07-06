"""Data model representing a single RSS article."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from src.constants import ArticleFormat, UPSCCategory


@dataclass(slots=True)
class RSSArticle:
    """Represents a single article fetched from an RSS feed."""

    title: str
    url: str
    source: str
    published_at: datetime
    summary: str = ""
    content: str = ""
    author: str | None = None
    format: ArticleFormat = ArticleFormat.HTML
    category: UPSCCategory | None = None
    tags: list[str] = field(default_factory=list)
    image_url: str | None = None
    fetched_at: datetime = field(default_factory=datetime.utcnow)
    guid: str | None = None

    def word_count(self) -> int:
        """Return the number of words in the article content."""
        return len(self.content.split())

    def has_content(self) -> bool:
        """Return whether the article has non-empty content."""
        return bool(self.content.strip())

    def to_dict(self) -> dict[str, object]:
        """Return a serializable dictionary representation of the article."""
        return {
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "published_at": self.published_at.isoformat(),
            "summary": self.summary,
            "content": self.content,
            "author": self.author,
            "format": self.format.value,
            "category": self.category.value if self.category else None,
            "tags": list(self.tags),
            "image_url": self.image_url,
            "fetched_at": self.fetched_at.isoformat(),
            "guid": self.guid,
        }