"""
Configuration management for Medical Intelligence Platform.

BRANCH-1: Core Utilities
Author: Boris (Claude Code)
"""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Application settings with validation."""

    # Application
    app_name: str = "Medical Intelligence Platform"
    app_version: str = "2.0.0"
    debug: bool = False
    environment: str = "development"

    # Database
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str = ""
    db_name: str = "medical_db"
    db_pool_size: int = 20
    db_max_overflow: int = 40
    db_echo: bool = False

    # Telegram
    telegram_api_id: int
    telegram_api_hash: str
    telegram_phone: str
    telegram_channels: list[str] = [
        "CheMedTelegram",
        "LobeliaCosmeticsOfficial",
        "TikvahPharma"
    ]

    # NLP
    nlp_use_gpu: bool = False
    nlp_models_dir: Path = Path("data/nlp_models")
    nlp_model_name: str = "en_core_sci_md"
    nlp_confidence_threshold: float = 0.6
    nlp_batch_size: int = 32

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = False
    api_workers: int = 4
    api_timeout: int = 30

    # Dashboard
    dashboard_port: int = 8501
    dashboard_theme: str = "light"

    # Logging
    log_level: str = "INFO"
    log_dir: Path = Path("logs")
    log_format: str = "json"  # "json" or "standard"
    log_retention_days: int = 30

    # Cache
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600
    redis_url: Optional[str] = None

    # Security
    api_key: Optional[str] = None
    secret_key: str = "change-me-in-production"
    cors_origins: list[str] = ["*"]

    # Feature flags
    enable_extraction: bool = True
    enable_nlp: bool = True
    enable_transformation: bool = True
    enable_api: bool = True
    enable_dashboard: bool = True

    @validator("db_pool_size", "db_max_overflow")
    def validate_pool_size(cls, v: int) -> int:
        """Validate database pool sizes."""
        if v < 1:
            raise ValueError("Pool size must be >= 1")
        return v

    @validator("nlp_confidence_threshold")
    def validate_confidence(cls, v: float) -> float:
        """Validate NLP confidence threshold."""
        if not (0.0 <= v <= 1.0):
            raise ValueError("Confidence threshold must be between 0 and 1")
        return v

    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()

    @property
    def database_url(self) -> str:
        """Get database connection URL."""
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def async_database_url(self) -> str:
        """Get async database connection URL."""
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment.lower() == "production"

    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment.lower() == "development"

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        Settings: Application settings

    Example:
        >>> settings = get_settings()
        >>> print(settings.app_name)
        Medical Intelligence Platform
    """
    return Settings()


if __name__ == "__main__":
    settings = get_settings()
    print(f"App: {settings.app_name} v{settings.app_version}")
    print(f"Database: {settings.database_url}")
    print(f"NLP GPU: {settings.nlp_use_gpu}")