"""
Data filtering utilities for applying sidebar filters to datasets.
"""
import pandas as pd
from typing import Dict, List, Tuple, Any


def apply_dispensary_filters(
    dispensaries: pd.DataFrame,
    filters: Dict[str, Any]
) -> pd.DataFrame:
    """
    Apply sidebar filters to dispensary data.

    Args:
        dispensaries (pd.DataFrame): Dispensary dataset
        filters (dict): Filter dictionary from generate_sidebar()
            - years: tuple of (start_year, end_year)
            - license_types: list of selected license types
            - county: selected county name or "All Counties"

    Returns:
        pd.DataFrame: Filtered dispensary data

    Example:
        >>> from utils.generate_sidebar import generate_sidebar
        >>> from utils.filters import apply_dispensary_filters
        >>> from utils.data_loader import load_data
        >>>
        >>> data = load_data()
        >>> filters = generate_sidebar()
        >>> filtered = apply_dispensary_filters(data['dispensaries'], filters)
    """
    filtered_df = dispensaries.copy()

    # Apply year filter
    if "years" in filters and filters["years"]:
        start_year, end_year = filters["years"]
        if "Year" in filtered_df.columns:
            filtered_df = filtered_df[
                (filtered_df["Year"] >= start_year) &
                (filtered_df["Year"] <= end_year)
            ]

    # Apply license type filter
    if "license_types" in filters and filters["license_types"]:
        if "License Designation" in filtered_df.columns:
            filtered_df = filtered_df[
                filtered_df["License Designation"].isin(filters["license_types"])
            ]

    # Apply county filter (supports both "county" and "counties" keys)
    counties_to_filter = None
    if "counties" in filters and filters["counties"]:
        # New format: list of counties
        if "All Counties" not in filters["counties"]:
            counties_to_filter = filters["counties"]
    elif "county" in filters and filters["county"] != "All Counties":
        # Old format: single county (backward compatibility)
        counties_to_filter = [filters["county"]]

    if counties_to_filter and "County" in filtered_df.columns:
        from .data_utils import normalize_county_name
        # Normalize filter counties
        normalized_filter_counties = [normalize_county_name(c) for c in counties_to_filter]
        # Normalize dataframe counties
        filtered_df["_normalized_county"] = filtered_df["County"].apply(normalize_county_name)
        filtered_df = filtered_df[filtered_df["_normalized_county"].isin(normalized_filter_counties)]
        filtered_df = filtered_df.drop(columns=["_normalized_county"])

    return filtered_df


def apply_sentiment_filters(
    sentiment: pd.DataFrame,
    filters: Dict[str, Any]
) -> pd.DataFrame:
    """
    Apply sidebar filters to sentiment data.

    Args:
        sentiment (pd.DataFrame): Sentiment dataset
        filters (dict): Filter dictionary from generate_sidebar()

    Returns:
        pd.DataFrame: Filtered sentiment data
    """
    filtered_df = sentiment.copy()

    # Apply year filter
    if "years" in filters and filters["years"]:
        start_year, end_year = filters["years"]
        if "Year" in filtered_df.columns:
            filtered_df = filtered_df[
                (filtered_df["Year"] >= start_year) &
                (filtered_df["Year"] <= end_year)
            ]

    # Apply county filter (supports both "county" and "counties" keys)
    counties_to_filter = None
    if "counties" in filters and filters["counties"]:
        # New format: list of counties
        if "All Counties" not in filters["counties"]:
            counties_to_filter = filters["counties"]
    elif "county" in filters and filters["county"] != "All Counties":
        # Old format: single county (backward compatibility)
        counties_to_filter = [filters["county"]]

    if counties_to_filter and "County" in filtered_df.columns:
        from .data_utils import normalize_county_name
        # Normalize filter counties
        normalized_filter_counties = [normalize_county_name(c) for c in counties_to_filter]
        # Normalize dataframe counties
        filtered_df["_normalized_county"] = filtered_df["County"].apply(normalize_county_name)
        filtered_df = filtered_df[filtered_df["_normalized_county"].isin(normalized_filter_counties)]
        filtered_df = filtered_df.drop(columns=["_normalized_county"])

    return filtered_df


def apply_density_filters(
    density: pd.DataFrame,
    filters: Dict[str, Any]
) -> pd.DataFrame:
    """
    Apply sidebar filters to density data.

    Args:
        density (pd.DataFrame): Density dataset
        filters (dict): Filter dictionary from generate_sidebar()

    Returns:
        pd.DataFrame: Filtered density data
    """
    filtered_df = density.copy()

    # Apply year filter
    if "years" in filters and filters["years"]:
        start_year, end_year = filters["years"]
        if "Year" in filtered_df.columns:
            filtered_df = filtered_df[
                (filtered_df["Year"] >= start_year) &
                (filtered_df["Year"] <= end_year)
            ]

    # Apply county filter
    if "county" in filters and filters["county"] != "All Counties":
        if "County" in filtered_df.columns:
            from .data_utils import normalize_county_name
            filter_county = normalize_county_name(filters["county"])
            filtered_df["_normalized_county"] = filtered_df["County"].apply(normalize_county_name)
            filtered_df = filtered_df[filtered_df["_normalized_county"] == filter_county]
            filtered_df = filtered_df.drop(columns=["_normalized_county"])

    return filtered_df


def get_filter_summary(filters: Dict[str, Any]) -> str:
    """
    Generate a human-readable summary of active filters.

    Args:
        filters (dict): Filter dictionary from generate_sidebar()

    Returns:
        str: Human-readable filter summary

    Example:
        >>> filters = {"years": (2020, 2023), "county": "Los Angeles County"}
        >>> print(get_filter_summary(filters))
        "Showing data for 2020-2023, Los Angeles County, all license types"
    """
    parts = []

    # Year range
    if "years" in filters and filters["years"]:
        start_year, end_year = filters["years"]
        if start_year == end_year:
            parts.append(f"year {start_year}")
        else:
            parts.append(f"{start_year}-{end_year}")

    # County (supports both "county" and "counties" keys)
    if "counties" in filters and filters["counties"]:
        # New format: list of counties
        if "All Counties" in filters["counties"]:
            parts.append("all counties")
        else:
            from .data_utils import normalize_county_name
            normalized_counties = [normalize_county_name(c) for c in filters["counties"]]
            if len(normalized_counties) == 1:
                parts.append(normalized_counties[0])
            else:
                parts.append(f"{len(normalized_counties)} counties")
    elif "county" in filters:
        # Old format: single county (backward compatibility)
        if filters["county"] == "All Counties":
            parts.append("all counties")
        else:
            from .data_utils import normalize_county_name
            county = normalize_county_name(filters["county"])
            parts.append(county)

    # License types
    if "license_types" in filters and filters["license_types"]:
        types = filters["license_types"]
        if len(types) == 3:
            parts.append("all license types")
        elif len(types) == 1:
            parts.append(types[0])
        else:
            parts.append(f"{len(types)} license types")

    if not parts:
        return "No filters applied"

    return "Showing data for " + ", ".join(parts)


def has_active_filters(filters: Dict[str, Any]) -> bool:
    """
    Check if any filters are actively restricting data.

    Args:
        filters (dict): Filter dictionary from generate_sidebar()

    Returns:
        bool: True if filters are restricting data, False if showing all
    """
    # Check if year range is not max
    if "years" in filters and filters["years"]:
        start_year, end_year = filters["years"]
        if start_year != 2018 or end_year != 2024:
            return True

    # Check if county is not "All Counties" (supports both "county" and "counties" keys)
    if "counties" in filters and filters["counties"]:
        # New format: list of counties
        if "All Counties" not in filters["counties"]:
            return True
    elif "county" in filters and filters["county"] != "All Counties":
        # Old format: single county (backward compatibility)
        return True

    # Check if not all license types selected
    if "license_types" in filters and filters["license_types"]:
        if len(filters["license_types"]) < 3:  # Less than all 3 types
            return True

    return False
