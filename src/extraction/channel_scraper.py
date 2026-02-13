"""
Channel scraper for Telegram data collection.

BRANCH-2: Data Extraction
Author: Boris (Claude Code)
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from src.core.logger import get_logger
from src.core.exceptions import ChannelScrapingError
from src.extraction.telegram_client import TelegramClientWrapper

logger = get_logger(__name__)


class ChannelScraper:
    """Scrape messages from Telegram channels."""

    def __init__(self, telegram_client: TelegramClientWrapper):
        """
        Initialize scraper.

        Args:
            telegram_client: Connected Telegram client
        """
        self.client = telegram_client
        self.logger = logger

    async def scrape_channel(
        self,
        channel: str,
        limit: int = 1000,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        keywords: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Scrape messages from a channel.

        Args:
            channel: Channel name or ID
            limit: Maximum messages to retrieve
            start_date: Filter messages after this date
            end_date: Filter messages before this date
            keywords: Filter by keywords in text

        Returns:
            List of scraped messages

        Raises:
            ChannelScrapingError: If scraping fails
        """
        try:
            self.logger.info(f"Starting scrape of {channel} (limit={limit})")

            messages = await self.client.get_messages(channel, limit=limit)

            # Filter by date
            if start_date or end_date:
                messages = self._filter_by_date(messages, start_date, end_date)

            # Filter by keywords
            if keywords:
                messages = self._filter_by_keywords(messages, keywords)

            self.logger.info(f"Scraped {len(messages)} messages from {channel}")
            return messages

        except Exception as e:
            raise ChannelScrapingError(
                f"Failed to scrape {channel}: {str(e)}",
                details={"channel": channel, "limit": limit}
            )

    def _filter_by_date(
        self,
        messages: List[Dict[str, Any]],
        start_date: Optional[datetime],
        end_date: Optional[datetime],
    ) -> List[Dict[str, Any]]:
        """Filter messages by date range."""
        filtered = []

        for msg in messages:
            msg_date = msg.get("date")
            if not msg_date:
                continue

            if start_date and msg_date < start_date:
                continue

            if end_date and msg_date > end_date:
                continue

            filtered.append(msg)

        self.logger.debug(f"Filtered to {len(filtered)} messages by date")
        return filtered

    def _filter_by_keywords(
        self,
        messages: List[Dict[str, Any]],
        keywords: List[str],
    ) -> List[Dict[str, Any]]:
        """Filter messages by keywords."""
        filtered = []
        keywords_lower = [k.lower() for k in keywords]

        for msg in messages:
            text = msg.get("text", "").lower()

            if any(keyword in text for keyword in keywords_lower):
                filtered.append(msg)

        self.logger.debug(f"Filtered to {len(filtered)} messages by keywords")
        return filtered

    async def scrape_multiple_channels(
        self,
        channels: List[str],
        limit: int = 1000,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Scrape multiple channels.

        Args:
            channels: List of channel names
            limit: Messages per channel

        Returns:
            Dictionary with channel names as keys
        """
        results = {}

        for channel in channels:
            try:
                messages = await self.scrape_channel(channel, limit=limit)
                results[channel] = messages
            except Exception as e:
                self.logger.error(f"Error scraping {channel}: {e}")
                results[channel] = []

        return results

    async def get_channel_stats(self, channel: str) -> Dict[str, Any]:
        """
        Get channel statistics.

        Args:
            channel: Channel name

        Returns:
            Statistics dictionary
        """
        try:
            info = await self.client.get_channel_info(channel)
            messages = await self.client.get_messages(channel, limit=100)

            total_views = sum(m.get("views", 0) for m in messages)
            total_forwards = sum(m.get("forwards", 0) for m in messages)
            media_count = sum(1 for m in messages if m.get("media"))

            return {
                "channel_name": info.get("name"),
                "channel_id": info.get("id"),
                "participants": info.get("participants"),
                "description": info.get("description"),
                "messages_sampled": len(messages),
                "total_views_sample": total_views,
                "total_forwards_sample": total_forwards,
                "media_count_sample": media_count,
                "avg_views": total_views / len(messages) if messages else 0,
                "avg_forwards": total_forwards / len(messages) if messages else 0,
                "media_percentage": (media_count / len(messages) * 100) if messages else 0,
            }

        except Exception as e:
            self.logger.error(f"Error getting stats for {channel}: {e}")
            raise ChannelScrapingError(f"Failed to get stats: {str(e)}")