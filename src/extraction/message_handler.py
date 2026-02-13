"""Message parsing and handling."""
from typing import Dict, Any, Optional
from datetime import datetime
from ..core.logger import get_logger
logger = get_logger(name)
class MessageHandler:
"""Handle and parse Telegram messages."""
@staticmethod
def parse_message(message: Dict[str, Any]) -> Dict[str, Any]:
    """Parse raw message to structured format."""
    return {
        "id": message.get("id"),
        "text": message.get("text", "").strip(),
        "date": message.get("date"),
        "views": message.get("views", 0),
        "forwards": message.get("forwards", 0),
        "sender_id": message.get("sender_id"),
        "has_media": message.get("media", False),
        "media_type": message.get("media_type"),
    }

@staticmethod
def extract_urls(text: str) -> list:
    """Extract URLs from text."""
    import re
    pattern = r'https?://[^\s]+'
    return re.findall(pattern, text)

@staticmethod
def extract_mentions(text: str) -> list:
    """Extract @mentions from text."""
    import re
    pattern = r'@\w+'
    return re.findall(pattern, text)

@staticmethod
def extract_hashtags(text: str) -> list:
    """Extract #hashtags from text."""
    import re
    pattern = r'#\w+'
    return re.findall(pattern, text)

@staticmethod
def clean_text(text: str) -> str:
    """Clean and normalize text."""
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Remove special characters but keep punctuation
    return text