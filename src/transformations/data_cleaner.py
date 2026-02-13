"""
Data cleaning and normalization utilities.

BRANCH-5: Data Transformation
Author: Boris (Claude Code)
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any

from ..core.logger import get_logger

logger = get_logger(__name__)


class DataCleaner:
    """Clean, normalize, and transform data."""

    @staticmethod
    def remove_duplicates(
        df: pd.DataFrame,
        subset: Optional[List[str]] = None,
        keep: str = "first"
    ) -> pd.DataFrame:
        """
        Remove duplicate rows.

        Args:
            df: Input dataframe
            subset: Columns to consider for duplicates
            keep: 'first', 'last', or False

        Returns:
            Dataframe with duplicates removed
        """
        logger.debug(f"Removing duplicates (keep={keep})...")
        initial_rows = len(df)

        df_clean = df.drop_duplicates(subset=subset, keep=keep)
        removed = initial_rows - len(df_clean)

        logger.info(f"Removed {removed} duplicate rows")
        return df_clean

    @staticmethod
    def handle_nulls(
        df: pd.DataFrame,
        strategy: str = "drop",
        fill_value: Any = None
    ) -> pd.DataFrame:
        """
        Handle null values.

        Args:
            df: Input dataframe
            strategy: 'drop', 'fill_value', 'fill_mean', 'fill_forward', 'fill_backward'
            fill_value: Value to fill with (for 'fill_value' strategy)

        Returns:
            Cleaned dataframe
        """
        logger.debug(f"Handling nulls with strategy: {strategy}")
        null_count = df.isnull().sum().sum()

        if null_count == 0:
            logger.info("No null values found")
            return df

        if strategy == "drop":
            df_clean = df.dropna()
        elif strategy == "fill_value":
            df_clean = df.fillna(fill_value)
        elif strategy == "fill_mean":
            df_clean = df.fillna(df.mean(numeric_only=True))
        elif strategy == "fill_forward":
            df_clean = df.fillna(method='ffill')
        elif strategy == "fill_backward":
            df_clean = df.fillna(method='bfill')
        else:
            logger.warning(f"Unknown strategy: {strategy}, using drop")
            df_clean = df.dropna()

        logger.info(f"Handled {null_count} null values")
        return df_clean

    @staticmethod
    def normalize_numeric(
        df: pd.DataFrame,
        columns: List[str],
        method: str = "minmax"
    ) -> pd.DataFrame:
        """
        Normalize numeric columns.

        Args:
            df: Input dataframe
            columns: Columns to normalize
            method: 'minmax' (0-1) or 'zscore' (mean=0, std=1)

        Returns:
            Dataframe with normalized columns
        """
        logger.debug(f"Normalizing {columns} using {method}...")

        df_norm = df.copy()

        for col in columns:
            if col not in df.columns:
                logger.warning(f"Column {col} not found")
                continue

            if method == "minmax":
                min_val = df_norm[col].min()
                max_val = df_norm[col].max()
                df_norm[col] = (df_norm[col] - min_val) / (max_val - min_val)

            elif method == "zscore":
                mean_val = df_norm[col].mean()
                std_val = df_norm[col].std()
                df_norm[col] = (df_norm[col] - mean_val) / std_val

        logger.info(f"Normalized {len(columns)} columns")
        return df_norm

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text.

        Args:
            text: Input text

        Returns:
            Normalized text
        """
        # Convert to lowercase
        text = text.lower()
        # Remove leading/trailing whitespace
        text = text.strip()
        # Replace multiple spaces with single space
        text = ' '.join(text.split())
        return text

    @staticmethod
    def normalize_text_series(series: pd.Series) -> pd.Series:
        """
        Normalize text in a pandas Series.

        Args:
            series: Input Series

        Returns:
            Series with normalized text
        """
        logger.debug("Normalizing text series...")
        return series.apply(DataCleaner.normalize_text)

    @staticmethod
    def remove_outliers(
        df: pd.DataFrame,
        columns: List[str],
        method: str = "iqr",
        threshold: float = 1.5
    ) -> pd.DataFrame:
        """
        Remove outliers from numeric columns.

        Args:
            df: Input dataframe
            columns: Columns to check
            method: 'iqr' (Interquartile Range) or 'zscore'
            threshold: IQR multiplier or z-score threshold

        Returns:
            Dataframe with outliers removed
        """
        logger.debug(f"Removing outliers using {method}...")
        initial_rows = len(df)

        df_clean = df.copy()

        for col in columns:
            if col not in df_clean.columns:
                continue

            if method == "iqr":
                Q1 = df_clean[col].quantile(0.25)
                Q3 = df_clean[col].quantile(0.75)
                IQR = Q3 - Q1

                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR

                df_clean = df_clean[
                    (df_clean[col] >= lower_bound) & (df_clean[col] <= upper_bound)
                ]

            elif method == "zscore":
                z_scores = np.abs((df_clean[col] - df_clean[col].mean()) / df_clean[col].std())
                df_clean = df_clean[z_scores < threshold]

        removed = initial_rows - len(df_clean)
        logger.info(f"Removed {removed} rows with outliers")
        return df_clean

    @staticmethod
    def validate_data_types(df: pd.DataFrame, expected_types: Dict[str, str]) -> bool:
        """
        Validate dataframe data types.

        Args:
            df: Input dataframe
            expected_types: Dict of {column: expected_dtype}

        Returns:
            True if all types match
        """
        logger.debug("Validating data types...")

        for col, expected_type in expected_types.items():
            if col not in df.columns:
                logger.warning(f"Column {col} not found")
                continue

            actual_type = str(df[col].dtype)
            if actual_type != expected_type:
                logger.error(f"Type mismatch for {col}: expected {expected_type}, got {actual_type}")
                return False

        logger.info("Data types validation passed")
        return True

    @staticmethod
    def get_data_quality_report(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate data quality report.

        Args:
            df: Input dataframe

        Returns:
            Quality report dictionary
        """
        total_cells = df.shape[0] * df.shape[1]
        null_cells = df.isnull().sum().sum()
        null_percentage = (null_cells / total_cells * 100) if total_cells > 0 else 0

        duplicates = df.duplicated().sum()

        return {
            "rows": df.shape[0],
            "columns": df.shape[1],
            "total_cells": total_cells,
            "null_cells": null_cells,
            "null_percentage": null_percentage,
            "duplicate_rows": duplicates,
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
        }