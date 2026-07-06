"""Workflow orchestrating the monthly topic discovery execution."""

from __future__ import annotations

from datetime import datetime, timezone

from src.agents.topic_finder import find_topics
from src.models.topic import Topic
from src.utils.logger import get_logger

logger = get_logger(__name__)


def run_monthly_workflow() -> list[Topic]:
    """Execute the monthly topic discovery workflow end to end."""
    started_at = datetime.now(tz=timezone.utc)
    logger.info("Monthly workflow started at {}", started_at.isoformat())

    try:
        topics = find_topics()
    except Exception as exc:
        logger.exception("Monthly workflow failed: {}", exc)
        raise

    finished_at = datetime.now(tz=timezone.utc)
    duration_seconds = (finished_at - started_at).total_seconds()

    logger.info(
        "Monthly workflow completed at {} ({} topics, {:.2f}s duration)",
        finished_at.isoformat(),
        len(topics),
        duration_seconds,
    )
    return topics


if __name__ == "__main__":
    run_monthly_workflow()