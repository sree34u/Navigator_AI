"""Application entry point for the UPSC Current Affairs Magazine Generator."""

from __future__ import annotations

import sys

from src.agents.topic_finder import find_topics
from src.config import get_settings
from src.utils.logger import get_logger, log_stage

logger = get_logger(__name__)


def bootstrap() -> None:
    """Initialize configuration, logging, and required directories."""
    settings = get_settings()
    settings.ensure_directories()

    logger.info("Starting {}", settings.app_name)
    logger.info("Environment: {}", settings.environment)
    logger.info("LLM provider: {}", settings.llm_provider)
    logger.info("Data directory: {}", settings.data_dir)
    logger.info("Output directory: {}", settings.output_dir)
    logger.info("Log directory: {}", settings.log_dir)
    logger.info("{} initialized successfully", settings.app_name)


def _display_summary(topics: list) -> None:
    """Display a concise execution summary of the topic discovery pipeline."""
    print("=" * 60)
    print("UPSC Current Affairs Magazine Generator - Execution Summary")
    print("=" * 60)
    print(f"Total topics generated: {len(topics)}")

    if topics:
        category_counts: dict[str, int] = {}
        for topic in topics:
            category = getattr(topic, "category", None)
            category_value = category.value if category else "unknown"
            category_counts[category_value] = (
                category_counts.get(category_value, 0) + 1
            )

        print("Topics by category:")
        for category_value, count in sorted(
            category_counts.items(), key=lambda pair: pair[1], reverse=True
        ):
            print(f"  {category_value}: {count}")
    else:
        print("No topics were generated in this run.")

    print("=" * 60)


def main() -> int:
    """Run the complete topic discovery pipeline and display a summary."""
    bootstrap()

    try:
        with log_stage("topic_discovery_pipeline", logger=logger):
            topics = find_topics()
    except Exception:
        logger.exception("Topic discovery pipeline failed")
        return 1

    _display_summary(topics)
    logger.info("Application run completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())