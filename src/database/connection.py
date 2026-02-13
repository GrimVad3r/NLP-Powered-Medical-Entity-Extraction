"""Database connection management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from ..core.config import get_settings
from ..core.logger import get_logger
from ..core.exceptions import DatabaseConnectionError
logger = get_logger(name)
Global engine and session
_engine = None
_SessionLocal = None
def get_engine():
"""Get or create database engine."""
global _engine
if _engine is None:
    try:
        settings = get_settings()
        _engine = create_engine(
            settings.database_url,
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            echo=settings.db_echo,
        )
        logger.info("Database engine created")
    except Exception as e:
        raise DatabaseConnectionError(f"Failed to create engine: {e}")

return _engine
def get_session_factory():
"""Get or create session factory."""
global _SessionLocal
if _SessionLocal is None:
    engine = get_engine()
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Session factory created")

return _SessionLocal
def get_db_session() -> Session:
"""Get new database session."""
SessionLocal = get_session_factory()
return SessionLocal()
@contextmanager
def session_scope():
"""Provide a transactional scope for all operations."""
session = get_db_session()
try:
yield session
session.commit()
except Exception as e:
session.rollback()
logger.error(f"Session error: {e}")
raise
finally:
session.close()