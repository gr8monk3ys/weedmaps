"""
Data validation utilities for ensuring data quality and consistency.

This module provides validation functions for numeric columns and data integrity checks.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any


class ValidationResult:
    """Stores the results of a validation check."""

    def __init__(
        self,
        is_valid: bool,
        column: str,
        message: str,
        invalid_count: int = 0,
        invalid_values: Optional[List[Any]] = None
    ):
        """
        Initialize a validation result.

        Args:
            is_valid: Whether the validation passed
            column: Name of the column validated
            message: Description of the validation result
            invalid_count: Number of invalid values found
            invalid_values: Sample of invalid values (if applicable)
        """
        self.is_valid = is_valid
        self.column = column
        self.message = message
        self.invalid_count = invalid_count
        self.invalid_values = invalid_values or []

    def __repr__(self) -> str:
        status = "✓ PASS" if self.is_valid else "✗ FAIL"
        return f"{status} [{self.column}]: {self.message}"


def validate_positive_numeric(
    df: pd.DataFrame,
    column: str,
    allow_zero: bool = True,
    column_display_name: Optional[str] = None
) -> ValidationResult:
    """
    Validate that a numeric column contains only positive values.

    Args:
        df: DataFrame to validate
        column: Column name to check
        allow_zero: Whether to allow zero values
        column_display_name: Display name for the column in messages

    Returns:
        ValidationResult with validation details
    """
    display_name = column_display_name or column

    if column not in df.columns:
        return ValidationResult(
            is_valid=False,
            column=column,
            message=f"Column '{display_name}' not found in dataset",
            invalid_count=0
        )

    # Convert to numeric, coercing errors to NaN
    numeric_values = pd.to_numeric(df[column], errors='coerce')

    # Check for negative values
    if allow_zero:
        invalid_mask = numeric_values < 0
        threshold_text = "non-negative (≥ 0)"
    else:
        invalid_mask = numeric_values <= 0
        threshold_text = "positive (> 0)"

    invalid_count = invalid_mask.sum()

    if invalid_count > 0:
        invalid_samples = df[invalid_mask][column].head(5).tolist()
        return ValidationResult(
            is_valid=False,
            column=column,
            message=f"{invalid_count} values in '{display_name}' are not {threshold_text}",
            invalid_count=invalid_count,
            invalid_values=invalid_samples
        )

    return ValidationResult(
        is_valid=True,
        column=column,
        message=f"All values in '{display_name}' are {threshold_text}",
        invalid_count=0
    )


def validate_range(
    df: pd.DataFrame,
    column: str,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    column_display_name: Optional[str] = None
) -> ValidationResult:
    """
    Validate that a numeric column's values fall within a specified range.

    Args:
        df: DataFrame to validate
        column: Column name to check
        min_value: Minimum allowed value (inclusive), None for no minimum
        max_value: Maximum allowed value (inclusive), None for no maximum
        column_display_name: Display name for the column in messages

    Returns:
        ValidationResult with validation details
    """
    display_name = column_display_name or column

    if column not in df.columns:
        return ValidationResult(
            is_valid=False,
            column=column,
            message=f"Column '{display_name}' not found in dataset",
            invalid_count=0
        )

    # Convert to numeric, coercing errors to NaN
    numeric_values = pd.to_numeric(df[column], errors='coerce')

    # Build range check
    invalid_mask = pd.Series([False] * len(df), index=df.index)

    range_text_parts = []
    if min_value is not None:
        invalid_mask |= numeric_values < min_value
        range_text_parts.append(f"≥ {min_value}")

    if max_value is not None:
        invalid_mask |= numeric_values > max_value
        range_text_parts.append(f"≤ {max_value}")

    range_text = " and ".join(range_text_parts) if range_text_parts else "any value"

    invalid_count = invalid_mask.sum()

    if invalid_count > 0:
        invalid_samples = df[invalid_mask][column].head(5).tolist()
        return ValidationResult(
            is_valid=False,
            column=column,
            message=f"{invalid_count} values in '{display_name}' outside range ({range_text})",
            invalid_count=invalid_count,
            invalid_values=invalid_samples
        )

    return ValidationResult(
        is_valid=True,
        column=column,
        message=f"All values in '{display_name}' within range ({range_text})",
        invalid_count=0
    )


def validate_year_column(
    df: pd.DataFrame,
    column: str = "Year",
    min_year: int = 2000,
    max_year: Optional[int] = None
) -> ValidationResult:
    """
    Validate that year values are reasonable.

    Args:
        df: DataFrame to validate
        column: Name of the year column
        min_year: Minimum valid year
        max_year: Maximum valid year (defaults to current year + 1)

    Returns:
        ValidationResult with validation details
    """
    import datetime

    if max_year is None:
        max_year = datetime.datetime.now().year + 1

    return validate_range(
        df,
        column,
        min_value=min_year,
        max_value=max_year,
        column_display_name="Year"
    )


def validate_sentiment_score(
    df: pd.DataFrame,
    column: str = "BERT_Sentiment",
    min_score: float = -1.0,
    max_score: float = 1.0
) -> ValidationResult:
    """
    Validate that sentiment scores are within the expected range.

    Args:
        df: DataFrame to validate
        column: Name of the sentiment column
        min_score: Minimum valid sentiment score
        max_score: Maximum valid sentiment score

    Returns:
        ValidationResult with validation details
    """
    return validate_range(
        df,
        column,
        min_value=min_score,
        max_value=max_score,
        column_display_name="Sentiment Score"
    )


def validate_percentage(
    df: pd.DataFrame,
    column: str,
    column_display_name: Optional[str] = None
) -> ValidationResult:
    """
    Validate that values represent valid percentages (0-100).

    Args:
        df: DataFrame to validate
        column: Column name to check
        column_display_name: Display name for the column in messages

    Returns:
        ValidationResult with validation details
    """
    return validate_range(
        df,
        column,
        min_value=0.0,
        max_value=100.0,
        column_display_name=column_display_name or f"{column} (percentage)"
    )


def validate_dataset(
    df: pd.DataFrame,
    dataset_name: str,
    validations: List[Dict[str, Any]]
) -> Tuple[bool, List[ValidationResult]]:
    """
    Run multiple validations on a dataset.

    Args:
        df: DataFrame to validate
        dataset_name: Name of the dataset for logging
        validations: List of validation configurations, each dict containing:
            - 'type': Validation type ('positive', 'range', 'year', 'sentiment', 'percentage')
            - 'column': Column name to validate
            - Additional type-specific parameters

    Returns:
        Tuple of (all_valid, list of ValidationResults)

    Example:
        >>> validations = [
        ...     {'type': 'positive', 'column': 'Population', 'allow_zero': False},
        ...     {'type': 'range', 'column': 'Score', 'min_value': 0, 'max_value': 100}
        ... ]
        >>> is_valid, results = validate_dataset(df, "MyData", validations)
    """
    results = []
    all_valid = True

    for validation_config in validations:
        validation_type = validation_config.get('type')
        column = validation_config.get('column')

        if not column:
            results.append(ValidationResult(
                is_valid=False,
                column="unknown",
                message="Validation configuration missing 'column' parameter",
                invalid_count=0
            ))
            all_valid = False
            continue

        # Route to appropriate validation function
        if validation_type == 'positive':
            result = validate_positive_numeric(
                df,
                column,
                allow_zero=validation_config.get('allow_zero', True),
                column_display_name=validation_config.get('display_name')
            )
        elif validation_type == 'range':
            result = validate_range(
                df,
                column,
                min_value=validation_config.get('min_value'),
                max_value=validation_config.get('max_value'),
                column_display_name=validation_config.get('display_name')
            )
        elif validation_type == 'year':
            result = validate_year_column(
                df,
                column,
                min_year=validation_config.get('min_year', 2000),
                max_year=validation_config.get('max_year')
            )
        elif validation_type == 'sentiment':
            result = validate_sentiment_score(
                df,
                column,
                min_score=validation_config.get('min_score', -1.0),
                max_score=validation_config.get('max_score', 1.0)
            )
        elif validation_type == 'percentage':
            result = validate_percentage(
                df,
                column,
                column_display_name=validation_config.get('display_name')
            )
        else:
            result = ValidationResult(
                is_valid=False,
                column=column,
                message=f"Unknown validation type: {validation_type}",
                invalid_count=0
            )

        results.append(result)
        if not result.is_valid:
            all_valid = False

    return all_valid, results


def validate_all_datasets(data_dict: Dict[str, pd.DataFrame]) -> Dict[str, Tuple[bool, List[ValidationResult]]]:
    """
    Validate all common datasets with predefined validation rules.

    Args:
        data_dict: Dictionary of DataFrames with keys:
            - 'dispensaries': Dispensary data
            - 'density': Density data
            - 'tweet_sentiment': Sentiment data

    Returns:
        Dictionary mapping dataset names to (is_valid, results) tuples
    """
    validation_results = {}

    # Dispensaries validations
    if 'dispensaries' in data_dict:
        validations = [
            {'type': 'year', 'column': 'Year', 'min_year': 2015},
        ]
        validation_results['dispensaries'] = validate_dataset(
            data_dict['dispensaries'],
            'Dispensaries',
            validations
        )

    # Density validations
    if 'density' in data_dict:
        validations = [
            {'type': 'positive', 'column': 'Population', 'allow_zero': False, 'display_name': 'Population'},
            {'type': 'positive', 'column': 'Dispensary_PerCapita', 'allow_zero': True, 'display_name': 'Dispensary Density'},
        ]
        validation_results['density'] = validate_dataset(
            data_dict['density'],
            'Density',
            validations
        )

    # Sentiment validations
    if 'tweet_sentiment' in data_dict:
        validations = [
            {'type': 'sentiment', 'column': 'BERT_Sentiment'},
            {'type': 'year', 'column': 'Year', 'min_year': 2015},
        ]
        validation_results['tweet_sentiment'] = validate_dataset(
            data_dict['tweet_sentiment'],
            'Tweet Sentiment',
            validations
        )

    return validation_results
