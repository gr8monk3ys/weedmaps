"""
Tests for the data validation module.
"""
import pytest
import pandas as pd
import numpy as np
from app.utils.data_validation import (
    ValidationResult,
    validate_positive_numeric,
    validate_range,
    validate_year_column,
    validate_sentiment_score,
    validate_percentage,
    validate_dataset,
    validate_all_datasets
)


class TestValidationResult:
    """Tests for ValidationResult class."""

    def test_valid_result(self):
        """Test creating a valid result."""
        result = ValidationResult(
            is_valid=True,
            column="test_column",
            message="All values valid",
            invalid_count=0
        )
        assert result.is_valid
        assert result.column == "test_column"
        assert result.invalid_count == 0
        assert "PASS" in repr(result)

    def test_invalid_result(self):
        """Test creating an invalid result."""
        result = ValidationResult(
            is_valid=False,
            column="test_column",
            message="Found invalid values",
            invalid_count=5,
            invalid_values=[1, 2, 3]
        )
        assert not result.is_valid
        assert result.invalid_count == 5
        assert len(result.invalid_values) == 3
        assert "FAIL" in repr(result)


class TestValidatePositiveNumeric:
    """Tests for validate_positive_numeric function."""

    def test_all_positive_values(self):
        """Test with all positive values."""
        df = pd.DataFrame({"value": [1, 2, 3, 4, 5]})
        result = validate_positive_numeric(df, "value", allow_zero=False)
        assert result.is_valid
        assert result.invalid_count == 0

    def test_with_zero_allowed(self):
        """Test with zero values when allowed."""
        df = pd.DataFrame({"value": [0, 1, 2, 3]})
        result = validate_positive_numeric(df, "value", allow_zero=True)
        assert result.is_valid
        assert result.invalid_count == 0

    def test_with_zero_not_allowed(self):
        """Test with zero values when not allowed."""
        df = pd.DataFrame({"value": [0, 1, 2, 3]})
        result = validate_positive_numeric(df, "value", allow_zero=False)
        assert not result.is_valid
        assert result.invalid_count == 1

    def test_with_negative_values(self):
        """Test with negative values."""
        df = pd.DataFrame({"value": [-1, 0, 1, 2, -3]})
        result = validate_positive_numeric(df, "value", allow_zero=True)
        assert not result.is_valid
        assert result.invalid_count == 2
        assert len(result.invalid_values) > 0

    def test_missing_column(self):
        """Test with missing column."""
        df = pd.DataFrame({"value": [1, 2, 3]})
        result = validate_positive_numeric(df, "nonexistent")
        assert not result.is_valid
        assert "not found" in result.message

    def test_custom_display_name(self):
        """Test with custom display name."""
        df = pd.DataFrame({"value": [1, 2, 3]})
        result = validate_positive_numeric(df, "value", column_display_name="Population")
        assert "Population" in result.message


class TestValidateRange:
    """Tests for validate_range function."""

    def test_within_range(self):
        """Test with all values within range."""
        df = pd.DataFrame({"score": [0.5, 0.7, 0.9]})
        result = validate_range(df, "score", min_value=0.0, max_value=1.0)
        assert result.is_valid
        assert result.invalid_count == 0

    def test_below_minimum(self):
        """Test with values below minimum."""
        df = pd.DataFrame({"score": [-0.5, 0.5, 0.7]})
        result = validate_range(df, "score", min_value=0.0, max_value=1.0)
        assert not result.is_valid
        assert result.invalid_count == 1

    def test_above_maximum(self):
        """Test with values above maximum."""
        df = pd.DataFrame({"score": [0.5, 0.7, 1.5]})
        result = validate_range(df, "score", min_value=0.0, max_value=1.0)
        assert not result.is_valid
        assert result.invalid_count == 1

    def test_no_minimum(self):
        """Test with no minimum specified."""
        df = pd.DataFrame({"score": [-10, 0, 5]})
        result = validate_range(df, "score", max_value=10.0)
        assert result.is_valid

    def test_no_maximum(self):
        """Test with no maximum specified."""
        df = pd.DataFrame({"score": [0, 5, 100]})
        result = validate_range(df, "score", min_value=0.0)
        assert result.is_valid

    def test_missing_column(self):
        """Test with missing column."""
        df = pd.DataFrame({"value": [1, 2, 3]})
        result = validate_range(df, "nonexistent", min_value=0, max_value=10)
        assert not result.is_valid


class TestValidateYearColumn:
    """Tests for validate_year_column function."""

    def test_valid_years(self):
        """Test with valid year values."""
        df = pd.DataFrame({"Year": [2020, 2021, 2022]})
        result = validate_year_column(df, min_year=2015)
        assert result.is_valid

    def test_year_too_old(self):
        """Test with years before minimum."""
        df = pd.DataFrame({"Year": [1999, 2020, 2021]})
        result = validate_year_column(df, min_year=2000)
        assert not result.is_valid
        assert result.invalid_count == 1

    def test_year_too_new(self):
        """Test with years after maximum."""
        import datetime
        current_year = datetime.datetime.now().year
        df = pd.DataFrame({"Year": [2020, current_year + 10]})
        result = validate_year_column(df, min_year=2015)
        assert not result.is_valid


class TestValidateSentimentScore:
    """Tests for validate_sentiment_score function."""

    def test_valid_sentiment_scores(self):
        """Test with valid sentiment scores."""
        df = pd.DataFrame({"BERT_Sentiment": [-0.5, 0.0, 0.5, 1.0]})
        result = validate_sentiment_score(df)
        assert result.is_valid

    def test_sentiment_out_of_range(self):
        """Test with sentiment scores out of range."""
        df = pd.DataFrame({"BERT_Sentiment": [-2.0, 0.0, 0.5, 1.5]})
        result = validate_sentiment_score(df)
        assert not result.is_valid
        assert result.invalid_count == 2


class TestValidatePercentage:
    """Tests for validate_percentage function."""

    def test_valid_percentages(self):
        """Test with valid percentage values."""
        df = pd.DataFrame({"percent": [0, 25, 50, 75, 100]})
        result = validate_percentage(df, "percent")
        assert result.is_valid

    def test_percentage_out_of_range(self):
        """Test with percentages out of range."""
        df = pd.DataFrame({"percent": [-10, 50, 150]})
        result = validate_percentage(df, "percent")
        assert not result.is_valid
        assert result.invalid_count == 2


class TestValidateDataset:
    """Tests for validate_dataset function."""

    def test_multiple_validations(self):
        """Test running multiple validations on a dataset."""
        df = pd.DataFrame({
            "population": [1000, 2000, 3000],
            "score": [0.5, 0.7, 0.9],
            "Year": [2020, 2021, 2022]
        })

        validations = [
            {'type': 'positive', 'column': 'population', 'allow_zero': False},
            {'type': 'range', 'column': 'score', 'min_value': 0.0, 'max_value': 1.0},
            {'type': 'year', 'column': 'Year', 'min_year': 2015}
        ]

        is_valid, results = validate_dataset(df, "TestData", validations)
        assert is_valid
        assert len(results) == 3
        assert all(r.is_valid for r in results)

    def test_with_failures(self):
        """Test with some validations failing."""
        df = pd.DataFrame({
            "population": [-1000, 2000, 3000],
            "score": [1.5, 0.7, 0.9]
        })

        validations = [
            {'type': 'positive', 'column': 'population', 'allow_zero': False},
            {'type': 'range', 'column': 'score', 'min_value': 0.0, 'max_value': 1.0}
        ]

        is_valid, results = validate_dataset(df, "TestData", validations)
        assert not is_valid
        assert len(results) == 2
        assert sum(1 for r in results if not r.is_valid) == 2

    def test_unknown_validation_type(self):
        """Test with unknown validation type."""
        df = pd.DataFrame({"value": [1, 2, 3]})
        validations = [
            {'type': 'unknown_type', 'column': 'value'}
        ]

        is_valid, results = validate_dataset(df, "TestData", validations)
        assert not is_valid
        assert len(results) == 1
        assert "Unknown validation type" in results[0].message

    def test_missing_column_parameter(self):
        """Test with missing column parameter."""
        df = pd.DataFrame({"value": [1, 2, 3]})
        validations = [
            {'type': 'positive'}  # Missing 'column'
        ]

        is_valid, results = validate_dataset(df, "TestData", validations)
        assert not is_valid
        assert "missing 'column' parameter" in results[0].message


class TestValidateAllDatasets:
    """Tests for validate_all_datasets function."""

    def test_validate_dispensaries(self):
        """Test validating dispensaries dataset."""
        data_dict = {
            'dispensaries': pd.DataFrame({
                'Year': [2020, 2021, 2022],
                'License Number': ['L1', 'L2', 'L3']
            })
        }

        results = validate_all_datasets(data_dict)
        assert 'dispensaries' in results
        is_valid, validation_results = results['dispensaries']
        assert len(validation_results) > 0

    def test_validate_density(self):
        """Test validating density dataset."""
        data_dict = {
            'density': pd.DataFrame({
                'Population': [10000, 20000, 30000],
                'Dispensary_PerCapita': [5.0, 7.5, 10.0]
            })
        }

        results = validate_all_datasets(data_dict)
        assert 'density' in results
        is_valid, validation_results = results['density']
        assert len(validation_results) > 0

    def test_validate_sentiment(self):
        """Test validating sentiment dataset."""
        data_dict = {
            'tweet_sentiment': pd.DataFrame({
                'BERT_Sentiment': [-0.5, 0.0, 0.5],
                'Year': [2020, 2021, 2022]
            })
        }

        results = validate_all_datasets(data_dict)
        assert 'tweet_sentiment' in results
        is_valid, validation_results = results['tweet_sentiment']
        assert len(validation_results) > 0

    def test_validate_all_datasets_together(self):
        """Test validating all datasets together."""
        data_dict = {
            'dispensaries': pd.DataFrame({
                'Year': [2020, 2021, 2022]
            }),
            'density': pd.DataFrame({
                'Population': [10000, 20000],
                'Dispensary_PerCapita': [5.0, 7.5]
            }),
            'tweet_sentiment': pd.DataFrame({
                'BERT_Sentiment': [-0.5, 0.5],
                'Year': [2020, 2021]
            })
        }

        results = validate_all_datasets(data_dict)
        assert len(results) == 3
        assert 'dispensaries' in results
        assert 'density' in results
        assert 'tweet_sentiment' in results

    def test_empty_data_dict(self):
        """Test with empty data dictionary."""
        data_dict = {}
        results = validate_all_datasets(data_dict)
        assert len(results) == 0
