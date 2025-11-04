"""
Tests for the filters module.
"""
import pytest
import pandas as pd
from app.utils.filters import (
    apply_dispensary_filters,
    apply_sentiment_filters,
    apply_density_filters,
    get_filter_summary,
    has_active_filters
)


class TestApplyDispensaryFilters:
    """Tests for apply_dispensary_filters function."""

    def test_no_filters_returns_all_data(self, sample_dispensaries_data):
        """Test that empty filters return all data."""
        filters = {}
        result = apply_dispensary_filters(sample_dispensaries_data, filters)
        assert len(result) == len(sample_dispensaries_data)

    def test_year_filter_single_year(self, sample_dispensaries_data):
        """Test filtering by a single year."""
        filters = {"years": (2020, 2020)}
        result = apply_dispensary_filters(sample_dispensaries_data, filters)
        assert len(result) == 3
        assert all(result["Year"] == 2020)

    def test_year_filter_range(self, sample_dispensaries_data):
        """Test filtering by a year range."""
        filters = {"years": (2020, 2021)}
        result = apply_dispensary_filters(sample_dispensaries_data, filters)
        assert len(result) == 5
        assert all((result["Year"] >= 2020) & (result["Year"] <= 2021))

    def test_license_type_filter(self, sample_dispensaries_data):
        """Test filtering by license designation."""
        filters = {"license_types": ["Adult-Use"]}
        result = apply_dispensary_filters(sample_dispensaries_data, filters)
        assert len(result) == 3
        assert all(result["License Designation"].isin(["Adult-Use"]))

    def test_multiple_license_types(self, sample_dispensaries_data):
        """Test filtering by multiple license types."""
        filters = {"license_types": ["Adult-Use", "Medicinal"]}
        result = apply_dispensary_filters(sample_dispensaries_data, filters)
        assert len(result) == 5

    def test_county_filter_old_format(self, sample_dispensaries_data):
        """Test filtering by single county (old format)."""
        filters = {"county": "Los Angeles County"}
        result = apply_dispensary_filters(sample_dispensaries_data, filters)
        assert len(result) == 2
        assert all(result["County"].str.contains("Los Angeles"))

    def test_county_filter_new_format(self, sample_dispensaries_data):
        """Test filtering by counties list (new format)."""
        filters = {"counties": ["Los Angeles County"]}
        result = apply_dispensary_filters(sample_dispensaries_data, filters)
        assert len(result) == 2
        assert all(result["County"].str.contains("Los Angeles"))

    def test_multiple_counties_new_format(self, sample_dispensaries_data):
        """Test filtering by multiple counties."""
        filters = {"counties": ["Los Angeles County", "San Diego County"]}
        result = apply_dispensary_filters(sample_dispensaries_data, filters)
        assert len(result) == 4
        assert all(result["County"].isin(["Los Angeles County", "San Diego County"]))

    def test_all_counties_returns_all_data(self, sample_dispensaries_data):
        """Test that 'All Counties' returns all data."""
        filters = {"counties": ["All Counties"]}
        result = apply_dispensary_filters(sample_dispensaries_data, filters)
        assert len(result) == len(sample_dispensaries_data)

    def test_county_normalization(self, sample_dispensaries_data):
        """Test that county names are normalized correctly."""
        # Add data with different county name formats
        data = sample_dispensaries_data.copy()
        filters = {"counties": ["Los Angeles"]}  # Without "County" suffix
        result = apply_dispensary_filters(data, filters)
        assert len(result) == 2

    def test_combined_filters(self, sample_dispensaries_data):
        """Test combining multiple filters."""
        filters = {
            "years": (2020, 2020),
            "license_types": ["Adult-Use"],
            "counties": ["Los Angeles County", "San Diego County"]
        }
        result = apply_dispensary_filters(sample_dispensaries_data, filters)
        assert len(result) == 2
        assert all(result["Year"] == 2020)
        assert all(result["License Designation"] == "Adult-Use")

    def test_empty_result_from_filters(self, sample_dispensaries_data):
        """Test that filters can result in empty dataset."""
        filters = {
            "years": (2025, 2025)  # Year that doesn't exist in data
        }
        result = apply_dispensary_filters(sample_dispensaries_data, filters)
        assert len(result) == 0

    def test_missing_year_column(self, sample_dispensaries_data):
        """Test graceful handling when Year column is missing."""
        data = sample_dispensaries_data.drop(columns=["Year"])
        filters = {"years": (2020, 2021)}
        result = apply_dispensary_filters(data, filters)
        assert len(result) == len(data)  # Should return all data if column missing

    def test_missing_license_column(self, sample_dispensaries_data):
        """Test graceful handling when License Designation column is missing."""
        data = sample_dispensaries_data.drop(columns=["License Designation"])
        filters = {"license_types": ["Adult-Use"]}
        result = apply_dispensary_filters(data, filters)
        assert len(result) == len(data)


class TestApplySentimentFilters:
    """Tests for apply_sentiment_filters function."""

    def test_no_filters_returns_all_data(self, sample_sentiment_data):
        """Test that empty filters return all data."""
        filters = {}
        result = apply_sentiment_filters(sample_sentiment_data, filters)
        assert len(result) == len(sample_sentiment_data)

    def test_year_filter(self, sample_sentiment_data):
        """Test filtering by year."""
        filters = {"years": (2020, 2020)}
        result = apply_sentiment_filters(sample_sentiment_data, filters)
        assert len(result) == 3
        assert all(result["Year"] == 2020)

    def test_county_filter_old_format(self, sample_sentiment_data):
        """Test filtering by single county (old format)."""
        filters = {"county": "Los Angeles County"}
        result = apply_sentiment_filters(sample_sentiment_data, filters)
        assert len(result) == 2

    def test_county_filter_new_format(self, sample_sentiment_data):
        """Test filtering by counties list (new format)."""
        filters = {"counties": ["Los Angeles County", "San Diego County"]}
        result = apply_sentiment_filters(sample_sentiment_data, filters)
        assert len(result) == 4

    def test_all_counties_returns_all_data(self, sample_sentiment_data):
        """Test that 'All Counties' returns all data."""
        filters = {"counties": ["All Counties"]}
        result = apply_sentiment_filters(sample_sentiment_data, filters)
        assert len(result) == len(sample_sentiment_data)

    def test_combined_filters(self, sample_sentiment_data):
        """Test combining year and county filters."""
        filters = {
            "years": (2020, 2020),
            "counties": ["Los Angeles County"]
        }
        result = apply_sentiment_filters(sample_sentiment_data, filters)
        assert len(result) == 1
        assert all(result["Year"] == 2020)


class TestApplyDensityFilters:
    """Tests for apply_density_filters function."""

    def test_no_filters_returns_all_data(self, sample_density_data):
        """Test that empty filters return all data."""
        filters = {}
        result = apply_density_filters(sample_density_data, filters)
        assert len(result) == len(sample_density_data)

    def test_year_filter(self, sample_density_data):
        """Test filtering by year."""
        filters = {"years": (2020, 2020)}
        result = apply_density_filters(sample_density_data, filters)
        assert len(result) == 3
        assert all(result["Year"] == 2020)

    def test_county_filter_old_format(self, sample_density_data):
        """Test filtering by single county (old format)."""
        filters = {"county": "Los Angeles County"}
        result = apply_density_filters(sample_density_data, filters)
        assert len(result) == 2

    def test_all_counties_returns_all_data(self, sample_density_data):
        """Test that 'All Counties' returns all data."""
        filters = {"county": "All Counties"}
        result = apply_density_filters(sample_density_data, filters)
        assert len(result) == len(sample_density_data)

    def test_combined_filters(self, sample_density_data):
        """Test combining year and county filters."""
        filters = {
            "years": (2020, 2021),
            "county": "Los Angeles County"
        }
        result = apply_density_filters(sample_density_data, filters)
        assert len(result) == 2
        assert all((result["Year"] >= 2020) & (result["Year"] <= 2021))


class TestGetFilterSummary:
    """Tests for get_filter_summary function."""

    def test_empty_filters(self):
        """Test summary with no filters."""
        filters = {}
        result = get_filter_summary(filters)
        assert result == "No filters applied"

    def test_single_year_filter(self):
        """Test summary with single year."""
        filters = {"years": (2020, 2020)}
        result = get_filter_summary(filters)
        assert "year 2020" in result

    def test_year_range_filter(self):
        """Test summary with year range."""
        filters = {"years": (2020, 2023)}
        result = get_filter_summary(filters)
        assert "2020-2023" in result

    def test_single_county_old_format(self):
        """Test summary with single county (old format)."""
        filters = {"county": "Los Angeles County"}
        result = get_filter_summary(filters)
        assert "Los Angeles" in result

    def test_single_county_new_format(self):
        """Test summary with single county (new format)."""
        filters = {"counties": ["Los Angeles County"]}
        result = get_filter_summary(filters)
        assert "Los Angeles" in result

    def test_multiple_counties(self):
        """Test summary with multiple counties."""
        filters = {"counties": ["Los Angeles County", "San Diego County"]}
        result = get_filter_summary(filters)
        assert "2 counties" in result

    def test_all_counties(self):
        """Test summary with all counties selected."""
        filters = {"counties": ["All Counties"]}
        result = get_filter_summary(filters)
        assert "all counties" in result

    def test_all_license_types(self):
        """Test summary with all license types."""
        filters = {"license_types": ["Adult-Use", "Medicinal", "Adult-Use and Medicinal"]}
        result = get_filter_summary(filters)
        assert "all license types" in result

    def test_single_license_type(self):
        """Test summary with single license type."""
        filters = {"license_types": ["Adult-Use"]}
        result = get_filter_summary(filters)
        assert "Adult-Use" in result

    def test_multiple_license_types(self):
        """Test summary with multiple license types."""
        filters = {"license_types": ["Adult-Use", "Medicinal"]}
        result = get_filter_summary(filters)
        assert "2 license types" in result

    def test_combined_filters_summary(self):
        """Test summary with all filters combined."""
        filters = {
            "years": (2020, 2023),
            "counties": ["Los Angeles County"],
            "license_types": ["Adult-Use"]
        }
        result = get_filter_summary(filters)
        assert "2020-2023" in result
        assert "Los Angeles" in result
        assert "Adult-Use" in result


class TestHasActiveFilters:
    """Tests for has_active_filters function."""

    def test_no_filters(self):
        """Test that empty filters are not active."""
        filters = {}
        assert has_active_filters(filters) is False

    def test_default_year_range_not_active(self):
        """Test that default year range (2018-2024) is not considered active."""
        filters = {"years": (2018, 2024)}
        assert has_active_filters(filters) is False

    def test_restricted_year_range_is_active(self):
        """Test that restricted year range is considered active."""
        filters = {"years": (2020, 2022)}
        assert has_active_filters(filters) is True

    def test_single_county_old_format_is_active(self):
        """Test that single county (old format) is active."""
        filters = {"county": "Los Angeles County"}
        assert has_active_filters(filters) is True

    def test_all_counties_old_format_not_active(self):
        """Test that 'All Counties' (old format) is not active."""
        filters = {"county": "All Counties"}
        assert has_active_filters(filters) is False

    def test_single_county_new_format_is_active(self):
        """Test that single county (new format) is active."""
        filters = {"counties": ["Los Angeles County"]}
        assert has_active_filters(filters) is True

    def test_multiple_counties_new_format_is_active(self):
        """Test that multiple counties (new format) is active."""
        filters = {"counties": ["Los Angeles County", "San Diego County"]}
        assert has_active_filters(filters) is True

    def test_all_counties_new_format_not_active(self):
        """Test that 'All Counties' (new format) is not active."""
        filters = {"counties": ["All Counties"]}
        assert has_active_filters(filters) is False

    def test_all_license_types_not_active(self):
        """Test that all 3 license types is not considered active."""
        filters = {"license_types": ["Adult-Use", "Medicinal", "Adult-Use and Medicinal"]}
        assert has_active_filters(filters) is False

    def test_restricted_license_types_is_active(self):
        """Test that less than 3 license types is considered active."""
        filters = {"license_types": ["Adult-Use"]}
        assert has_active_filters(filters) is True

    def test_combined_default_filters_not_active(self):
        """Test that all default values together are not active."""
        filters = {
            "years": (2018, 2024),
            "county": "All Counties",
            "license_types": ["Adult-Use", "Medicinal", "Adult-Use and Medicinal"]
        }
        assert has_active_filters(filters) is False

    def test_any_active_filter_returns_true(self):
        """Test that any single active filter returns True."""
        # Active year
        assert has_active_filters({"years": (2020, 2020)}) is True
        # Active county
        assert has_active_filters({"county": "Los Angeles"}) is True
        # Active license types
        assert has_active_filters({"license_types": ["Adult-Use"]}) is True
