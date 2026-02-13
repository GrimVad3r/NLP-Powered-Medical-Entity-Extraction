#!/usr/bin/env python3
"""
Run Telegram extraction pipeline.

Author: Boris (Claude Code)
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import get_settings
from src.core.logger import get_logger
from src.extraction.telegram_client import create_telegram_client
from src.extraction.channel_scraper import ChannelScraper

logger = get_logger(__name__)


async def run_extraction(
    channels: list,
    limit: int = 1000,
    keywords: list = None,
):
    """
    Run extraction pipeline.

    Args:
        channels: List of channels to scrape
        limit: Messages per channel
        keywords: Optional keywords to filter
    """
    try:
        logger.info("=" * 60)
        logger.info("Telegram Extraction Pipeline")
        logger.info("=" * 60)

        # Create Telegram client
        logger.info("Connecting to Telegram...")
        client = await create_telegram_client()

        # Create scraper
        scraper = ChannelScraper(client)

        # Scrape channels
        logger.info(f"Scraping {len(channels)} channels...")
        all_results = await scraper.scrape_multiple_channels(channels, limit=limit)

        # Log results
        total_messages = sum(len(msgs) for msgs in all_results.values())
        logger.info(f"✅ Total messages scraped: {total_messages}")

        for channel, messages in all_results.items():
            logger.info(f"  - {channel}: {len(messages)} messages")

        # Get channel stats
        logger.info("\nChannel Statistics:")
        for channel in channels:
            try:
                stats = await scraper.get_channel_stats(channel)
                logger.info(f"\n{channel}:")
                logger.info(f"  Participants: {stats['participants']}")
                logger.info(f"  Avg Views: {stats['avg_views']:.0f}")
                logger.info(f"  Avg Forwards: {stats['avg_forwards']:.0f}")
                logger.info(f"  Media %: {stats['media_percentage']:.1f}%")
            except Exception as e:
                logger.warning(f"  Error getting stats: {e}")

        # Disconnect
        await client.disconnect()

        logger.info("\n" + "=" * 60)
        logger.info("Extraction completed successfully!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ Extraction failed: {str(e)}")
        raise


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Telegram extraction pipeline")
    parser.add_argument(
        "--channels",
        nargs="+",
        help="Channel names to scrape",
        default=None
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=1000,
        help="Messages per channel"
    )
    parser.add_argument(
        "--keywords",
        nargs="+",
        help="Keywords to filter",
        default=None
    )

    args = parser.parse_args()

    # Get channels from config if not provided
    channels = args.channels or get_settings().telegram_channels

    logger.info(f"Channels: {channels}")
    logger.info(f"Limit: {args.limit}")
    if args.keywords:
        logger.info(f"Keywords: {args.keywords}")

    # Run extraction
    if sys.version_info >= (3, 7):
        asyncio.run(run_extraction(channels, args.limit, args.keywords))
    else:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_extraction(channels, args.limit, args.keywords))


if __name__ == "__main__":
    main()