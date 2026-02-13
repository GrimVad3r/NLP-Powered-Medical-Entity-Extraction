"""
Input validators and data validation utilities.

BRANCH-1: Core Utilities
Author: Boris (Claude Code)
"""

import re
from typing import Any, Optional, List

from .logger import get_logger

logger = get_logger(__name__)


class Validators:
    """Input validation utility class."""

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email address format.

        Args:
            email: Email address

        Returns:
            True if valid email
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        Validate phone number format.

        Args:
            phone: Phone number with country code

        Returns:
            True if valid phone
        """
        # Remove spaces and dashes
        clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
        # Check if it's a valid format (starts with + and has 10-15 digits)
        return bool(re.match(r'^\+\d{10,15}$', clean_phone))

    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Validate URL format.

        Args:
            url: URL string

        Returns:
            True if valid URL
        """
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, url))

    @staticmethod
    def validate_text_length(
        text: str,
        min_length: int = 1,
        max_length: int = 5000
    ) -> bool:
        """
        Validate text length is within range.

        Args:
            text: Input text
            min_length: Minimum length
            max_length: Maximum length

        Returns:
            True if length is valid
        """
        return min_length <= len(text) <= max_length

    @staticmethod
    def validate_number_range(
        value: float,
        min_val: float,
        max_val: float
    ) -> bool:
        """
        Validate number is within range.

        Args:
            value: Number to validate
            min_val: Minimum value
            max_val: Maximum value

        Returns:
            True if in range
        """
        return min_val <= value <= max_val

    @staticmethod
    def validate_enum(value: str, allowed_values: List[str]) -> bool:
        """
        Validate value is in allowed list.

        Args:
            value: Value to check
            allowed_values: List of allowed values

        Returns:
            True if value is allowed
        """
        return value in allowed_values

    @staticmethod
    def validate_ip_address(ip: str) -> bool:
        """
        Validate IP address format.

        Args:
            ip: IP address

        Returns:
            True if valid IP
        """
        # IPv4 validation
        ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if re.match(ipv4_pattern, ip):
            parts = ip.split('.')
            return all(0 <= int(part) <= 255 for part in parts)

        # IPv6 validation (simplified)
        ipv6_pattern = r'^[0-9a-fA-F:]{2,}$'
        return bool(re.match(ipv6_pattern, ip))

    @staticmethod
    def validate_date_format(date_str: str, format_str: str = "%Y-%m-%d") -> bool:
        """
        Validate date format.

        Args:
            date_str: Date string
            format_str: Expected format

        Returns:
            True if valid date
        """
        from datetime import datetime

        try:
            datetime.strptime(date_str, format_str)
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_json(json_str: str) -> bool:
        """
        Validate JSON format.

        Args:
            json_str: JSON string

        Returns:
            True if valid JSON
        """
        import json

        try:
            json.loads(json_str)
            return True
        except json.JSONDecodeError:
            return False

    @staticmethod
    def validate_required_fields(data: dict, required_fields: List[str]) -> bool:
        """
        Validate required fields exist in dictionary.

        Args:
            data: Dictionary to check
            required_fields: List of required field names

        Returns:
            True if all required fields present
        """
        for field in required_fields:
            if field not in data or data[field] is None:
                logger.warning(f"Missing required field: {field}")
                return False

        return True


def validate_telegram_channel_name(name: str) -> bool:
    """
    Validate Telegram channel name format.

    Args:
        name: Channel name

    Returns:
        True if valid Telegram channel name
    """
    # Telegram channel names are alphanumeric and underscores
    pattern = r'^[a-zA-Z0-9_]{5,32}$'
    return bool(re.match(pattern, name))


def validate_confidence_score(score: float) -> bool:
    """
    Validate confidence score is between 0 and 1.

    Args:
        score: Confidence score

    Returns:
        True if valid
    """
    return Validators.validate_number_range(score, 0.0, 1.0)


def validate_entity_type(entity_type: str) -> bool:
    """
    Validate entity type is in allowed list.

    Args:
        entity_type: Entity type string

    Returns:
        True if valid entity type
    """
    valid_types = [
        "MEDICATION",
        "DOSAGE",
        "CONDITION",
        "SYMPTOM",
        "PRICE",
        "FREQUENCY",
        "FACILITY",
        "SIDE_EFFECT",
    ]
    return Validators.validate_enum(entity_type, valid_types)


def validate_message_text(text: str) -> bool:
    """
    Validate message text.

    Args:
        text: Message text

    Returns:
        True if valid
    """
    if not isinstance(text, str):
        return False

    if not text.strip():
        return False

    return Validators.validate_text_length(text, min_length=1, max_length=5000)


def validate_product_name(name: str) -> bool:
    """
    Validate product name.

    Args:
        name: Product name

    Returns:
        True if valid
    """
    if not isinstance(name, str):
        return False

    # Product names should be 2-200 characters, alphanumeric + spaces
    pattern = r'^[a-zA-Z0-9\s\-]{2,200}$'
    return bool(re.match(pattern, name))


def validate_price(price: float) -> bool:
    """
    Validate price value.

    Args:
        price: Price value

    Returns:
        True if valid
    """
    return Validators.validate_number_range(price, 0.0, 1000000.0)


class SchemaValidator:
    """Validate data against schema."""

    @staticmethod
    def validate_message_schema(data: dict) -> tuple[bool, Optional[str]]:
        """
        Validate message data schema.

        Args:
            data: Message data dictionary

        Returns:
            (is_valid, error_message)
        """
        required_fields = ["text", "date"]

        if not Validators.validate_required_fields(data, required_fields):
            return False, "Missing required fields"

        if not validate_message_text(data["text"]):
            return False, "Invalid message text"

        return True, None

    @staticmethod
    def validate_entity_schema(data: dict) -> tuple[bool, Optional[str]]:
        """
        Validate entity data schema.

        Args:
            data: Entity data dictionary

        Returns:
            (is_valid, error_message)
        """
        required_fields = ["text", "entity_type"]

        if not Validators.validate_required_fields(data, required_fields):
            return False, "Missing required fields"

        if not validate_entity_type(data["entity_type"]):
            return False, "Invalid entity type"

        if "confidence" in data and not validate_confidence_score(data["confidence"]):
            return False, "Invalid confidence score"

        return True, None

    @staticmethod
    def validate_product_schema(data: dict) -> tuple[bool, Optional[str]]:
        """
        Validate product data schema.

        Args:
            data: Product data dictionary

        Returns:
            (is_valid, error_message)
        """
        required_fields = ["name", "category"]

        if not Validators.validate_required_fields(data, required_fields):
            return False, "Missing required fields"

        if not validate_product_name(data["name"]):
            return False, "Invalid product name"

        if "avg_price" in data and not validate_price(data["avg_price"]):
            return False, "Invalid price"

        return True, None