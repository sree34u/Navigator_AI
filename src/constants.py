"""Reusable constant values used across the application."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Final

BASE_DIR: Final[Path] = Path(__file__).resolve().parent.parent

DATA_DIR: Final[Path] = BASE_DIR / "data"
RAW_DATA_DIR: Final[Path] = DATA_DIR / "raw"
PROCESSED_DATA_DIR: Final[Path] = DATA_DIR / "processed"
CACHE_DIR: Final[Path] = DATA_DIR / "cache"
DB_DIR: Final[Path] = DATA_DIR / "db"

CONFIG_DIR: Final[Path] = BASE_DIR / "config"
PROMPTS_DIR: Final[Path] = CONFIG_DIR / "prompts"

OUTPUT_DIR: Final[Path] = BASE_DIR / "output"
PDF_OUTPUT_DIR: Final[Path] = OUTPUT_DIR / "pdf"
MAGAZINE_OUTPUT_DIR: Final[Path] = OUTPUT_DIR / "magazines"

LOG_DIR: Final[Path] = BASE_DIR / "logs"

DEFAULT_DB_FILENAME: Final[str] = "app.db"
DEFAULT_SETTINGS_FILENAME: Final[str] = "settings.py"
DEFAULT_LOGGING_CONFIG_FILENAME: Final[str] = "logging.yaml"

PROMPT_FILE_SUMMARIZER: Final[str] = "summarizer.yaml"
PROMPT_FILE_EDITORIAL: Final[str] = "editorial.yaml"
PROMPT_FILE_MCQ_GENERATOR: Final[str] = "mcq_generator.yaml"
PROMPT_FILE_MAGAZINE_LAYOUT: Final[str] = "magazine_layout.yaml"

MAGAZINE_TEMPLATE_FILENAME: Final[str] = "magazine_template.html"
MAGAZINE_STYLES_FILENAME: Final[str] = "styles.css"


class UPSCCategory(StrEnum):
    """Standard UPSC current affairs subject categories."""

    POLITY = "polity"
    ECONOMY = "economy"
    ENVIRONMENT = "environment"
    SCIENCE_AND_TECHNOLOGY = "science_and_technology"
    INTERNATIONAL_RELATIONS = "international_relations"
    GEOGRAPHY = "geography"
    HISTORY = "history"
    ART_AND_CULTURE = "art_and_culture"
    SOCIAL_ISSUES = "social_issues"
    ETHICS = "ethics"
    GOVERNANCE = "governance"
    SECURITY = "security"
    DISASTER_MANAGEMENT = "disaster_management"
    MISCELLANEOUS = "miscellaneous"


class ArticleFormat(StrEnum):
    """Supported source article content formats."""

    HTML = "html"
    JSON = "json"
    XML = "xml"
    PLAIN_TEXT = "plain_text"


class ExportFormat(StrEnum):
    """Supported magazine export formats."""

    PDF = "pdf"
    HTML = "html"
    MARKDOWN = "markdown"


class LLMProvider(StrEnum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"


SUPPORTED_RSS_MIME_TYPES: Final[tuple[str, ...]] = (
    "application/rss+xml",
    "application/xml",
    "application/atom+xml",
    "text/xml",
)

SUPPORTED_IMAGE_EXTENSIONS: Final[tuple[str, ...]] = (
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
)

SUPPORTED_DOCUMENT_EXTENSIONS: Final[tuple[str, ...]] = (
    ".pdf",
    ".html",
    ".md",
)

DEFAULT_RSS_TIMEOUT_SECONDS: Final[int] = 30
DEFAULT_RSS_MAX_ARTICLES_PER_FEED: Final[int] = 20
DEFAULT_RSS_USER_AGENT: Final[str] = (
    "Mozilla/5.0 (compatible; UPSCMagazineBot/1.0; "
    "+https://github.com/upsc-current-affairs-generator)"
)
DEFAULT_RSS_RETRY_ATTEMPTS: Final[int] = 3
DEFAULT_RSS_RETRY_BACKOFF_SECONDS: Final[float] = 2.0

DEFAULT_RSS_FEEDS: Final[tuple[str, ...]] = (
    "https://www.thehindu.com/news/national/feeder/default.rss",
    "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3",
    "https://www.livemint.com/rss/news",
)

MIN_ARTICLE_WORD_COUNT: Final[int] = 50
MAX_ARTICLE_WORD_COUNT: Final[int] = 5000

DEFAULT_ENCODING: Final[str] = "utf-8"