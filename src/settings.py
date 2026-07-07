"""Application configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Centralized application settings sourced from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="upsc-current-affairs-generator")
    environment: str = Field(default="development")
    debug: bool = Field(default=False)

    openai_api_key: str = Field(default="")
    anthropic_api_key: str = Field(default="")
    llm_provider: str = Field(default="anthropic")
    llm_model: str = Field(default="claude-sonnet-4-6")
    llm_max_tokens: int = Field(default=4096)
    llm_temperature: float = Field(default=0.3)
    llm_timeout_seconds: int = Field(default=60)
    llm_max_retries: int = Field(default=3)

    database_url: str = Field(
        default=f"sqlite:///{(BASE_DIR / 'data' / 'db' / 'app.db').as_posix()}"
    )

    rss_feed_urls: str = Field(default="")
    rss_fetch_timeout_seconds: int = Field(default=30)
    rss_max_articles_per_feed: int = Field(default=20)

    playwright_headless: bool = Field(default=True)
    playwright_timeout_ms: int = Field(default=30000)
    playwright_browser: str = Field(default="chromium")

    data_dir: Path = Field(default=BASE_DIR / "data")
    raw_data_dir: Path = Field(default=BASE_DIR / "data" / "raw")
    processed_data_dir: Path = Field(default=BASE_DIR / "data" / "processed")
    cache_dir: Path = Field(default=BASE_DIR / "data" / "cache")

    prompts_dir: Path = Field(default=BASE_DIR / "config" / "prompts")

    output_dir: Path = Field(default=BASE_DIR / "output")
    pdf_output_dir: Path = Field(default=BASE_DIR / "output" / "pdf")
    magazine_output_dir: Path = Field(default=BASE_DIR / "output" / "magazines")

    log_dir: Path = Field(default=BASE_DIR / "logs")
    log_level: str = Field(default="INFO")
    log_rotation: str = Field(default="10 MB")
    log_retention: str = Field(default="14 days")

    streamlit_server_port: int = Field(default=8501)
    streamlit_server_address: str = Field(default="0.0.0.0")

    def rss_feed_url_list(self) -> list[str]:
        """Return the configured RSS feed URLs as a list."""
        if not self.rss_feed_urls:
            return []
        return [url.strip() for url in self.rss_feed_urls.split(",") if url.strip()]

    def ensure_directories(self) -> None:
        """Create all configured filesystem directories if they do not exist."""
        directories = (
            self.data_dir,
            self.raw_data_dir,
            self.processed_data_dir,
            self.cache_dir,
            self.prompts_dir,
            self.output_dir,
            self.pdf_output_dir,
            self.magazine_output_dir,
            self.log_dir,
        )
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached singleton instance of the application settings."""
    settings = Settings()
    settings.ensure_directories()
    return settings