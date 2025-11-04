"""
Tests for the configuration modules.
"""
import pytest
from app.config.regions import (
    CALIFORNIA_REGIONS,
    SIMPLE_REGIONS,
    get_region_for_county
)
from app.config.theme import (
    PLOTLY_THEME,
    GREEN_PALETTE,
    get_default_layout,
    COLOR_SCALES
)


class TestRegions:
    """Tests for region configuration."""

    def test_california_regions_structure(self):
        """Test that CALIFORNIA_REGIONS has expected structure."""
        assert isinstance(CALIFORNIA_REGIONS, dict)
        assert "Northern California" in CALIFORNIA_REGIONS
        assert "Central California" in CALIFORNIA_REGIONS
        assert "Southern California" in CALIFORNIA_REGIONS

    def test_simple_regions_structure(self):
        """Test that SIMPLE_REGIONS has expected structure."""
        assert isinstance(SIMPLE_REGIONS, dict)
        assert "Northern" in SIMPLE_REGIONS
        assert "Bay Area" in SIMPLE_REGIONS
        assert "Central" in SIMPLE_REGIONS
        assert "Southern" in SIMPLE_REGIONS

    def test_all_regions_have_counties(self):
        """Test that all regions contain county lists."""
        for region, counties in CALIFORNIA_REGIONS.items():
            assert isinstance(counties, list)
            assert len(counties) > 0

        for region, counties in SIMPLE_REGIONS.items():
            assert isinstance(counties, list)
            assert len(counties) > 0

    def test_get_region_for_county_simple(self):
        """Test getting region for a county using simple regions."""
        assert get_region_for_county("Los Angeles", use_simple=True) == "Southern"
        assert get_region_for_county("San Francisco", use_simple=True) == "Bay Area"
        assert get_region_for_county("Sacramento", use_simple=True) == "Central"
        assert get_region_for_county("Humboldt", use_simple=True) == "Northern"

    def test_get_region_for_county_detailed(self):
        """Test getting region for a county using detailed regions."""
        assert get_region_for_county("Los Angeles", use_simple=False) == "Southern California"
        assert get_region_for_county("Marin", use_simple=False) == "Northern California"

    def test_get_region_for_county_with_suffix(self):
        """Test that county names with 'County' suffix work."""
        assert get_region_for_county("Los Angeles County", use_simple=True) == "Southern"

    def test_get_region_for_unknown_county(self):
        """Test that unknown counties return 'Unknown'."""
        assert get_region_for_county("Fake County") == "Unknown"


class TestTheme:
    """Tests for theme configuration."""

    def test_plotly_theme_is_string(self):
        """Test that PLOTLY_THEME is a valid string."""
        assert isinstance(PLOTLY_THEME, str)
        assert len(PLOTLY_THEME) > 0

    def test_green_palette_structure(self):
        """Test that GREEN_PALETTE has expected color keys."""
        required_keys = ["primary", "secondary", "accent", "dark", "light"]
        for key in required_keys:
            assert key in GREEN_PALETTE
            assert isinstance(GREEN_PALETTE[key], str)
            assert GREEN_PALETTE[key].startswith("#")

    def test_color_scales_structure(self):
        """Test that COLOR_SCALES has expected keys."""
        assert "sequential" in COLOR_SCALES
        assert "diverging" in COLOR_SCALES
        assert "categorical" in COLOR_SCALES
        assert isinstance(COLOR_SCALES["categorical"], list)

    def test_get_default_layout_basic(self):
        """Test basic layout generation."""
        layout = get_default_layout()
        assert "template" in layout
        assert layout["template"] == PLOTLY_THEME
        assert "paper_bgcolor" in layout
        assert "plot_bgcolor" in layout

    def test_get_default_layout_with_height(self):
        """Test layout generation with custom height."""
        layout = get_default_layout(height=500)
        assert layout["height"] == 500

    def test_get_default_layout_with_title(self):
        """Test layout generation with custom title."""
        layout = get_default_layout(title="Test Chart")
        assert "title" in layout
        assert layout["title"]["text"] == "Test Chart"
