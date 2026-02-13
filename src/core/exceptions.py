"""
Custom exception hierarchy for Medical Intelligence Platform.

BRANCH-1: Core Utilities
Author: Boris (Claude Code)
"""

from typing import Optional


class MedicalIntelligencePlatformError(Exception):
    """Base exception for Medical Intelligence Platform."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[dict] = None,
    ):
        """
        Initialize exception.

        Args:
            message: Error message
            error_code: Error code for tracking
            details: Additional error details
        """
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}

        super().__init__(self.message)

    def to_dict(self) -> dict:
        """Convert exception to dictionary."""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details,
        }


# Configuration Errors
class ConfigurationError(MedicalIntelligencePlatformError):
    """Configuration error."""

    pass


class InvalidConfigurationError(ConfigurationError):
    """Invalid configuration parameter."""

    pass


# Extraction Errors
class ExtractionError(MedicalIntelligencePlatformError):
    """Base extraction error."""

    pass


class TelegramClientError(ExtractionError):
    """Telegram client error."""

    pass


class TelegramAuthenticationError(TelegramClientError):
    """Telegram authentication failed."""

    pass


class ChannelScrapingError(ExtractionError):
    """Channel scraping error."""

    pass


class MediaDownloadError(ExtractionError):
    """Media download error."""

    pass


# NLP Errors
class NLPError(MedicalIntelligencePlatformError):
    """Base NLP error."""

    pass


class ModelLoadingError(NLPError):
    """NLP model loading error."""

    pass


class ModelInferenceError(NLPError):
    """NLP model inference error."""

    pass


class MedicalTextProcessingError(NLPError):
    """Medical text processing error."""

    pass


class EntityExtractionError(NLPError):
    """Entity extraction error."""

    pass


class EntityLinkingError(NLPError):
    """Entity linking error."""

    pass


class TextClassificationError(NLPError):
    """Text classification error."""

    pass


# Database Errors
class DatabaseError(MedicalIntelligencePlatformError):
    """Base database error."""

    pass


class DatabaseConnectionError(DatabaseError):
    """Database connection error."""

    pass


class DatabaseOperationError(DatabaseError):
    """Database operation error."""

    pass


class DataValidationError(DatabaseError):
    """Data validation error."""

    pass


# API Errors
class APIError(MedicalIntelligencePlatformError):
    """Base API error."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[dict] = None,
    ):
        """Initialize API error."""
        super().__init__(message, error_code, details)
        self.status_code = status_code

    def to_dict(self) -> dict:
        """Convert to API response dictionary."""
        response = super().to_dict()
        response["status_code"] = self.status_code
        return response


class ValidationError(APIError):
    """Request validation error."""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, status_code=422, error_code="VALIDATION_ERROR", details=details)


class NotFoundError(APIError):
    """Resource not found error."""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, status_code=404, error_code="NOT_FOUND", details=details)


class UnauthorizedError(APIError):
    """Unauthorized error."""

    def __init__(self, message: str = "Unauthorized", details: Optional[dict] = None):
        super().__init__(message, status_code=401, error_code="UNAUTHORIZED", details=details)


class ForbiddenError(APIError):
    """Forbidden error."""

    def __init__(self, message: str = "Forbidden", details: Optional[dict] = None):
        super().__init__(message, status_code=403, error_code="FORBIDDEN", details=details)


class ConflictError(APIError):
    """Resource conflict error."""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, status_code=409, error_code="CONFLICT", details=details)


class RateLimitError(APIError):
    """Rate limit exceeded error."""

    def __init__(self, message: str = "Rate limit exceeded", details: Optional[dict] = None):
        super().__init__(message, status_code=429, error_code="RATE_LIMIT", details=details)


# Transformation Errors
class TransformationError(MedicalIntelligencePlatformError):
    """Base transformation error."""

    pass


class DataQualityError(TransformationError):
    """Data quality check failed."""

    pass


class DBTExecutionError(TransformationError):
    """dbt execution error."""

    pass


# Retry Error
class RetryableError(MedicalIntelligencePlatformError):
    """Error that should trigger a retry."""

    pass


def is_retryable(error: Exception) -> bool:
    """
    Check if error is retryable.

    Args:
        error: Exception instance

    Returns:
        bool: True if error should be retried
    """
    retryable_types = (
        RetryableError,
        TelegramClientError,
        MediaDownloadError,
        DatabaseConnectionError,
        ModelInferenceError,
    )
    return isinstance(error, retryable_types)