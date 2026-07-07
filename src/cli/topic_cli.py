"""Command-line interface for managing UPSC topic discovery and inspection."""

from __future__ import annotations

import argparse
import sys
from collections import Counter

from src.agents.topic_finder import find_topics
from src.storage.topic_repository import TopicRepository
from src.utils.logger import get_logger

logger = get_logger(__name__)


def _build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with all supported subcommands."""
    parser = argparse.ArgumentParser(
        prog="topic-cli",
        description="CLI for the UPSC Current Affairs topic pipeline.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("fetch", help="Run the topic discovery pipeline.")
    subparsers.add_parser("stats", help="Show topic statistics.")
    subparsers.add_parser("categories", help="List all topic categories.")

    latest_parser = subparsers.add_parser(
        "latest", help="Show the most recently created topics."
    )
    latest_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of topics to display (default: 10).",
    )

    return parser


def _handle_fetch() -> int:
    """Run the topic discovery pipeline and report the outcome."""
    topics = find_topics()
    if not topics:
        logger.warning("Fetch completed with no topics generated")
        print("No topics were generated.")
        return 1

    print(f"Fetched and saved {len(topics)} topics.")
    return 0


def _handle_stats(repository: TopicRepository) -> int:
    """Display aggregate statistics about persisted topics."""
    topics = repository.load_topics()

    if not topics:
        print("No topics found. Run 'fetch' first.")
        return 0

    category_counts = Counter(topic.get("category", "unknown") for topic in topics)
    approved_count = sum(1 for topic in topics if topic.get("approved", False))
    unapproved_count = len(topics) - approved_count

    print(f"Total topics: {len(topics)}")
    print(f"Approved: {approved_count}")
    print(f"Unapproved: {unapproved_count}")
    print("Topics by category:")
    for category, count in sorted(
        category_counts.items(), key=lambda pair: pair[1], reverse=True
    ):
        print(f"  {category}: {count}")

    return 0


def _handle_categories(repository: TopicRepository) -> int:
    """Display all distinct topic categories currently present in storage."""
    topics = repository.load_topics()

    if not topics:
        print("No topics found. Run 'fetch' first.")
        return 0

    categories = sorted({topic.get("category", "unknown") for topic in topics})
    print("Available categories:")
    for category in categories:
        print(f"  {category}")

    return 0


def _handle_latest(repository: TopicRepository, limit: int) -> int:
    """Display the most recently created topics."""
    latest_topics = repository.get_latest(limit=limit)

    if not latest_topics:
        print("No topics found. Run 'fetch' first.")
        return 0

    print(f"Latest {len(latest_topics)} topics:")
    for topic in latest_topics:
        title = topic.get("title", "Untitled")
        category = topic.get("category", "unknown")
        created_at = topic.get("created_at", "unknown")
        print(f"  [{category}] {title} ({created_at})")

    return 0


def main(argv: list[str] | None = None) -> int:
    """Entry point for the topic CLI, dispatching to the requested subcommand."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    repository = TopicRepository()

    if args.command == "fetch":
        return _handle_fetch()
    if args.command == "stats":
        return _handle_stats(repository)
    if args.command == "categories":
        return _handle_categories(repository)
    if args.command == "latest":
        return _handle_latest(repository, limit=args.limit)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())