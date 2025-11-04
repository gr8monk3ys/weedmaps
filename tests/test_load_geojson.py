"""
Tests for the load_geojson module.
"""
import pytest
import json
import tempfile
import os
from app.utils.load_geojson import load_geojson


class TestLoadGeoJSON:
    """Tests for load_geojson function."""

    def test_loads_valid_geojson(self, tmp_path):
        """Test that valid GeoJSON is loaded correctly."""
        geojson_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"NAME": "Los Angeles"},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[-118, 34], [-118, 35], [-117, 35], [-117, 34], [-118, 34]]]
                    }
                }
            ]
        }

        # Create temporary file
        geojson_file = tmp_path / "test.geojson"
        with open(geojson_file, 'w') as f:
            json.dump(geojson_data, f)

        result = load_geojson(str(geojson_file))
        assert result["type"] == "FeatureCollection"
        assert len(result["features"]) == 1
        assert result["features"][0]["properties"]["NAME"] == "Los Angeles"

    def test_file_not_found(self):
        """Test that FileNotFoundError is raised for non-existent file."""
        with pytest.raises(FileNotFoundError, match="GeoJSON file not found"):
            load_geojson("/nonexistent/path/file.geojson")

    def test_invalid_json(self, tmp_path):
        """Test that invalid JSON raises ValueError."""
        invalid_file = tmp_path / "invalid.geojson"
        with open(invalid_file, 'w') as f:
            f.write("{ invalid json }")

        with pytest.raises(ValueError, match="Invalid JSON"):
            load_geojson(str(invalid_file))

    def test_not_a_dictionary(self, tmp_path):
        """Test that non-dictionary JSON raises ValueError."""
        invalid_file = tmp_path / "array.geojson"
        with open(invalid_file, 'w') as f:
            json.dump(["not", "a", "dict"], f)

        with pytest.raises(ValueError, match="GeoJSON must be a dictionary"):
            load_geojson(str(invalid_file))

    def test_wrong_type(self, tmp_path):
        """Test that wrong type raises ValueError."""
        wrong_type_data = {
            "type": "Feature",  # Should be FeatureCollection
            "properties": {},
            "geometry": {}
        }

        geojson_file = tmp_path / "wrong_type.geojson"
        with open(geojson_file, 'w') as f:
            json.dump(wrong_type_data, f)

        with pytest.raises(ValueError, match="GeoJSON must be a FeatureCollection"):
            load_geojson(str(geojson_file))

    def test_missing_features(self, tmp_path):
        """Test that missing 'features' raises ValueError."""
        no_features_data = {
            "type": "FeatureCollection"
            # Missing 'features' key
        }

        geojson_file = tmp_path / "no_features.geojson"
        with open(geojson_file, 'w') as f:
            json.dump(no_features_data, f)

        with pytest.raises(ValueError, match="must contain 'features' array"):
            load_geojson(str(geojson_file))

    def test_features_not_list(self, tmp_path):
        """Test that non-list 'features' raises ValueError."""
        invalid_features_data = {
            "type": "FeatureCollection",
            "features": "not a list"
        }

        geojson_file = tmp_path / "invalid_features.geojson"
        with open(geojson_file, 'w') as f:
            json.dump(invalid_features_data, f)

        with pytest.raises(ValueError, match="'features' must be a list"):
            load_geojson(str(geojson_file))

    def test_empty_features(self, tmp_path):
        """Test that empty features array raises ValueError."""
        empty_features_data = {
            "type": "FeatureCollection",
            "features": []
        }

        geojson_file = tmp_path / "empty_features.geojson"
        with open(geojson_file, 'w') as f:
            json.dump(empty_features_data, f)

        with pytest.raises(ValueError, match="contains no features"):
            load_geojson(str(geojson_file))

    def test_invalid_feature_structure(self, tmp_path):
        """Test that invalid feature structure raises ValueError."""
        invalid_feature_data = {
            "type": "FeatureCollection",
            "features": [
                "not a dict"  # Should be a dictionary
            ]
        }

        geojson_file = tmp_path / "invalid_feature.geojson"
        with open(geojson_file, 'w') as f:
            json.dump(invalid_feature_data, f)

        with pytest.raises(ValueError, match="Feature 0 is not a dictionary"):
            load_geojson(str(geojson_file))

    def test_feature_missing_type(self, tmp_path):
        """Test that feature missing 'type' raises ValueError."""
        missing_type_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    # Missing "type": "Feature"
                    "properties": {},
                    "geometry": {}
                }
            ]
        }

        geojson_file = tmp_path / "missing_type.geojson"
        with open(geojson_file, 'w') as f:
            json.dump(missing_type_data, f)

        with pytest.raises(ValueError, match="Feature 0 missing or invalid 'type' field"):
            load_geojson(str(geojson_file))

    def test_feature_missing_geometry(self, tmp_path):
        """Test that feature missing 'geometry' raises ValueError."""
        missing_geometry_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {}
                    # Missing "geometry"
                }
            ]
        }

        geojson_file = tmp_path / "missing_geometry.geojson"
        with open(geojson_file, 'w') as f:
            json.dump(missing_geometry_data, f)

        with pytest.raises(ValueError, match="Feature 0 missing 'geometry' field"):
            load_geojson(str(geojson_file))

    def test_feature_missing_properties(self, tmp_path):
        """Test that feature missing 'properties' raises ValueError."""
        missing_properties_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]
                    }
                    # Missing "properties"
                }
            ]
        }

        geojson_file = tmp_path / "missing_properties.geojson"
        with open(geojson_file, 'w') as f:
            json.dump(missing_properties_data, f)

        with pytest.raises(ValueError, match="Feature 0 missing 'properties' field"):
            load_geojson(str(geojson_file))

    def test_validates_first_5_features_only(self, tmp_path):
        """Test that only first 5 features are validated."""
        # Create GeoJSON with 6 features, last one invalid
        features = []
        for i in range(6):
            if i < 5:
                # Valid features
                features.append({
                    "type": "Feature",
                    "properties": {"NAME": f"County {i}"},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]
                    }
                })
            else:
                # Invalid 6th feature (should not be validated)
                features.append({
                    "type": "Feature",
                    # Missing geometry and properties
                })

        geojson_data = {
            "type": "FeatureCollection",
            "features": features
        }

        geojson_file = tmp_path / "many_features.geojson"
        with open(geojson_file, 'w') as f:
            json.dump(geojson_data, f)

        # Should not raise error since 6th feature is not validated
        result = load_geojson(str(geojson_file))
        assert len(result["features"]) == 6

    def test_multiple_features(self, tmp_path):
        """Test that GeoJSON with multiple features loads correctly."""
        geojson_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"NAME": "Los Angeles"},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[-118, 34], [-118, 35], [-117, 35], [-117, 34], [-118, 34]]]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {"NAME": "San Francisco"},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[-122, 37], [-122, 38], [-121, 38], [-121, 37], [-122, 37]]]
                    }
                }
            ]
        }

        geojson_file = tmp_path / "multiple.geojson"
        with open(geojson_file, 'w') as f:
            json.dump(geojson_data, f)

        result = load_geojson(str(geojson_file))
        assert len(result["features"]) == 2
        assert result["features"][0]["properties"]["NAME"] == "Los Angeles"
        assert result["features"][1]["properties"]["NAME"] == "San Francisco"
