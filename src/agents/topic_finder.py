"""Agent pipeline for discovering, classifying, ranking, and persisting topics."""

from __future__ import annotations

from src.constants import UPSCCategory
from src.models.rss_article import RSSArticle
from src.models.topic import Topic
from src.services.duplicate_detector import deduplicate_by_title
from src.services.rss_downloader import download_feeds
from src.services.rss_feed_manager import RSSFeedManager
from src.services.rss_normalizer import deduplicate_articles, normalize_entries
from src.services.topic_classifier import TopicLabel, classify_articles
from src.services.topic_ranker import rank_articles
from src.services.topic_summary import generate_summary_for_article
from src.storage.topic_repository import TopicRepository
from src.utils.logger import get_logger

logger = get_logger(__name__)

_TOPIC_LABEL_TO_CATEGORY: dict[TopicLabel, str] = {
    TopicLabel.IR: "international_relations",
    TopicLabel.POLITY: "polity",
    TopicLabel.GOVERNANCE: "governance",
    TopicLabel.ECONOMY: "economy",
    TopicLabel.ENVIRONMENT: "environment",
    TopicLabel.SCIENCE: "science_and_technology",
    TopicLabel.HISTORY: "history",
    TopicLabel.ART_AND_CULTURE: "art_and_culture",
    TopicLabel.SOCIETY: "social_issues",
    TopicLabel.ETHICS: "ethics",
    TopicLabel.REPORTS: "governance",
    TopicLabel.PLACES: "geography",
    TopicLabel.PERSONS: "miscellaneous",
    TopicLabel.SPECIES: "environment",
    TopicLabel.INTERNAL_SECURITY: "security",
    TopicLabel.UNCLASSIFIED: "miscellaneous",
}


def _load_feed_urls(feed_manager: RSSFeedManager) -> list[str]:
    """Load all enabled RSS feed URLs from the feed manager."""
    return list(feed_manager.get_all_feeds())


def _normalize_articles(raw_articles: list[RSSArticle]) -> list[RSSArticle]:
    """Normalize raw articles into a consistent structure."""
    entries = [article.to_dict() for article in raw_articles]
    return normalize_entries(entries)


def _remove_duplicates(articles: list[RSSArticle]) -> list[RSSArticle]:
    """Remove duplicate articles by GUID/URL and by title similarity."""
    deduplicated_by_key = deduplicate_articles(articles)
    return deduplicate_by_title(deduplicated_by_key)


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


def _build_topic_from_group(
    label: TopicLabel, ranked_articles: list[tuple[RSSArticle, int]]
) -> Topic:
    """Construct a Topic instance from a ranked group of classified articles."""
    category_value = _TOPIC_LABEL_TO_CATEGORY.get(label, "miscellaneous")
    category = UPSCCategory(category_value)

    top_article, top_score = ranked_articles[0]
    summary = generate_summary_for_article(top_article)

    topic = Topic(
        title=top_article.title,
        category=category,
        summary=summary,
        relevance=f"Importance score: {top_score}",
    )

    for article, _ in ranked_articles:
        topic.add_source_article(article)

    return topic


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


def _log_pipeline_statistics(
    feed_count: int,
    downloaded_count: int,
    normalized_count: int,
    deduplicated_count: int,
    grouped_articles: dict[TopicLabel, list[RSSArticle]],
    topic_count: int,
) -> None:
    """Log summary statistics for the topic discovery pipeline run."""
    logger.info("Pipeline statistics:")
    logger.info("  Feeds loaded: {}", feed_count)
    logger.info("  Articles downloaded: {}", downloaded_count)
    logger.info("  Articles normalized: {}", normalized_count)
    logger.info("  Articles after deduplication: {}", deduplicated_count)
    for label, articles in grouped_articles.items():
        if articles:
            logger.info("  Category '{}': {} articles", label.value, len(articles))
    logger.info("  Topics generated: {}", topic_count)


def find_topics(
    feed_urls: list[str] | None = None,
    repository: TopicRepository | None = None,
) -> list[Topic]:
    """Run the full topic discovery pipeline and persist results to disk."""
    feed_manager = RSSFeedManager()
    urls = feed_urls or _load_feed_urls(feed_manager)

    if not urls:
        logger.warning("No RSS feed URLs configured, skipping topic discovery")
        return []

    logger.info("Starting topic discovery pipeline for {} feeds", len(urls))

    downloaded_articles = download_feeds(urls)
    if not downloaded_articles:
        logger.warning("No articles were downloaded, aborting pipeline")
        return []

    normalized_articles = _normalize_articles(downloaded_articles)
    deduplicated_articles = _remove_duplicates(normalized_articles)

    grouped_articles = classify_articles(deduplicated_articles)
    ranked_groups = _rank_grouped_articles(grouped_articles)
    topics = _build_topics(ranked_groups)

    topic_repository = repository or TopicRepository()
    topic_repository.save_topics([topic.to_dict() for topic in topics])

    _log_pipeline_statistics(
        feed_count=len(urls),
        downloaded_count=len(downloaded_articles),
        normalized_count=len(normalized_articles),
        deduplicated_count=len(deduplicated_articles),
        grouped_articles=grouped_articles,
        topic_count=len(topics),
    )

    logger.info("Topic discovery pipeline complete: {} topics saved", len(topics))
    return topics