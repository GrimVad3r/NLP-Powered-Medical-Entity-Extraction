"""
API security utilities and authentication.

BRANCH-6: REST API
Author: Boris (Claude Code)
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
import jwt
from datetime import datetime, timedelta
import hashlib

from ..core.config import get_settings
from ..core.logger import get_logger

logger = get_logger(__name__)

security = HTTPBearer()
settings = get_settings()


class TokenManager:
    """Manage JWT tokens."""

    def __init__(self, secret_key: str = None, algorithm: str = "HS256"):
        self.secret_key = secret_key or settings.secret_key
        self.algorithm = algorithm

    def create_token(self, data: dict, expires_in_hours: int = 24) -> str:
        """
        Create JWT token.

        Args:
            data: Token payload
            expires_in_hours: Token expiration time

        Returns:
            JWT token string
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(hours=expires_in_hours)
        to_encode.update({"exp": expire})

        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            logger.debug("Token created successfully")
            return encoded_jwt
        except Exception as e:
            logger.error(f"Token creation failed: {e}")
            raise

    def verify_token(self, token: str) -> dict:
        """
        Verify JWT token.

        Args:
            token: JWT token string

        Returns:
            Token payload

        Raises:
            HTTPException: If token is invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
            )
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )


class PasswordManager:
    """Manage password hashing and verification."""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash password.

        Args:
            password: Plain password

        Returns:
            Hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verify password.

        Args:
            password: Plain password
            hashed_password: Hashed password

        Returns:
            True if password matches
        """
        return hashlib.sha256(password.encode()).hexdigest() == hashed_password


async def verify_api_key(credentials: Optional[HTTPAuthCredentials] = Depends(security)) -> str:
    """
    Verify API key.

    Args:
        credentials: HTTP bearer credentials

    Returns:
        API key

    Raises:
        HTTPException: If API key is invalid
    """
    if not settings.api_key:
        # No API key required
        return "default"

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )

    if credentials.credentials != settings.api_key:
        logger.warning("Invalid API key attempted")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )

    logger.debug("API key verified")
    return credentials.credentials


async def verify_token(credentials: Optional[HTTPAuthCredentials] = Depends(security)) -> dict:
    """
    Verify JWT token.

    Args:
        credentials: HTTP bearer credentials

    Returns:
        Token payload

    Raises:
        HTTPException: If token is invalid
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing credentials",
        )

    token_manager = TokenManager()

    try:
        payload = token_manager.verify_token(credentials.credentials)
        logger.debug("Token verified")
        return payload
    except HTTPException:
        raise


def check_rate_limit(request_count: int, limit: int = 100) -> bool:
    """
    Check if request count exceeds limit.

    Args:
        request_count: Current request count
        limit: Rate limit

    Returns:
        True if within limit
    """
    return request_count < limit


class SecurityHeaders:
    """Add security headers to response."""

    @staticmethod
    def get_security_headers() -> dict:
        """
        Get security headers.

        Returns:
            Dictionary of security headers
        """
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
        }


class InputValidator:
    """Validate user input."""

    @staticmethod
    def validate_string(value: str, min_length: int = 1, max_length: int = 1000) -> bool:
        """
        Validate string input.

        Args:
            value: Input string
            min_length: Minimum length
            max_length: Maximum length

        Returns:
            True if valid
        """
        if not isinstance(value, str):
            return False

        return min_length <= len(value) <= max_length

    @staticmethod
    def validate_integer(value: int, min_val: int = 0, max_val: int = 1000000) -> bool:
        """
        Validate integer input.

        Args:
            value: Input integer
            min_val: Minimum value
            max_val: Maximum value

        Returns:
            True if valid
        """
        if not isinstance(value, int):
            return False

        return min_val <= value <= max_val

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email address.

        Args:
            email: Email address

        Returns:
            True if valid email format
        """
        import re

        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def sanitize_string(value: str) -> str:
        """
        Sanitize string input (remove dangerous characters).

        Args:
            value: Input string

        Returns:
            Sanitized string
        """
        # Remove common SQL injection patterns
        dangerous_patterns = ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_"]

        for pattern in dangerous_patterns:
            value = value.replace(pattern, "")

        return value