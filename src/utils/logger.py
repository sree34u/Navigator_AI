"""Reusable application logging configuration using loguru."""

from __future__ import annotations

import functools
import sys
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any, ParamSpec, TypeVar

from loguru import logger as _logger

from src.config import get_settings

_CONFIGURED = False

P = ParamSpec("P")
R = TypeVar("R")


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

    _logger.add(
        log_dir / "errors_{time:YYYY-MM-DD}.log",
        level="ERROR",
        format=(
            "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
            "{name}:{function}:{line} - {message}"
        ),
        rotation=settings.log_rotation,
        retention=settings.log_retention,
        compression="zip",
        encoding="utf-8",
        backtrace=True,
        diagnose=True,
        enqueue=True,
    )

    _CONFIGURED = True


def get_logger(name: str) -> "_logger.__class__":
    """Return a configured logger instance bound to the given module name."""
    _configure_logger()
    return _logger.bind(module=name)


@contextmanager
def log_stage(stage_name: str, logger: Any | None = None) -> Iterator[None]:
    """Log the start, completion, duration, and any error of a pipeline stage."""
    active_logger = logger or get_logger("pipeline")
    active_logger.info("Stage started: {}", stage_name)
    start_time = time.perf_counter()

    try:
        yield
    except Exception as exc:
        elapsed_seconds = time.perf_counter() - start_time
        active_logger.error(
            "Stage failed: {} after {:.3f}s - {}", stage_name, elapsed_seconds, exc
        )
        raise
    else:
        elapsed_seconds = time.perf_counter() - start_time
        active_logger.info(
            "Stage completed: {} in {:.3f}s", stage_name, elapsed_seconds
        )


def log_execution_time(
    logger: Any | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorate a function to log its execution time and any raised errors."""

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        active_logger = logger or get_logger(func.__module__)

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
            except Exception as exc:
                elapsed_seconds = time.perf_counter() - start_time
                active_logger.error(
                    "Function '{}' failed after {:.3f}s - {}",
                    func.__qualname__,
                    elapsed_seconds,
                    exc,
                )
                raise
            else:
                elapsed_seconds = time.perf_counter() - start_time
                active_logger.info(
                    "Function '{}' completed in {:.3f}s",
                    func.__qualname__,
                    elapsed_seconds,
                )
                return result

        return wrapper

    return decorator


def log_error(message: str, exc: Exception, logger: Any | None = None) -> None:
    """Log an error message with exception details using the active logger."""
    active_logger = logger or get_logger("errors")
    active_logger.error("{}: {}", message, exc)