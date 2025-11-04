"""
Regional definitions for California counties.

This module contains standardized regional groupings used throughout the application
for analyzing and visualizing cannabis market data by region.
"""

# Detailed regional breakdown - used in Geographic Analysis
CALIFORNIA_REGIONS = {
    "Northern California": [
        "Del Norte",
        "Siskiyou",
        "Modoc",
        "Humboldt",
        "Trinity",
        "Shasta",
        "Lassen",
        "Tehama",
        "Plumas",
        "Mendocino",
        "Glenn",
        "Butte",
        "Sierra",
        "Lake",
        "Colusa",
        "Yuba",
        "Nevada",
        "Placer",
        "Sutter",
        "Yolo",
        "El Dorado",
        "Sacramento",
        "Amador",
        "Solano",
        "Napa",
        "Sonoma",
        "Marin",
    ],
    "Central California": [
        "San Joaquin",
        "Calaveras",
        "Alpine",
        "Tuolumne",
        "Stanislaus",
        "Mono",
        "Merced",
        "Mariposa",
        "Madera",
        "Fresno",
        "Kings",
        "Tulare",
        "Inyo",
        "San Benito",
        "Monterey",
    ],
    "Southern California": [
        "San Luis Obispo",
        "Santa Barbara",
        "Ventura",
        "Los Angeles",
        "San Bernardino",
        "Orange",
        "Riverside",
        "San Diego",
        "Imperial",
    ],
}

# Simplified regional breakdown - used for high-level analysis
SIMPLE_REGIONS = {
    "Northern": [
        "Humboldt",
        "Mendocino",
        "Trinity",
        "Del Norte",
        "Siskiyou",
        "Shasta",
        "Tehama",
    ],
    "Bay Area": [
        "San Francisco",
        "Alameda",
        "Contra Costa",
        "San Mateo",
        "Santa Clara",
        "Marin",
        "Sonoma",
        "Napa",
        "Solano",
    ],
    "Central": [
        "Sacramento",
        "San Joaquin",
        "Stanislaus",
        "Merced",
        "Fresno",
        "Kings",
        "Tulare",
        "Kern",
    ],
    "Southern": [
        "Los Angeles",
        "Orange",
        "San Diego",
        "Riverside",
        "San Bernardino",
        "Ventura",
        "Santa Barbara",
    ],
}


def get_region_for_county(county_name, use_simple=False):
    """
    Get the region name for a given county.

    Args:
        county_name (str): Name of the county (with or without " County" suffix)
        use_simple (bool): If True, use SIMPLE_REGIONS, otherwise use CALIFORNIA_REGIONS

    Returns:
        str: Region name, or "Unknown" if county not found
    """
    # Clean county name
    clean_name = county_name.replace(" County", "").strip()

    regions = SIMPLE_REGIONS if use_simple else CALIFORNIA_REGIONS

    for region, counties in regions.items():
        if clean_name in counties:
            return region

    return "Unknown"
