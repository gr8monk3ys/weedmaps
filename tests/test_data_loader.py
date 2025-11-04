"""
Tests for the data_loader module.
"""
import pytest
import pandas as pd
from app.utils.data_loader import convert_sentiment_score, get_data_dir


class TestConvertSentimentScore:
    """Tests for the convert_sentiment_score function."""

    def test_convert_nan(self):
        """Test that NaN values are converted to 0."""
        assert convert_sentiment_score(pd.NA) == 0
        assert convert_sentiment_score(None) == 0

    def test_convert_numeric(self):
        """Test that numeric values are returned as-is."""
        assert convert_sentiment_score(0.5) == 0.5
        assert convert_sentiment_score(-0.3) == -0.3
        assert convert_sentiment_score(1) == 1.0

    def test_convert_star_rating(self):
        """Test conversion of star ratings to -1 to 1 scale."""
        # 5 stars -> 1.0
        assert convert_sentiment_score("5 star") == 1.0
        # 3 stars -> 0.0 (neutral)
        assert convert_sentiment_score("3 star") == 0.0
        # 1 star -> -1.0
        assert convert_sentiment_score("1 star") == -1.0
        # 4 stars -> 0.5
        assert convert_sentiment_score("4 star") == 0.5

    def test_convert_invalid_star(self):
        """Test that invalid star ratings return 0."""
        assert convert_sentiment_score("invalid star") == 0
        assert convert_sentiment_score("star") == 0

    def test_convert_other_string(self):
        """Test that non-star string values return 0."""
        assert convert_sentiment_score("positive") == 0
        assert convert_sentiment_score("negative") == 0


class TestGetDataDir:
    """Tests for the get_data_dir function."""

    def test_returns_string(self):
        """Test that get_data_dir returns a string path."""
        result = get_data_dir()
        assert isinstance(result, str)

    def test_contains_data(self):
        """Test that the returned path contains 'data'."""
        result = get_data_dir()
        assert 'data' in result.lower()


# Note: Testing load_data() requires mocking Streamlit's st.error and st.stop
# which is more complex. These tests would need to be added with proper mocking.
