"""Unit tests for the keyword-rule based topic classifier."""

from __future__ import annotations


from datetime import datetime, timezone

from src.models.rss_article import RSSArticle
from src.services.topic_classifier import (
    TopicLabel,
    classify_article,
    classify_articles,
    classify_text,
)


def _make_article(title: str, summary: str = "", content: str = "") -> RSSArticle:
    """Build a minimal RSSArticle instance for testing."""
    return RSSArticle(
        title=title,
        url="https://example.com/article",
        source="Test Source",
        published_at=datetime.now(tz=timezone.utc),
        summary=summary,
        content=content,
    )


@pytest.mark.parametrize(
    ("text", "expected_label"),
    [
        (
            "India and the United States sign a new bilateral trade agreement",
            TopicLabel.IR,
        ),
        (
            "Lok Sabha passes the constitutional amendment bill",
            TopicLabel.POLITY,
        ),
        (
            "RBI announces new monetary policy amid rising inflation",
            TopicLabel.ECONOMY,
        ),
        (
            "ISRO successfully launches new satellite using quantum technology",
            TopicLabel.SCIENCE,
        ),
        (
            "Climate change and global warming threaten biodiversity in wetlands",
            TopicLabel.ENVIRONMENT,
        ),
        (
            "Archaeological findings reveal new insights into ancient india heritage site",
            TopicLabel.HISTORY,
        ),
        (
            "Government launches new education policy to reduce poverty and improve literacy",
            TopicLabel.SOCIETY,
        ),
        (
            "Committee report highlights concerns over corruption and lack of accountability",
            TopicLabel.ETHICS,
        ),
        (
            "World Bank report ranks countries on the human development index",
            TopicLabel.REPORTS,
        ),
        (
            "New bridge to connect the coastal area near the river basin valley",
            TopicLabel.PLACES,
        ),
        (
            "Chief Justice appointed as new head of the judiciary commission",
            TopicLabel.PERSONS,
        ),
        (
            "Tiger reserve reports rise in endangered species population",
            TopicLabel.SPECIES,
        ),
    ],
)
def test_classify_text_returns_expected_label() -> None:
    """Each category's representative text should classify to its expected label."""
    cases = [
        (
            "India and the United States sign a new bilateral trade agreement",
            TopicLabel.IR,
        ),
        (
            "Lok Sabha passes the constitutional amendment bill",
            TopicLabel.POLITY,
        ),
        ("RBI announces new monetary policy amid rising inflation", TopicLabel.ECONOMY),
        (
            "ISRO successfully launches new satellite using quantum technology",
            TopicLabel.SCIENCE,
        ),
        (
            "Climate change and global warming threaten biodiversity in wetlands",
            TopicLabel.ENVIRONMENT,
        ),
        (
            "Archaeological findings reveal new insights into ancient india heritage site",
            TopicLabel.HISTORY,
        ),
        (
            "Government launches new education policy to reduce poverty and improve literacy",
            TopicLabel.SOCIETY,
        ),
        (
            "Committee report highlights concerns over corruption and lack of accountability",
            TopicLabel.ETHICS,
        ),
        (
            "World Bank report ranks countries on the human development index",
            TopicLabel.REPORTS,
        ),
        (
            "New bridge to connect the coastal area near the river basin valley",
            TopicLabel.PLACES,
        ),
        (
            "Chief Justice appointed as new head of the judiciary commission",
            TopicLabel.PERSONS,
        ),
        ("Tiger reserve reports rise in endangered species population", TopicLabel.SPECIES),
    ]

    for text, expected_label in cases:
        assert classify_text(text) == expected_label


def test_classify_text_returns_unclassified_for_unrelated_text() -> None:
    """Text with no matching keywords should classify as unclassified."""
    result = classify_text("The weather today is sunny with a light breeze")
    assert result == TopicLabel.UNCLASSIFIED


def test_classify_article_uses_title_summary_and_content() -> None:
    """classify_article should combine title, summary, and content for matching."""
    article = _make_article(
        title="Update on national affairs",
        summary="",
        content="The Supreme Court delivered a landmark judiciary verdict today",
    )
    assert classify_article(article) == TopicLabel.POLITY


def test_classify_article_returns_unclassified_when_no_keywords_match() -> None:
    """An article with no matching keywords should be unclassified."""
    article = _make_article(
        title="Local bakery wins best pastry award",
        summary="A small town bakery received recognition",
    )
    assert classify_article(article) == TopicLabel.UNCLASSIFIED


def test_classify_articles_groups_by_label() -> None:
    """classify_articles should group articles into their respective labels."""
    articles = [
        _make_article("Parliament passes new amendment bill"),
        _make_article("RBI cuts repo rate amid inflation concerns"),
        _make_article("ISRO launches new satellite mission"),
        _make_article("Unrelated local weather update"),
    ]

    grouped = classify_articles(articles)

    assert len(grouped[TopicLabel.POLITY]) == 1
    assert len(grouped[TopicLabel.ECONOMY]) == 1
    assert len(grouped[TopicLabel.SCIENCE]) == 1
    assert len(grouped[TopicLabel.UNCLASSIFIED]) == 1


def test_classify_articles_includes_all_labels_as_keys() -> None:
    """classify_articles should return a dict containing all TopicLabel keys."""
    grouped = classify_articles([])
    for label in TopicLabel:
        assert label in grouped
        assert grouped[label] == []