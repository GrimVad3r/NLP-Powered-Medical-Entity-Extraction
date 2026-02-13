"""
Unit tests for configuration module.

Tests settings loading, validation, and caching.
"""

import pytest
import os
from unittest.mock import patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.config import Settings, get_settings


class TestSettings:
    """Test Settings class."""

    def test_settings_creation(self):
        """Test creating settings."""
        settings = Settings()

        assert settings is not None
        assert hasattr(settings, "database_url")
        assert hasattr(settings, "api_key")

    def test_default_database_url(self):
        """Test default database URL."""
        settings = Settings()

        assert settings.database_url is not None
        assert "sqlite" in settings.database_url or "postgresql" in settings.database_url

    def test_api_settings(self):
        """Test API settings."""
        settings = Settings()

        assert hasattr(settings, "api_host")
        assert hasattr(settings, "api_port")
        assert settings.api_port > 0

    def test_logging_settings(self):
        """Test logging settings."""
        settings = Settings()

        assert hasattr(settings, "log_level")
        assert settings.log_level in ["DEBUG", "INFO", "WARNING", "ERROR"]

    def test_nlp_settings(self):
        """Test NLP settings."""
        settings = Settings()

        assert hasattr(settings, "nlp_model_name")
        assert settings.nlp_model_name == "en_core_sci_md"

    def test_database_settings(self):
        """Test database settings."""
        settings = Settings()

        assert hasattr(settings, "db_pool_size")
        assert hasattr(settings, "db_max_overflow")
        assert settings.db_pool_size > 0

    @patch.dict(os.environ, {"API_KEY": "test_key_123"})
    def test_environment_variable_loading(self):
        """Test loading from environment variables."""
        settings = Settings()

        # Should load from environment
        assert settings.api_key == "test_key_123"

    def test_settings_validation(self):
        """Test settings validation."""
        try:
            settings = Settings()
            assert settings is not None
        except ValueError as e:
            pytest.fail(f"Settings validation failed: {e}")


class TestSettingsCaching:
    """Test settings caching."""

    def test_get_settings_returns_same_instance(self):
        """Test get_settings returns cached instance."""
        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2

    def test_settings_attributes_consistent(self):
        """Test settings attributes are consistent."""
        settings = get_settings()

        api_key_1 = settings.api_key
        api_key_2 = get_settings().api_key

        assert api_key_1 == api_key_2


class TestDatabaseConfiguration:
    """Test database configuration."""

    def test_database_url_format(self):
        """Test database URL format."""
        settings = Settings()

        # Should be valid SQLAlchemy URL
        assert "://" in settings.database_url

    def test_database_pool_settings(self):
        """Test database pool settings."""
        settings = Settings()

        assert settings.db_pool_size > 0
        assert settings.db_max_overflow >= 0
        assert settings.db_pool_size <= settings.db_pool_size + settings.db_max_overflow

    def test_database_timeout(self):
        """Test database timeout setting."""
        settings = Settings()

        assert hasattr(settings, "db_timeout")
        assert settings.db_timeout > 0


class TestTelegramConfiguration:
    """Test Telegram configuration."""

    def test_telegram_settings_exist(self):
        """Test Telegram settings exist."""
        settings = Settings()

        assert hasattr(settings, "telegram_api_id")
        assert hasattr(settings, "telegram_api_hash")
        assert hasattr(settings, "telegram_phone_number")

    def test_telegram_rate_limit(self):
        """Test Telegram rate limit."""
        settings = Settings()

        assert hasattr(settings, "telegram_rate_limit")
        assert settings.telegram_rate_limit > 0


class TestAPIConfiguration:
    """Test API configuration."""

    def test_api_host(self):
        """Test API host configuration."""
        settings = Settings()

        assert settings.api_host is not None
        # Should be localhost or 0.0.0.0 for development
        assert settings.api_host in ["localhost", "0.0.0.0", "127.0.0.1"]

    def test_api_port(self):
        """Test API port configuration."""
        settings = Settings()

        assert 1000 < settings.api_port < 65535

    def test_api_base_url(self):
        """Test API base URL."""
        settings = Settings()

        assert hasattr(settings, "api_base_url")


class TestLoggingConfiguration:
    """Test logging configuration."""

    def test_log_level_valid(self):
        """Test log level is valid."""
        settings = Settings()

        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        assert settings.log_level in valid_levels

    def test_log_file_path(self):
        """Test log file path."""
        settings = Settings()

        assert hasattr(settings, "log_file")

    def test_log_format(self):
        """Test log format."""
        settings = Settings()

        assert hasattr(settings, "log_format")


class TestFeatureFlags:
    """Test feature flags."""

    def test_feature_flags_exist(self):
        """Test feature flags exist."""
        settings = Settings()

        assert hasattr(settings, "enable_nlp")
        assert hasattr(settings, "enable_extraction")
        assert hasattr(settings, "enable_api")

    def test_feature_flags_boolean(self):
        """Test feature flags are boolean."""
        settings = Settings()

        assert isinstance(settings.enable_nlp, bool)
        assert isinstance(settings.enable_extraction, bool)
        assert isinstance(settings.enable_api, bool)