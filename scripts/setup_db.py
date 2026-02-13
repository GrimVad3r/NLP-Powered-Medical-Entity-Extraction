#!/usr/bin/env python3
"""
Database setup and initialization script.

Author: Boris (Claude Code)
"""

import os
import sys
from pathlib import Path

from sqlalchemy import create_engine

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import get_settings
from src.core.logger import get_logger
from src.database.models import Base, create_tables

logger = get_logger(__name__)


def setup_database():
    """
    Initialize database with schema.

    Returns:
        True if successful
    """
    try:
        settings = get_settings()

        logger.info("=" * 60)
        logger.info("Database Setup")
        logger.info("=" * 60)

        # Create engine
        logger.info(f"Connecting to database: {settings.db_host}:{settings.db_port}/{settings.db_name}")
        engine = create_engine(
            settings.database_url,
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            echo=settings.db_echo,
        )

        # Test connection
        with engine.connect() as conn:
            logger.info("✅ Database connection successful")

        # Create all tables
        logger.info("Creating tables...")
        Base.metadata.create_all(engine)
        logger.info("✅ All tables created successfully")

        # Log table information
        logger.info("\nCreated tables:")
        for table in Base.metadata.tables:
            logger.info(f"  - {table}")

        logger.info("\n" + "=" * 60)
        logger.info("Database setup completed successfully!")
        logger.info("=" * 60)

        return True

    except Exception as e:
        logger.error(f"❌ Database setup failed: {str(e)}")
        return False


def drop_all_tables():
    """
    Drop all tables (WARNING: Destructive!).

    Returns:
        True if successful
    """
    try:
        settings = get_settings()

        logger.warning("=" * 60)
        logger.warning("WARNING: About to DROP ALL TABLES!")
        logger.warning("=" * 60)

        response = input("Type 'yes' to confirm: ")
        if response.lower() != "yes":
            logger.info("Cancelled")
            return False

        engine = create_engine(settings.database_url)
        Base.metadata.drop_all(engine)

        logger.warning("✅ All tables dropped")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to drop tables: {str(e)}")
        return False


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Database setup utility")
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop all tables (WARNING: destructive)"
    )
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Drop and recreate all tables"
    )

    args = parser.parse_args()

    if args.drop:
        drop_all_tables()
    elif args.recreate:
        drop_all_tables()
        setup_database()
    else:
        setup_database()


if __name__ == "__main__":
    main()