"""Application entry point for the UPSC Current Affairs Magazine Generator."""

from __future__ import annotations

from src.config import get_settings
from src.utils.logger import get_logger

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


def main() -> None:
    """Run application startup routine."""
    bootstrap()


if __name__ == "__main__":
    main()