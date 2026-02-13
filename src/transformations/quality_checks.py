"""
Data quality checks and validation.

BRANCH-5: Data Transformation
Author: Boris (Claude Code)
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from ..core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class QualityCheckResult:
    """Result of a quality check."""

    check_name: str
    passed: bool
    message: str
    rows_affected: int = 0
    percentage: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "check_name": self.check_name,
            "passed": self.passed,
            "message": self.message,
            "rows_affected": self.rows_affected,
            "percentage": self.percentage,
        }


class QualityChecker:
    """Check data quality and integrity."""

    def __init__(self):
        """Initialize quality checker."""
        self.results: List[QualityCheckResult] = []

    def check_no_nulls(
        self,
        data: List[Dict],
        field: str,
        severity: str = "error"
    ) -> QualityCheckResult:
        """
        Check for null values in field.

        Args:
            data: List of data dictionaries
            field: Field to check
            severity: 'error' or 'warning'

        Returns:
            Check result
        """
        has_nulls = [item for item in data if item.get(field) is None]
        passed = len(has_nulls) == 0

        result = QualityCheckResult(
            check_name=f"No nulls in {field}",
            passed=passed,
            message=f"Found {len(has_nulls)} null values" if has_nulls else "No nulls found",
            rows_affected=len(has_nulls),
            percentage=(len(has_nulls) / len(data) * 100) if data else 0
        )

        self.results.append(result)
        return result

    def check_value_range(
        self,
        data: List[Dict],
        field: str,
        min_val: float,
        max_val: float
    ) -> QualityCheckResult:
        """
        Check values are within range.

        Args:
            data: List of data dictionaries
            field: Field to check
            min_val: Minimum value
            max_val: Maximum value

        Returns:
            Check result
        """
        out_of_range = [
            item for item in data
            if item.get(field) is not None and not (min_val <= item.get(field) <= max_val)
        ]

        passed = len(out_of_range) == 0

        result = QualityCheckResult(
            check_name=f"{field} in range [{min_val}, {max_val}]",
            passed=passed,
            message=f"Found {len(out_of_range)} values out of range" if out_of_range else "All values in range",
            rows_affected=len(out_of_range),
            percentage=(len(out_of_range) / len(data) * 100) if data else 0
        )

        self.results.append(result)
        return result

    def check_unique_values(
        self,
        data: List[Dict],
        field: str
    ) -> QualityCheckResult:
        """
        Check for unique values in field.

        Args:
            data: List of data dictionaries
            field: Field to check

        Returns:
            Check result
        """
        values = [item.get(field) for item in data if item.get(field) is not None]
        unique_count = len(set(values))
        total_count = len(values)

        duplicates = total_count - unique_count
        passed = duplicates == 0

        result = QualityCheckResult(
            check_name=f"Unique values in {field}",
            passed=passed,
            message=f"Found {duplicates} duplicate values out of {total_count}",
            rows_affected=duplicates,
            percentage=(duplicates / total_count * 100) if total_count > 0 else 0
        )

        self.results.append(result)
        return result

    def check_not_empty(self, data: List[Dict]) -> QualityCheckResult:
        """
        Check data is not empty.

        Args:
            data: List of data dictionaries

        Returns:
            Check result
        """
        passed = len(data) > 0

        result = QualityCheckResult(
            check_name="Data not empty",
            passed=passed,
            message=f"Found {len(data)} records",
            rows_affected=0,
            percentage=100 if passed else 0
        )

        self.results.append(result)
        return result

    def check_column_exists(
        self,
        data: List[Dict],
        columns: List[str]
    ) -> QualityCheckResult:
        """
        Check required columns exist.

        Args:
            data: List of data dictionaries
            columns: Required columns

        Returns:
            Check result
        """
        if not data:
            missing = columns
        else:
            first_record = data[0]
            missing = [col for col in columns if col not in first_record]

        passed = len(missing) == 0

        result = QualityCheckResult(
            check_name=f"Columns exist: {columns}",
            passed=passed,
            message=f"Missing columns: {missing}" if missing else "All required columns present",
            rows_affected=0,
            percentage=((len(columns) - len(missing)) / len(columns) * 100) if columns else 0
        )

        self.results.append(result)
        return result

    def check_data_type(
        self,
        data: List[Dict],
        field: str,
        expected_type: type
    ) -> QualityCheckResult:
        """
        Check field data type.

        Args:
            data: List of data dictionaries
            field: Field to check
            expected_type: Expected data type

        Returns:
            Check result
        """
        invalid_types = [
            item for item in data
            if item.get(field) is not None and not isinstance(item.get(field), expected_type)
        ]

        passed = len(invalid_types) == 0

        result = QualityCheckResult(
            check_name=f"{field} is {expected_type.__name__}",
            passed=passed,
            message=f"Found {len(invalid_types)} records with wrong type",
            rows_affected=len(invalid_types),
            percentage=(len(invalid_types) / len(data) * 100) if data else 0
        )

        self.results.append(result)
        return result

    def check_pattern_match(
        self,
        data: List[Dict],
        field: str,
        pattern: str
    ) -> QualityCheckResult:
        """
        Check field matches regex pattern.

        Args:
            data: List of data dictionaries
            field: Field to check
            pattern: Regex pattern

        Returns:
            Check result
        """
        import re

        compiled_pattern = re.compile(pattern)
        non_matching = [
            item for item in data
            if item.get(field) is not None and not compiled_pattern.match(str(item.get(field)))
        ]

        passed = len(non_matching) == 0

        result = QualityCheckResult(
            check_name=f"{field} matches pattern {pattern}",
            passed=passed,
            message=f"Found {len(non_matching)} non-matching values",
            rows_affected=len(non_matching),
            percentage=(len(non_matching) / len(data) * 100) if data else 0
        )

        self.results.append(result)
        return result

    def get_summary(self) -> Dict[str, Any]:
        """
        Get quality check summary.

        Returns:
            Summary dictionary
        """
        total_checks = len(self.results)
        passed_checks = sum(1 for r in self.results if r.passed)
        failed_checks = total_checks - passed_checks

        return {
            "total_checks": total_checks,
            "passed": passed_checks,
            "failed": failed_checks,
            "pass_rate": (passed_checks / total_checks * 100) if total_checks > 0 else 0,
            "details": [r.to_dict() for r in self.results],
        }

    def get_failed_checks(self) -> List[QualityCheckResult]:
        """Get list of failed checks."""
        return [r for r in self.results if not r.passed]

    def print_report(self) -> None:
        """Print quality report to logger."""
        summary = self.get_summary()

        logger.info("=" * 60)
        logger.info("DATA QUALITY REPORT")
        logger.info("=" * 60)
        logger.info(f"Total Checks: {summary['total_checks']}")
        logger.info(f"Passed: {summary['passed']}")
        logger.info(f"Failed: {summary['failed']}")
        logger.info(f"Pass Rate: {summary['pass_rate']:.1f}%")
        logger.info("=" * 60)

        for result in self.results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            logger.info(f"{status}: {result.check_name} - {result.message}")