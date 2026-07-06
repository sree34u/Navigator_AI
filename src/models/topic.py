"""Data model representing a single UPSC current affairs topic."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from src.constants import UPSCCategory
from src.models.rss_article import RSSArticle


@dataclass(slots=True)
class Topic:
    """Represents a single UPSC-relevant current affairs topic."""

    title: str
    category: UPSCCategory
    summary: str = ""
    analysis: str = ""
    relevance: str = ""
    keywords: list[str] = field(default_factory=list)
    source_articles: list[RSSArticle] = field(default_factory=list)
    prelims_points: list[str] = field(default_factory=list)
    mains_points: list[str] = field(default_factory=list)
    static_links: list[str] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def add_source_article(self, article: RSSArticle) -> None:
        """Attach a source article to this topic."""
        self.source_articles.append(article)

    def source_count(self) -> int:
        """Return the number of source articles backing this topic."""
        return len(self.source_articles)

    def is_complete(self) -> bool:
        """Return whether the topic has both summary and analysis content."""
        return bool(self.summary.strip()) and bool(self.analysis.strip())

    def to_dict(self) -> dict[str, object]:
        """Return a serializable dictionary representation of the topic."""
        return {
            "id": str(self.id),
            "title": self.title,
            "category": self.category.value,
            "summary": self.summary,
            "analysis": self.analysis,
            "relevance": self.relevance,
            "keywords": list(self.keywords),
            "source_articles": [
                article.to_dict() for article in self.source_articles
            ],
            "prelims_points": list(self.prelims_points),
            "mains_points": list(self.mains_points),
            "static_links": list(self.static_links),
            "created_at": self.created_at.isoformat(),
        }