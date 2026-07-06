"""Agent pipeline for discovering, classifying, ranking, and persisting topics."""

from __future__ import annotations

from pathlib import Path

from src.config import get_settings
from src.models.rss_article import RSSArticle
from src.models.topic import Topic
from src.services.rss_downloader import download_feeds
from src.services.topic_classifier import TopicLabel, classify_articles
from src.services.topic_ranker import rank_articles
from src.storage.json_storage import save_json
from src.utils.logger import get_logger

logger = get_logger(__name__)

_TOPIC_LABEL_TO_CATEGORY: dict[TopicLabel, str] = {
    TopicLabel.IR: "international_relations",
    TopicLabel.POLITY: "polity",
    TopicLabel.ECONOMY: "economy",
    TopicLabel.SCIENCE: "science_and_technology",
    TopicLabel.ENVIRONMENT: "environment",
    TopicLabel.HISTORY: "history",
    TopicLabel.SOCIETY: "social_issues",
    TopicLabel.ETHICS: "ethics",
    TopicLabel.REPORTS: "governance",
    TopicLabel.PLACES: "geography",
    TopicLabel.PERSONS: "miscellaneous",
    TopicLabel.SPECIES: "environment",
    TopicLabel.UNCLASSIFIED: "miscellaneous",
}

_DEFAULT_OUTPUT_FILENAME: str = "topics.json"


def _build_topic_from_group(
    label: TopicLabel, ranked_articles: list[tuple[RSSArticle, int]]
) -> Topic:
    """Construct a Topic instance from a ranked group of classified articles."""
    from src.constants import UPSCCategory

    category_value = _TOPIC_LABEL_TO_CATEGORY.get(label, "miscellaneous")
    category = UPSCCategory(category_value)

    top_article, top_score = ranked_articles[0]
    topic = Topic(
        title=top_article.title,
        category=category,
        summary=top_article.summary,
        relevance=f"Importance score: {top_score}",
    )

    for article, _ in ranked_articles:
        topic.add_source_article(article)

    return topic


def _rank_grouped_articles(
    grouped_articles: dict[TopicLabel, list[RSSArticle]],
) -> dict[TopicLabel, list[tuple[RSSArticle, int]]]:
    """Rank articles within each topic group by importance score."""
    ranked_groups: dict[TopicLabel, list[tuple[RSSArticle, int]]] = {}
    for label, articles in grouped_articles.items():
        if not articles:
            continue
        ranked_groups[label] = rank_articles(articles)
    return ranked_groups


def _build_topics(
    ranked_groups: dict[TopicLabel, list[tuple[RSSArticle, int]]],
) -> list[Topic]:
    """Build Topic objects from ranked article groups."""
    topics: list[Topic] = []
    for label, ranked_articles in ranked_groups.items():
        if not ranked_articles:
            continue
        topic = _build_topic_from_group(label, ranked_articles)
        topics.append(topic)
    return topics


def find_topics(
    feed_urls: list[str] | None = None,
    output_path: Path | None = None,
) -> list[Topic]:
    """Run the full topic discovery pipeline and persist results to disk."""
    settings = get_settings()
    urls = feed_urls or settings.rss_feed_url_list()

    if not urls:
        logger.warning("No RSS feed URLs configured, skipping topic discovery")
        return []

    logger.info("Starting topic discovery pipeline for {} feeds", len(urls))

    articles = download_feeds(urls)
    if not articles:
        logger.warning("No articles were downloaded, aborting pipeline")
        return []

    grouped_articles = classify_articles(articles)
    ranked_groups = _rank_grouped_articles(grouped_articles)
    topics = _build_topics(ranked_groups)

    destination = output_path or (settings.processed_data_dir / _DEFAULT_OUTPUT_FILENAME)
    save_json([topic.to_dict() for topic in topics], destination)

    logger.info(
        "Topic discovery pipeline complete: {} topics saved to {}",
        len(topics),
        destination,
    )
    return topics