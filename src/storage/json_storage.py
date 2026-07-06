"""Generic reusable JSON storage utility for saving and loading data."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, TypeVar

from src.utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class JSONStorageError(Exception):
    """Raised when JSON data cannot be saved or loaded."""


def _default_serializer(obj: Any) -> Any:
    """Serialize non-JSON-native objects such as dataclasses and paths."""
    if is_dataclass(obj) and not isinstance(obj, type):
        return asdict(obj)
    if isinstance(obj, Path):
        return str(obj)
    if hasattr(obj, "to_dict") and callable(obj.to_dict):
        return obj.to_dict()
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def save_json(data: Any, file_path: Path, indent: int = 2) -> None:
    """Save arbitrary data as JSON to the given file path."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with file_path.open("w", encoding="utf-8") as file_handle:
            json.dump(
                data,
                file_handle,
                indent=indent,
                ensure_ascii=False,
                default=_default_serializer,
            )
    except (OSError, TypeError) as exc:
        logger.error("Failed to save JSON to {}: {}", file_path, exc)
        raise JSONStorageError(f"Failed to save JSON to {file_path}") from exc

    logger.debug("Saved JSON data to {}", file_path)


def load_json(file_path: Path) -> Any:
    """Load JSON data from the given file path."""
    if not file_path.exists():
        raise JSONStorageError(f"JSON file does not exist: {file_path}")

    try:
        with file_path.open("r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
    except (OSError, json.JSONDecodeError) as exc:
        logger.error("Failed to load JSON from {}: {}", file_path, exc)
        raise JSONStorageError(f"Failed to load JSON from {file_path}") from exc

    logger.debug("Loaded JSON data from {}", file_path)
    return data


def load_json_or_default(file_path: Path, default: T) -> T | Any:
    """Load JSON data from a file path, returning a default if it does not exist."""
    if not file_path.exists():
        logger.debug("JSON file {} not found, returning default", file_path)
        return default
    return load_json(file_path)


def delete_json(file_path: Path) -> None:
    """Delete a JSON file if it exists."""
    if file_path.exists():
        file_path.unlink()
        logger.debug("Deleted JSON file: {}", file_path)