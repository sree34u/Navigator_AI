"""Reusable application logging configuration using loguru."""

from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger as _logger

from src.config import get_settings

_CONFIGURED = False


def _configure_logger() -> None:
    """Configure loguru sinks for console and rotating daily file logging."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    settings = get_settings()
    log_dir: Path = settings.log_dir
    log_dir.mkdir(parents=True, exist_ok=True)

    _logger.remove()

    _logger.add(
        sys.stderr,
        level=settings.log_level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> "
            "- <level>{message}</level>"
        ),
        colorize=True,
        backtrace=False,
        diagnose=False,
    )

    _logger.add(
        log_dir / "app_{time:YYYY-MM-DD}.log",
        level=settings.log_level,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
            "{name}:{function}:{line} - {message}"
        ),
        rotation=settings.log_rotation,
        retention=settings.log_retention,
        compression="zip",
        encoding="utf-8",
        backtrace=True,
        diagnose=False,
        enqueue=True,
    )

    _CONFIGURED = True


def get_logger(name: str) -> "_logger.__class__":
    """Return a configured logger instance bound to the given module name."""
    _configure_logger()
    return _logger.bind(module=name)