"""
Module for loading and processing data from various sources.
"""

import os
import pandas as pd
import streamlit as st
from .load_geojson import load_geojson
from .error_messages import (
    show_file_missing_error,
    show_column_missing_error,
    show_loading_error
)


def get_data_dir():
    """Get the path to the data directory."""
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(os.path.dirname(current_dir), "data")


def convert_sentiment_score(score):
    """Convert sentiment score from string format to numeric."""
    if pd.isna(score):
        return 0

    # If it's already numeric, return as is
    if isinstance(score, (int, float)):
        return float(score)

    # Convert star ratings to numeric scale
    if isinstance(score, str) and "star" in score.lower():
        try:
            stars = float(score.split()[0])
            # Convert 5-star scale to -1 to 1 scale
            return (stars - 3) / 2
        except (ValueError, IndexError):
            return 0

    # For other string values, default to 0
    return 0


# Required columns for each dataset
REQUIRED_COLUMNS = {
    "dispensaries": ["County", "Year", "License Number", "Dispensary Name", "License Type"],
    "density": ["County", "Dispensary_PerCapita", "Population"],
    "tweet_sentiment": ["BERT_Sentiment", "County"]
}


@st.cache_data
def load_data():
    """
    Load all data files and return them as a dictionary.

    This function is cached to improve performance. Data is loaded once
    and reused across page views within the same session.

    Returns:
        dict: Dictionary containing processed data frames

    Raises:
        FileNotFoundError: If required data files are missing
        ValueError: If required columns are missing from data files
    """
    data_dir = get_data_dir()

    # Validate required files exist
    required_files = {
        "Dispensaries.csv": ["County"],
        "Dispensary_Density.csv": ["County", "Dispensary_PerCapita"],
        "Tweet_Sentiment.csv": ["BERT_Sentiment"],
        "California_County_Boundaries.geojson": None
    }

    for filename in required_files.keys():
        file_path = os.path.join(data_dir, filename)
        if not os.path.exists(file_path):
            show_file_missing_error(filename, file_path)
            st.stop()

    # Load dispensaries data
    try:
        dispensaries = pd.read_csv(
            os.path.join(data_dir, "Dispensaries.csv"), index_col=None
        )

        if dispensaries.empty:
            st.warning("⚠️ Dispensaries.csv is empty")

        # Derive Year from License_Date if Year column doesn't exist
        if "Year" not in dispensaries.columns and "License_Date" in dispensaries.columns:
            dispensaries["Year"] = pd.to_datetime(dispensaries["License_Date"]).dt.year

        # Validate all required columns for dispensaries
        missing_cols = [col for col in REQUIRED_COLUMNS["dispensaries"] if col not in dispensaries.columns]
        if missing_cols:
            show_column_missing_error(
                "Dispensaries.csv",
                missing_cols,
                REQUIRED_COLUMNS["dispensaries"]
            )
            st.stop()
    except Exception as e:
        show_loading_error("Dispensaries.csv", str(e))
        st.stop()

    # Load density data
    try:
        density = pd.read_csv(
            os.path.join(data_dir, "Dispensary_Density.csv"), index_col=None
        )

        if density.empty:
            st.warning("⚠️ Dispensary_Density.csv is empty")

        # Validate all required columns for density
        missing_cols = [col for col in REQUIRED_COLUMNS["density"] if col not in density.columns]
        if missing_cols:
            show_column_missing_error(
                "Dispensary_Density.csv",
                missing_cols,
                REQUIRED_COLUMNS["density"]
            )
            st.stop()
    except Exception as e:
        show_loading_error("Dispensary_Density.csv", str(e))
        st.stop()

    # Load tweet sentiment data and process
    try:
        tweet_sentiment = pd.read_csv(
            os.path.join(data_dir, "Tweet_Sentiment.csv"), index_col=None
        )

        if tweet_sentiment.empty:
            st.warning("⚠️ Tweet_Sentiment.csv is empty")

        # Validate all required columns for tweet_sentiment
        missing_cols = [col for col in REQUIRED_COLUMNS["tweet_sentiment"] if col not in tweet_sentiment.columns]
        if missing_cols:
            show_column_missing_error(
                "Tweet_Sentiment.csv",
                missing_cols,
                REQUIRED_COLUMNS["tweet_sentiment"]
            )
            st.stop()
    except Exception as e:
        show_loading_error("Tweet_Sentiment.csv", str(e))
        st.stop()

    # Convert sentiment scores
    tweet_sentiment["BERT_Sentiment"] = tweet_sentiment["BERT_Sentiment"].apply(
        convert_sentiment_score
    )

    # Handle date columns
    date_columns = ["Tweet_Date", "Created_At", "Date"]
    for col in date_columns:
        if col in tweet_sentiment.columns:
            try:
                tweet_sentiment[col] = pd.to_datetime(tweet_sentiment[col])
            except (ValueError, TypeError):
                continue

    # If no valid date column exists, create one based on index
    if not any(col in tweet_sentiment.columns for col in date_columns):
        st.warning(
            "⚠️ No date column found in Tweet_Sentiment.csv. "
            "Using synthetic dates starting from 2020-01-01. "
            "Temporal analysis may not reflect actual dates."
        )
        tweet_sentiment["Tweet_Date"] = pd.date_range(
            start="2020-01-01", periods=len(tweet_sentiment), freq="D"
        )

    # Ensure we have a primary date column
    if "Tweet_Date" not in tweet_sentiment.columns:
        for col in ["Created_At", "Date"]:
            if col in tweet_sentiment.columns:
                tweet_sentiment["Tweet_Date"] = tweet_sentiment[col]
                break

    # Load GeoJSON with error handling
    try:
        ca_counties = load_geojson(
            os.path.join(data_dir, "California_County_Boundaries.geojson")
        )
    except Exception as e:
        show_loading_error("California_County_Boundaries.geojson", str(e))
        st.stop()

    data = {
        "dispensaries": dispensaries,
        "density": density,
        "tweet_sentiment": tweet_sentiment,
        "ca_counties": ca_counties,
    }

    return data
