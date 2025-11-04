"""
Module for loading and processing GeoJSON data.
"""
import json

def load_geojson(file_path):
    """
    Load and validate GeoJSON data from a file.

    Args:
        file_path (str): Path to the GeoJSON file

    Returns:
        dict: Loaded and validated GeoJSON data

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the GeoJSON structure is invalid
        json.JSONDecodeError: If the file contains invalid JSON
    """
    # Load the JSON file
    try:
        with open(file_path, encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in GeoJSON file '{file_path}': {str(e)}")
    except FileNotFoundError:
        raise FileNotFoundError(f"GeoJSON file not found: '{file_path}'")

    # Validate GeoJSON structure
    if not isinstance(data, dict):
        raise ValueError(f"GeoJSON must be a dictionary, got {type(data).__name__}")

    # Check for FeatureCollection type
    geojson_type = data.get("type")
    if geojson_type != "FeatureCollection":
        raise ValueError(
            f"GeoJSON must be a FeatureCollection, got type='{geojson_type}'"
        )

    # Validate features array exists
    if "features" not in data:
        raise ValueError("GeoJSON FeatureCollection must contain 'features' array")

    features = data["features"]
    if not isinstance(features, list):
        raise ValueError(
            f"GeoJSON 'features' must be a list, got {type(features).__name__}"
        )

    if len(features) == 0:
        raise ValueError("GeoJSON FeatureCollection contains no features")

    # Validate feature structure (sample first few features)
    for i, feature in enumerate(features[:5]):  # Check first 5 features
        if not isinstance(feature, dict):
            raise ValueError(
                f"Feature {i} is not a dictionary, got {type(feature).__name__}"
            )

        if "type" not in feature or feature["type"] != "Feature":
            raise ValueError(f"Feature {i} missing or invalid 'type' field")

        if "geometry" not in feature:
            raise ValueError(f"Feature {i} missing 'geometry' field")

        if "properties" not in feature:
            raise ValueError(f"Feature {i} missing 'properties' field")

    return data
