"""Database migration utilities."""
from alembic import command
from alembic.config import Config as AlembicConfig
from ..core.logger import get_logger
logger = get_logger(name)
class MigrationManager:
"""Manage database migrations."""
def __init__(self, alembic_ini_path: str = "alembic.ini"):
    """Initialize migration manager."""
    self.alembic_config = AlembicConfig(alembic_ini_path)

def upgrade(self, revision: str = "head"):
    """Run migrations up to revision."""
    try:
        command.upgrade(self.alembic_config, revision)
        logger.info(f"Upgraded to {revision}")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise

def downgrade(self, revision: str = "-1"):
    """Run migrations down to revision."""
    try:
        command.downgrade(self.alembic_config, revision)
        logger.info(f"Downgraded to {revision}")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise

def current(self):
    """Get current revision."""
    try:
        return command.current(self.alembic_config)
    except Exception as e:
        logger.error(f"Failed to get current revision: {e}")
        raise