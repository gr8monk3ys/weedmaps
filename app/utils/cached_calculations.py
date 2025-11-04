"""
Cached calculation functions for performance optimization.

These functions use @st.cache_data to avoid recalculating expensive aggregations
when the same data and parameters are used.
"""
import pandas as pd
import streamlit as st
from typing import Tuple, Dict, Any


@st.cache_data
def calculate_top_counties(
    density_df: pd.DataFrame,
    n: int = 10,
    metric_column: str = "Dispensary_PerCapita"
) -> pd.DataFrame:
    """
    Cache expensive top-N county calculation.

    Args:
        density_df: Density dataframe
        n: Number of top counties to return
        metric_column: Column to sort by

    Returns:
        DataFrame of top N counties
    """
    return density_df.nlargest(n, metric_column)


@st.cache_data
def calculate_yearly_growth(dispensaries_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate year-over-year growth metrics.

    Args:
        dispensaries_df: Dispensary dataframe with Year column

    Returns:
        DataFrame with yearly metrics and growth rates
    """
    yearly_data = (
        dispensaries_df.groupby("Year")
        .agg(
            {
                "License Number": "nunique",  # Count unique licenses
                "Dispensary Name": "nunique",  # Count unique dispensaries
            }
        )
        .reset_index()
    )

    yearly_data["Growth_Rate"] = yearly_data["Dispensary Name"].pct_change() * 100

    return yearly_data


@st.cache_data
def calculate_county_sentiment(
    sentiment_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate county-level sentiment aggregations.

    Args:
        sentiment_df: Sentiment dataframe with County and BERT_Sentiment columns

    Returns:
        DataFrame with county-level sentiment metrics
    """
    county_sentiment = (
        sentiment_df.groupby("County")
        .agg({"BERT_Sentiment": ["mean", "count", lambda x: (x > 0).mean() * 100]})
        .reset_index()
    )

    county_sentiment.columns = [
        "County",
        "Average Sentiment",
        "Tweet Count",
        "Positive Ratio",
    ]

    return county_sentiment.round(2)


@st.cache_data
def calculate_regional_density(
    density_df: pd.DataFrame,
    region_mapping: Dict[str, Any]
) -> pd.DataFrame:
    """
    Calculate average density by region.

    Args:
        density_df: Density dataframe
        region_mapping: Dictionary mapping region names to lists of counties

    Returns:
        DataFrame with regional density averages
    """
    regional_density = []

    for region, counties in region_mapping.items():
        # Ensure counties have " County" suffix
        counties_formatted = [
            c + " County" if not c.endswith(" County") else c
            for c in counties
        ]
        avg_density = density_df[
            density_df["County"].isin(counties_formatted)
        ]["Dispensary_PerCapita"].mean()

        regional_density.append(
            {
                "Region": region,
                "Average_Density": avg_density if not pd.isna(avg_density) else 0,
            }
        )

    return pd.DataFrame(regional_density)


@st.cache_data
def calculate_monthly_sentiment(
    sentiment_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate monthly sentiment metrics.

    Args:
        sentiment_df: Sentiment dataframe with Tweet_Date and BERT_Sentiment

    Returns:
        DataFrame with monthly aggregations
    """
    # Ensure Tweet_Date is datetime
    sentiment_df = sentiment_df.copy()

    if "Tweet_Date" not in sentiment_df.columns and "Year" in sentiment_df.columns:
        # Create Tweet_Date from Year and Month if needed
        sentiment_df["Tweet_Date"] = pd.to_datetime(
            sentiment_df["Year"].astype(str)
            + "-"
            + sentiment_df["Month"].astype(str)
            + "-01"
        )

    monthly_sentiment = (
        sentiment_df.groupby(pd.Grouper(key="Tweet_Date", freq="ME"))
        .agg({"BERT_Sentiment": ["mean", "size", lambda x: (x > 0).mean() * 100]})
        .reset_index()
    )

    # Flatten column names
    monthly_sentiment.columns = ["Date", "Sentiment", "Volume", "Positive_Ratio"]

    return monthly_sentiment


@st.cache_data
def calculate_license_type_distribution(
    dispensaries_df: pd.DataFrame
) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    Calculate license type distribution.

    Args:
        dispensaries_df: Dispensary dataframe

    Returns:
        Tuple of (distribution DataFrame, counts dictionary)
    """
    if "License Designation" in dispensaries_df.columns:
        type_counts = dispensaries_df["License Designation"].value_counts()
    elif "License Type" in dispensaries_df.columns:
        type_counts = dispensaries_df["License Type"].value_counts()
    else:
        return pd.DataFrame(), {}

    distribution_df = type_counts.reset_index()
    distribution_df.columns = ["License Type", "Count"]

    counts_dict = type_counts.to_dict()

    return distribution_df, counts_dict


@st.cache_data
def calculate_market_correlation(
    sentiment_df: pd.DataFrame,
    density_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate correlation between market density and sentiment.

    Args:
        sentiment_df: County-level sentiment data
        density_df: Density data with County, Dispensary_PerCapita, Population

    Returns:
        Merged DataFrame with both sentiment and density metrics
    """
    market_correlation = pd.merge(
        sentiment_df,
        density_df[["County", "Dispensary_PerCapita", "Population"]],
        on="County",
        how="inner",
    )

    return market_correlation


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_data_quality_metrics(data_dict: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """
    Calculate data quality metrics for all datasets.

    Args:
        data_dict: Dictionary of dataframes (dispensaries, density, sentiment)

    Returns:
        Dictionary of quality metrics
    """
    metrics = {}

    for name, df in data_dict.items():
        if df is not None and not df.empty:
            total_records = len(df)
            total_cells = df.size
            null_cells = df.isna().sum().sum()
            completeness = (1 - null_cells / total_cells) * 100 if total_cells > 0 else 0

            metrics[name] = {
                "total_records": total_records,
                "completeness": completeness,
                "null_cells": null_cells,
            }

            # Add dataset-specific metrics
            if "County" in df.columns:
                metrics[name]["unique_counties"] = df["County"].nunique()

            if "Year" in df.columns:
                years = df["Year"].dropna()
                if len(years) > 0:
                    metrics[name]["year_range"] = f"{int(years.min())}-{int(years.max())}"

    return metrics
