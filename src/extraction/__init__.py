"""Data extraction module."""
from .telegram_client import TelegramClientWrapper, create_telegram_client
from .channel_scraper import ChannelScraper
all = [
"TelegramClientWrapper",
"create_telegram_client",
"ChannelScraper",
]
