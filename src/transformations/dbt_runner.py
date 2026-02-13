"""
dbt project runner and orchestrator.

BRANCH-5: Data Transformation
Author: Boris (Claude Code)
"""

import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

from ..core.config import get_settings
from ..core.logger import get_logger
from ..core.exceptions import DBTExecutionError

logger = get_logger(__name__)


class DBTRunner:
    """Run dbt transformations and manage data pipelines."""

    def __init__(self, dbt_project_dir: str = "dbt"):
        """
        Initialize DBT runner.

        Args:
            dbt_project_dir: Path to dbt project directory
        """
        self.dbt_dir = Path(dbt_project_dir)
        self.settings = get_settings()

        if not self.dbt_dir.exists():
            raise DBTExecutionError(f"dbt project directory not found: {dbt_project_dir}")

        logger.info(f"DBT runner initialized at {self.dbt_dir}")

    def run_transformations(self, select: str = "", threads: int = 4) -> bool:
        """
        Run dbt transformations.

        Args:
            select: Optional selection criteria (e.g., "stg_*")
            threads: Number of parallel threads

        Returns:
            True if successful

        Raises:
            DBTExecutionError: If dbt run fails
        """
        try:
            logger.info("Starting dbt transformations...")

            cmd = ["dbt", "run"]
            
            if select:
                cmd.extend(["--select", select])
            
            cmd.extend(["--threads", str(threads)])

            logger.info(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                cwd=self.dbt_dir,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                logger.info("✅ dbt run successful")
                return True
            else:
                logger.error(f"dbt run failed:\n{result.stderr}")
                raise DBTExecutionError(
                    f"dbt run failed with return code {result.returncode}",
                    details={"stderr": result.stderr}
                )

        except subprocess.CalledProcessError as e:
            raise DBTExecutionError(f"dbt execution failed: {e}")
        except Exception as e:
            raise DBTExecutionError(f"Failed to run dbt: {e}")

    def run_tests(self) -> bool:
        """
        Run dbt tests for data quality.

        Returns:
            True if all tests pass

        Raises:
            DBTExecutionError: If tests fail
        """
        try:
            logger.info("Running dbt tests...")

            result = subprocess.run(
                ["dbt", "test"],
                cwd=self.dbt_dir,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                logger.info("✅ dbt tests passed")
                return True
            else:
                logger.warning(f"dbt tests failed:\n{result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Failed to run dbt tests: {e}")
            raise DBTExecutionError(f"Test execution failed: {e}")

    def generate_docs(self) -> bool:
        """
        Generate dbt documentation.

        Returns:
            True if successful
        """
        try:
            logger.info("Generating dbt documentation...")

            result = subprocess.run(
                ["dbt", "docs", "generate"],
                cwd=self.dbt_dir,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                logger.info("✅ Documentation generated successfully")
                return True
            else:
                logger.error(f"Documentation generation failed: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Failed to generate docs: {e}")
            return False

    def get_manifest(self) -> Optional[Dict[str, Any]]:
        """
        Get dbt manifest (model metadata).

        Returns:
            Manifest dictionary or None
        """
        try:
            import json

            manifest_path = self.dbt_dir / "target" / "manifest.json"

            if not manifest_path.exists():
                logger.warning("Manifest not found, running dbt compile...")
                self.compile()

            with open(manifest_path) as f:
                return json.load(f)

        except Exception as e:
            logger.error(f"Failed to get manifest: {e}")
            return None

    def compile(self) -> bool:
        """
        Compile dbt project.

        Returns:
            True if successful
        """
        try:
            logger.info("Compiling dbt project...")

            result = subprocess.run(
                ["dbt", "compile"],
                cwd=self.dbt_dir,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                logger.info("✅ dbt compile successful")
                return True
            else:
                logger.error(f"dbt compile failed: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Failed to compile: {e}")
            return False

    def snapshot(self) -> bool:
        """
        Create snapshots of data.

        Returns:
            True if successful
        """
        try:
            logger.info("Creating dbt snapshots...")

            result = subprocess.run(
                ["dbt", "snapshot"],
                cwd=self.dbt_dir,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                logger.info("✅ Snapshots created successfully")
                return True
            else:
                logger.error(f"Snapshot creation failed: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Failed to create snapshots: {e}")
            return False

    def seed(self) -> bool:
        """
        Load seed data.

        Returns:
            True if successful
        """
        try:
            logger.info("Loading seed data...")

            result = subprocess.run(
                ["dbt", "seed"],
                cwd=self.dbt_dir,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                logger.info("✅ Seed data loaded successfully")
                return True
            else:
                logger.error(f"Seed loading failed: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Failed to load seeds: {e}")
            return False

    def full_refresh(self) -> bool:
        """
        Run full refresh (drop and recreate all models).

        Returns:
            True if successful
        """
        try:
            logger.warning("Running full refresh (this will drop all models)...")

            result = subprocess.run(
                ["dbt", "run", "--full-refresh"],
                cwd=self.dbt_dir,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                logger.info("✅ Full refresh successful")
                return True
            else:
                logger.error(f"Full refresh failed: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Failed to run full refresh: {e}")
            return False