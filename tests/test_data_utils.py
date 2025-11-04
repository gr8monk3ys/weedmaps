"""
Tests for the data_utils module.
"""
import pytest
import pandas as pd
from app.utils.data_utils import (
    normalize_county_name,
    add_county_suffix,
    normalize_dataframe_counties,
    validate_county_names
)


class TestNormalizeCountyName:
    """Tests for normalize_county_name function."""

    def test_removes_county_suffix(self):
        """Test that ' County' suffix is removed."""
        assert normalize_county_name("Los Angeles County") == "Los Angeles"
        assert normalize_county_name("San Francisco County") == "San Francisco"

    def test_already_normalized(self):
        """Test that names without suffix are unchanged."""
        assert normalize_county_name("Los Angeles") == "Los Angeles"
        assert normalize_county_name("San Francisco") == "San Francisco"

    def test_case_insensitive_suffix(self):
        """Test that suffix removal is case-insensitive."""
        assert normalize_county_name("Los Angeles COUNTY") == "Los Angeles"
        assert normalize_county_name("Los Angeles county") == "Los Angeles"

    def test_strips_whitespace(self):
        """Test that leading/trailing whitespace is removed."""
        assert normalize_county_name("  Los Angeles County  ") == "Los Angeles"
        assert normalize_county_name("  Los Angeles  ") == "Los Angeles"

    def test_none_input(self):
        """Test that None input returns None."""
        assert normalize_county_name(None) is None

    def test_nan_input(self):
        """Test that pandas NA input returns None."""
        assert normalize_county_name(pd.NA) is None
        assert normalize_county_name(float('nan')) is None

    def test_empty_string(self):
        """Test that empty string returns None."""
        assert normalize_county_name("") is None
        assert normalize_county_name("   ") is None

    def test_non_string_input(self):
        """Test that non-string inputs are converted to string."""
        assert normalize_county_name(123) == "123"


class TestAddCountySuffix:
    """Tests for add_county_suffix function."""

    def test_adds_county_suffix(self):
        """Test that ' County' suffix is added."""
        assert add_county_suffix("Los Angeles") == "Los Angeles County"
        assert add_county_suffix("San Francisco") == "San Francisco County"

    def test_already_has_suffix(self):
        """Test that suffix is not duplicated."""
        assert add_county_suffix("Los Angeles County") == "Los Angeles County"
        assert add_county_suffix("San Francisco County") == "San Francisco County"

    def test_case_insensitive_suffix(self):
        """Test that existing suffix check is case-insensitive."""
        assert add_county_suffix("Los Angeles COUNTY") == "Los Angeles COUNTY"
        assert add_county_suffix("Los Angeles county") == "Los Angeles county"

    def test_strips_whitespace(self):
        """Test that leading/trailing whitespace is removed."""
        assert add_county_suffix("  Los Angeles  ") == "Los Angeles County"

    def test_none_input(self):
        """Test that None input returns None."""
        assert add_county_suffix(None) is None

    def test_nan_input(self):
        """Test that pandas NA input returns None."""
        assert add_county_suffix(pd.NA) is None
        assert add_county_suffix(float('nan')) is None

    def test_empty_string(self):
        """Test that empty string returns None."""
        assert add_county_suffix("") is None
        assert add_county_suffix("   ") is None

    def test_non_string_input(self):
        """Test that non-string inputs are converted to string."""
        assert add_county_suffix(123) == "123 County"


class TestNormalizeDataframeCounties:
    """Tests for normalize_dataframe_counties function."""

    def test_normalizes_county_column(self):
        """Test that county names in DataFrame are normalized."""
        df = pd.DataFrame({
            "County": ["Los Angeles County", "San Francisco County", "San Diego"],
            "Value": [1, 2, 3]
        })
        result = normalize_dataframe_counties(df)
        assert result["County"].tolist() == ["Los Angeles", "San Francisco", "San Diego"]
        # Original dataframe should not be modified
        assert df["County"].tolist() == ["Los Angeles County", "San Francisco County", "San Diego"]

    def test_handles_none_values(self):
        """Test that None values are handled correctly."""
        df = pd.DataFrame({
            "County": ["Los Angeles County", None, "San Diego"],
            "Value": [1, 2, 3]
        })
        result = normalize_dataframe_counties(df)
        assert result["County"].tolist()[0] == "Los Angeles"
        assert pd.isna(result["County"].tolist()[1])
        assert result["County"].tolist()[2] == "San Diego"

    def test_custom_column_name(self):
        """Test that custom column name works."""
        df = pd.DataFrame({
            "Location": ["Los Angeles County", "San Francisco County"],
            "Value": [1, 2]
        })
        result = normalize_dataframe_counties(df, column_name="Location")
        assert result["Location"].tolist() == ["Los Angeles", "San Francisco"]

    def test_missing_column_raises_error(self):
        """Test that missing column raises ValueError."""
        df = pd.DataFrame({
            "NotCounty": ["Los Angeles County"],
            "Value": [1]
        })
        with pytest.raises(ValueError, match="Column 'County' not found"):
            normalize_dataframe_counties(df)

    def test_empty_dataframe(self):
        """Test that empty DataFrame is handled correctly."""
        df = pd.DataFrame({"County": []})
        result = normalize_dataframe_counties(df)
        assert len(result) == 0


class TestValidateCountyNames:
    """Tests for validate_county_names function."""

    def test_all_valid_counties(self):
        """Test that all valid counties return True."""
        df = pd.DataFrame({
            "County": ["Los Angeles County", "San Francisco County"]
        })
        known = ["Los Angeles", "San Francisco", "San Diego"]
        is_valid, invalid = validate_county_names(df, known_counties=known)
        assert is_valid is True
        assert invalid == []

    def test_some_invalid_counties(self):
        """Test that invalid counties are detected."""
        df = pd.DataFrame({
            "County": ["Los Angeles County", "Invalid County", "San Francisco"]
        })
        known = ["Los Angeles", "San Francisco"]
        is_valid, invalid = validate_county_names(df, known_counties=known)
        assert is_valid is False
        assert "Invalid County" in invalid

    def test_normalizes_before_validation(self):
        """Test that counties are normalized before validation."""
        df = pd.DataFrame({
            "County": ["Los Angeles County", "San Francisco"]
        })
        # Known counties provided without suffix
        known = ["Los Angeles", "San Francisco"]
        is_valid, invalid = validate_county_names(df, known_counties=known)
        assert is_valid is True
        assert invalid == []

    def test_no_known_counties_checks_nulls(self):
        """Test that without known counties, only checks for nulls."""
        df = pd.DataFrame({
            "County": ["Los Angeles", "San Francisco", None]
        })
        is_valid, invalid = validate_county_names(df, known_counties=None)
        assert is_valid is False

    def test_custom_column_name(self):
        """Test that custom column name works."""
        df = pd.DataFrame({
            "Location": ["Los Angeles County", "San Francisco County"]
        })
        known = ["Los Angeles", "San Francisco"]
        is_valid, invalid = validate_county_names(df, column_name="Location", known_counties=known)
        assert is_valid is True

    def test_missing_column_raises_error(self):
        """Test that missing column raises ValueError."""
        df = pd.DataFrame({
            "NotCounty": ["Los Angeles"]
        })
        with pytest.raises(ValueError, match="Column 'County' not found"):
            validate_county_names(df)

    def test_empty_dataframe(self):
        """Test that empty DataFrame is valid."""
        df = pd.DataFrame({"County": []})
        known = ["Los Angeles"]
        is_valid, invalid = validate_county_names(df, known_counties=known)
        assert is_valid is True
        assert invalid == []

    def test_duplicate_counties(self):
        """Test that duplicate counties don't cause issues."""
        df = pd.DataFrame({
            "County": ["Los Angeles", "Los Angeles", "San Francisco"]
        })
        known = ["Los Angeles", "San Francisco"]
        is_valid, invalid = validate_county_names(df, known_counties=known)
        assert is_valid is True
        assert invalid == []
