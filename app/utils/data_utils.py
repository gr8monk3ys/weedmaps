"""
Data utility functions for common transformations and cleaning operations.
"""
import pandas as pd
from typing import Optional, List, Tuple


def normalize_county_name(name: Optional[str]) -> Optional[str]:
    """
    Normalize county names to a consistent format (without " County" suffix).

    This function ensures county names are consistent across the application,
    which is important for matching with GeoJSON features and merging datasets.

    Args:
        name (str): County name to normalize (e.g., "Los Angeles County" or "Los Angeles")

    Returns:
        str: Normalized county name without " County" suffix, or None if input is None/empty

    Examples:
        >>> normalize_county_name("Los Angeles County")
        "Los Angeles"
        >>> normalize_county_name("Los Angeles")
        "Los Angeles"
        >>> normalize_county_name("  San Francisco County  ")
        "San Francisco"
        >>> normalize_county_name(None)
        None
    """
    # Check for NA values first (before boolean evaluation)
    if pd.isna(name):
        return None

    if not name:
        return None

    # Convert to string and strip whitespace
    normalized = str(name).strip()

    # Check if empty after stripping
    if not normalized:
        return None

    # Remove " County" suffix if present (case-insensitive)
    if normalized.lower().endswith(" county"):
        normalized = normalized[:-7].strip()

    return normalized


def add_county_suffix(name: Optional[str]) -> Optional[str]:
    """
    Add " County" suffix to county name if not already present.

    Args:
        name: County name (e.g., "Los Angeles" or "Los Angeles County")

    Returns:
        County name with " County" suffix, or None if input is None/empty

    Examples:
        >>> add_county_suffix("Los Angeles")
        "Los Angeles County"
        >>> add_county_suffix("Los Angeles County")
        "Los Angeles County"
        >>> add_county_suffix(None)
        None
    """
    # Check for NA values first (before boolean evaluation)
    if pd.isna(name):
        return None

    if not name:
        return None

    # Convert to string and strip whitespace
    formatted = str(name).strip()

    # Check if empty after stripping
    if not formatted:
        return None

    # Add " County" suffix if not present (case-insensitive)
    if not formatted.lower().endswith(" county"):
        formatted = f"{formatted} County"

    return formatted


def normalize_dataframe_counties(df: pd.DataFrame, column_name: str = "County") -> pd.DataFrame:
    """
    Normalize county names in a DataFrame column.

    Args:
        df: DataFrame containing county names
        column_name: Name of the column containing county names

    Returns:
        DataFrame with normalized county names

    Example:
        >>> df = pd.DataFrame({"County": ["Los Angeles County", "San Diego County"]})
        >>> normalized_df = normalize_dataframe_counties(df)
        >>> normalized_df["County"].tolist()
        ["Los Angeles", "San Diego"]
    """
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in DataFrame")

    df_copy = df.copy()
    df_copy[column_name] = df_copy[column_name].apply(normalize_county_name)

    return df_copy


def validate_county_names(
    df: pd.DataFrame,
    column_name: str = "County",
    known_counties: Optional[List[str]] = None
) -> Tuple[bool, List[str]]:
    """
    Validate that county names in a DataFrame match a list of known counties.

    Args:
        df: DataFrame containing county names
        column_name: Name of the column containing county names
        known_counties: List of valid county names (normalized, without " County")

    Returns:
        Tuple of (bool, list of invalid counties)

    Example:
        >>> df = pd.DataFrame({"County": ["Los Angeles", "Invalid County"]})
        >>> valid_counties = ["Los Angeles", "San Diego"]
        >>> is_valid, invalid = validate_county_names(df, known_counties=valid_counties)
        >>> is_valid
        False
        >>> invalid
        ["Invalid County"]
    """
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in DataFrame")

    if known_counties is None:
        # If no known counties provided, just check for non-null values
        invalid = df[df[column_name].isna()][column_name].tolist()
        return len(invalid) == 0, invalid

    # Normalize known counties
    known_normalized = {normalize_county_name(c) for c in known_counties}

    # Find counties not in the known list
    invalid = []
    for county in df[column_name].dropna().unique():
        normalized = normalize_county_name(county)
        if normalized not in known_normalized:
            invalid.append(county)

    return len(invalid) == 0, invalid
