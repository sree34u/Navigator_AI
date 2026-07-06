"""Utilities for ensuring required application directories exist."""

from __future__ import annotations

from pathlib import Path

from src.config import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


def get_required_directories() -> tuple[Path, ...]:
    """Return the collection of directories required by the application."""
    settings = get_settings()
    return (
        settings.data_dir,
        settings.raw_data_dir,
        settings.processed_data_dir,
        settings.cache_dir,
        settings.prompts_dir,
        settings.output_dir,
        settings.pdf_output_dir,
        settings.magazine_output_dir,
        settings.log_dir,
    )


def ensure_directory(directory: Path) -> None:
    """Create a single directory, including parents, if it does not exist."""
    directory.mkdir(parents=True, exist_ok=True)
    logger.debug("Ensured directory exists: {}", directory)


def ensure_all_directories(directories: tuple[Path, ...] | None = None) -> None:
    """Create all required application directories if they do not exist."""
    target_directories = directories or get_required_directories()
    for directory in target_directories:
        ensure_directory(directory)
    logger.info("All required directories are ready")