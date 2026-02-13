"""
Data aggregation and summarization functions.

BRANCH-5: Data Transformation
Author: Boris (Claude Code)
"""

from typing import Dict, List, Any, Optional
from collections import Counter
import statistics

from ..core.logger import get_logger

logger = get_logger(__name__)


class AggregationEngine:
    """Aggregate and summarize data."""

    @staticmethod
    def count_by_field(data: List[Dict], field: str) -> Dict[str, int]:
        """
        Count occurrences by field value.

        Args:
            data: List of data dictionaries
            field: Field to count by

        Returns:
            Dictionary of {value: count}
        """
        logger.debug(f"Counting by field: {field}")
        values = [item.get(field) for item in data if item.get(field) is not None]
        counts = dict(Counter(values))
        logger.info(f"Found {len(counts)} unique values in {field}")
        return counts

    @staticmethod
    def sum_by_field(
        data: List[Dict],
        field: str,
        group_by: Optional[str] = None
    ) -> Dict:
        """
        Sum values by field.

        Args:
            data: List of data dictionaries
            field: Field to sum
            group_by: Optional field to group by

        Returns:
            Dictionary of sums
        """
        logger.debug(f"Summing {field}" + (f" grouped by {group_by}" if group_by else ""))

        if group_by:
            groups = {}
            for item in data:
                key = item.get(group_by)
                if key is not None:
                    groups.setdefault(key, 0)
                    groups[key] += item.get(field, 0)
            logger.info(f"Grouped sum by {group_by}: {len(groups)} groups")
            return groups
        else:
            total = sum(item.get(field, 0) for item in data)
            logger.info(f"Total sum of {field}: {total}")
            return {"total": total}

    @staticmethod
    def average_by_field(
        data: List[Dict],
        field: str,
        group_by: Optional[str] = None
    ) -> Dict:
        """
        Calculate average of field.

        Args:
            data: List of data dictionaries
            field: Field to average
            group_by: Optional field to group by

        Returns:
            Dictionary of averages
        """
        logger.debug(f"Averaging {field}" + (f" grouped by {group_by}" if group_by else ""))

        if not data:
            return {}

        if group_by:
            groups = {}
            for item in data:
                key = item.get(group_by)
                if key is not None:
                    if key not in groups:
                        groups[key] = []
                    groups[key].append(item.get(field, 0))

            averages = {key: statistics.mean(vals) for key, vals in groups.items()}
            logger.info(f"Grouped average by {group_by}: {len(averages)} groups")
            return averages
        else:
            values = [item.get(field, 0) for item in data]
            avg = statistics.mean(values) if values else 0
            logger.info(f"Average of {field}: {avg}")
            return {"average": avg}

    @staticmethod
    def group_by_field(data: List[Dict], field: str) -> Dict[str, List]:
        """
        Group data by field value.

        Args:
            data: List of data dictionaries
            field: Field to group by

        Returns:
            Dictionary of {value: [items]}
        """
        logger.debug(f"Grouping by field: {field}")
        groups = {}

        for item in data:
            key = item.get(field)
            if key is not None:
                if key not in groups:
                    groups[key] = []
                groups[key].append(item)

        logger.info(f"Created {len(groups)} groups by {field}")
        return groups

    @staticmethod
    def percentile(values: List[float], percentile: float) -> float:
        """
        Calculate percentile value.

        Args:
            values: List of numeric values
            percentile: Percentile (0-100)

        Returns:
            Percentile value
        """
        if not values:
            return 0

        sorted_values = sorted(values)
        index = (percentile / 100) * (len(sorted_values) - 1)
        lower = int(index)
        upper = lower + 1

        if upper >= len(sorted_values):
            return sorted_values[lower]

        weight = index - lower
        return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight

    @staticmethod
    def get_statistics(values: List[float]) -> Dict[str, float]:
        """
        Get comprehensive statistics for values.

        Args:
            values: List of numeric values

        Returns:
            Dictionary of statistics
        """
        if not values:
            return {}

        sorted_values = sorted(values)
        n = len(sorted_values)

        return {
            "count": n,
            "sum": sum(sorted_values),
            "mean": statistics.mean(sorted_values),
            "median": statistics.median(sorted_values),
            "stdev": statistics.stdev(sorted_values) if n > 1 else 0,
            "min": min(sorted_values),
            "max": max(sorted_values),
            "q25": AggregationEngine.percentile(sorted_values, 25),
            "q75": AggregationEngine.percentile(sorted_values, 75),
        }

    @staticmethod
    def pivot_table(
        data: List[Dict],
        index_field: str,
        column_field: str,
        value_field: str,
        aggregation: str = "sum"
    ) -> Dict:
        """
        Create pivot table.

        Args:
            data: List of data dictionaries
            index_field: Field for rows
            column_field: Field for columns
            value_field: Field to aggregate
            aggregation: 'sum', 'count', 'mean'

        Returns:
            Pivot table as nested dictionary
        """
        logger.debug(f"Creating pivot table: {index_field} x {column_field}")

        pivot = {}

        for item in data:
            row = item.get(index_field)
            col = item.get(column_field)
            val = item.get(value_field, 0)

            if row is not None and col is not None:
                if row not in pivot:
                    pivot[row] = {}

                if col not in pivot[row]:
                    if aggregation == "count":
                        pivot[row][col] = 0
                    else:
                        pivot[row][col] = val

                if aggregation == "sum":
                    pivot[row][col] += val
                elif aggregation == "count":
                    pivot[row][col] += 1

        logger.info(f"Created pivot table: {len(pivot)} rows")
        return pivot

    @staticmethod
    def flatten_nested(data: Dict) -> List[Dict]:
        """
        Flatten nested dictionary to list of records.

        Args:
            data: Nested dictionary

        Returns:
            List of flattened records
        """
        records = []

        for key, value in data.items():
            if isinstance(value, dict):
                for subkey, subval in value.items():
                    records.append({
                        "key": key,
                        "subkey": subkey,
                        "value": subval,
                    })
            else:
                records.append({
                    "key": key,
                    "value": value,
                })

        return records

    @staticmethod
    def top_n(
        data: Dict[str, Any],
        n: int = 10,
        reverse: bool = True
    ) -> List[tuple]:
        """
        Get top N items by value.

        Args:
            data: Dictionary of {key: value}
            n: Number of top items
            reverse: Sort descending if True

        Returns:
            List of (key, value) tuples
        """
        sorted_items = sorted(data.items(), key=lambda x: x[1], reverse=reverse)
        return sorted_items[:n]

    @staticmethod
    def bottom_n(
        data: Dict[str, Any],
        n: int = 10
    ) -> List[tuple]:
        """
        Get bottom N items by value.

        Args:
            data: Dictionary of {key: value}
            n: Number of bottom items

        Returns:
            List of (key, value) tuples
        """
        return AggregationEngine.top_n(data, n=n, reverse=False)