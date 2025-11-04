"""
Module for generating and managing the application sidebar.
"""
import streamlit as st
from typing import Dict, List, Tuple, Any
from .data_loader import load_data


@st.cache_data
def get_filter_options() -> Dict[str, List]:
    """
    Get available filter options from the data.
    Cached to avoid reloading data on every sidebar render.

    Returns:
        Dictionary containing available filter options:
            - years: List[int] - Available years
            - license_types: List[str] - Available license types
            - counties: List[str] - Available counties
    """
    data = load_data()
    dispensaries = data['dispensaries']

    # Get unique years (sorted)
    years = sorted(dispensaries['Year'].dropna().unique().astype(int).tolist())

    # Get unique license types (sorted)
    license_types = sorted(dispensaries['License Type'].dropna().unique().tolist())

    # Get unique counties (sorted)
    counties = sorted(dispensaries['County'].dropna().unique().tolist())

    return {
        'years': years,
        'license_types': license_types,
        'counties': counties
    }


def generate_sidebar() -> Dict[str, Any]:
    """
    Generate the application sidebar with filters and information.

    Returns:
        Dictionary containing the selected filter values:
            - years: Tuple[int, int] - Selected year range (start, end)
            - license_types: List[str] - Selected license types
            - counties: List[str] - Selected counties (including "All Counties" if selected)
    """
    # Get dynamic filter options from data
    filter_options = get_filter_options()

    with st.sidebar:
        # Title and logo
        st.markdown('<p class="sidebar-header">Cannabis Analytics</p>', unsafe_allow_html=True)

        # About section
        st.markdown('<p class="sidebar-subheader">About</p>', unsafe_allow_html=True)
        st.markdown("""
            This dashboard provides insights into California's cannabis retail market,
            combining dispensary data with social media sentiment analysis.
        """)

        # Time period filter
        st.markdown('<p class="sidebar-subheader">Filters</p>', unsafe_allow_html=True)

        years = filter_options['years']
        selected_years = st.select_slider(
            "Time Period",
            options=years,
            value=(min(years), max(years))
        )

        # License type filter
        license_types = filter_options['license_types']
        selected_types = st.multiselect(
            "License Types",
            options=license_types,
            default=license_types
        )

        # County filter (multiselect to allow filtering by multiple counties)
        counties = filter_options['counties']
        selected_counties = st.multiselect(
            "Counties",
            options=["All Counties"] + counties,
            default=["All Counties"],
            help="Select one or more counties to filter data"
        )

        # Return filters
        return {
            "years": selected_years,
            "license_types": selected_types,
            "counties": selected_counties
        }
