"""
Data Quality Dashboard

This page provides comprehensive data quality metrics and validation insights
for all datasets used in the Cannabis Analytics Dashboard.

Features:
- Dataset completeness metrics
- Null value analysis
- Data coverage statistics
- Year range and temporal coverage
- County coverage validation
- Data freshness indicators

Data Sources:
- Dispensaries.csv: Retailer license information
- Dispensary_Density.csv: Population-adjusted metrics
- Tweet_Sentiment.csv: Sentiment scores
- California_County_Boundaries.geojson: Geographic boundaries
"""
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from utils.generate_sidebar import generate_sidebar
from utils.data_loader import load_data
from utils.cached_calculations import get_data_quality_metrics
from utils.plot_helpers import create_bar_chart
from utils.data_validation import validate_all_datasets

# Page config
st.set_page_config(
    page_title="Data Quality | Cannabis Analytics", page_icon="🔍", layout="wide"
)

# Load data
data = load_data()
dispensaries = data["dispensaries"]
density = data["density"]
tweet_sentiment = data["tweet_sentiment"]

# Get sidebar filters (for consistency, even if not used for filtering)
sidebar_filters = generate_sidebar()

# Title and description
st.title("🔍 Data Quality Dashboard")
st.markdown(
    """
    Monitor the quality, completeness, and coverage of all datasets used in the
    Cannabis Analytics Dashboard. This page provides transparency into data
    quality metrics and helps identify potential data issues.
"""
)

# Calculate data quality metrics
data_dict = {
    "Dispensaries": dispensaries,
    "Density": density,
    "Tweet Sentiment": tweet_sentiment
}

quality_metrics = get_data_quality_metrics(data_dict)

# Overall Data Quality Summary
st.subheader("📊 Overall Data Quality Summary")

# Create summary metrics in columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_records = sum(m["total_records"] for m in quality_metrics.values())
    st.metric("Total Records", f"{total_records:,}", "Across all datasets")

with col2:
    avg_completeness = sum(m["completeness"] for m in quality_metrics.values()) / len(quality_metrics)
    st.metric("Average Completeness", f"{avg_completeness:.1f}%", "Data filled")

with col3:
    total_null_cells = sum(m["null_cells"] for m in quality_metrics.values())
    st.metric("Total Null Cells", f"{total_null_cells:,}", "Missing values")

with col4:
    num_datasets = len(quality_metrics)
    st.metric("Datasets Monitored", f"{num_datasets}", "Active datasets")

# Data Validation
st.subheader("🔬 Data Validation Results")

# Run validations
validation_results = validate_all_datasets(data_dict)

# Count total validations and failures
total_validations = sum(len(results) for _, results in validation_results.values())
total_failures = sum(
    sum(1 for result in results if not result.is_valid)
    for _, results in validation_results.values()
)

# Display validation summary
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Validations", f"{total_validations}", "Checks performed")

with col2:
    st.metric("Passed", f"{total_validations - total_failures}", "✓ Valid")

with col3:
    if total_failures > 0:
        st.metric("Failed", f"{total_failures}", "✗ Issues found", delta_color="inverse")
    else:
        st.metric("Failed", "0", "✓ All passed")

# Display validation details in expandable sections
for dataset_name, (is_valid, results) in validation_results.items():
    status_icon = "✅" if is_valid else "⚠️"
    status_text = "All validations passed" if is_valid else f"{sum(1 for r in results if not r.is_valid)} validation(s) failed"

    with st.expander(f"{status_icon} {dataset_name.title()} Dataset - {status_text}", expanded=not is_valid):
        if not results:
            st.info("No validations configured for this dataset.")
            continue

        # Display results in a table
        results_data = []
        for result in results:
            results_data.append({
                "Column": result.column,
                "Status": "✓ Pass" if result.is_valid else "✗ Fail",
                "Message": result.message,
                "Invalid Count": result.invalid_count if not result.is_valid else "-"
            })

        results_df = pd.DataFrame(results_data)

        # Display with color coding
        def color_status(val):
            if "✓ Pass" in str(val):
                return "background-color: #1B5E20; color: white"
            elif "✗ Fail" in str(val):
                return "background-color: #B71C1C; color: white"
            return ""

        styled_results = results_df.style.map(color_status, subset=["Status"])

        st.dataframe(
            styled_results,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Column": st.column_config.TextColumn("Column", width="medium"),
                "Status": st.column_config.TextColumn("Status", width="small"),
                "Message": st.column_config.TextColumn("Validation Details", width="large"),
                "Invalid Count": st.column_config.TextColumn("Invalid Count", width="small")
            }
        )

        # Show invalid value samples if any failures
        failed_validations = [r for r in results if not r.is_valid and r.invalid_values]
        if failed_validations:
            st.write("**Sample Invalid Values:**")
            for result in failed_validations:
                if result.invalid_values:
                    st.code(f"{result.column}: {result.invalid_values}")

# Dataset-Specific Metrics
st.subheader("📋 Dataset-Specific Metrics")

# Create tabs for each dataset
tabs = st.tabs(list(quality_metrics.keys()))

for tab, (dataset_name, metrics) in zip(tabs, quality_metrics.items()):
    with tab:
        # Dataset overview
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Records", f"{metrics['total_records']:,}")

        with col2:
            st.metric("Completeness", f"{metrics['completeness']:.2f}%")

        with col3:
            st.metric("Null Cells", f"{metrics['null_cells']:,}")

        # Additional dataset-specific metrics
        if "unique_counties" in metrics:
            st.write(f"**Counties Covered:** {metrics['unique_counties']}")

        if "year_range" in metrics:
            st.write(f"**Year Range:** {metrics['year_range']}")

        # Show sample data
        st.write("#### Sample Data Preview")
        dataset_df = data_dict[dataset_name]
        st.dataframe(dataset_df.head(10), use_container_width=True)

# Completeness Comparison
st.subheader("📈 Completeness Comparison")

# Create bar chart comparing completeness across datasets
completeness_data = pd.DataFrame([
    {"Dataset": name, "Completeness": metrics["completeness"]}
    for name, metrics in quality_metrics.items()
])

fig_completeness = create_bar_chart(
    completeness_data,
    x="Dataset",
    y="Completeness",
    title="Data Completeness by Dataset",
    y_label="Completeness (%)"
)
fig_completeness.update_yaxes(range=[0, 100])
st.plotly_chart(fig_completeness, use_container_width=True)

# Null Value Analysis
st.subheader("🔍 Null Value Analysis")

col1, col2 = st.columns(2)

with col1:
    # Null values by dataset
    null_data = pd.DataFrame([
        {"Dataset": name, "Null Cells": metrics["null_cells"]}
        for name, metrics in quality_metrics.items()
    ])

    fig_nulls = create_bar_chart(
        null_data,
        x="Dataset",
        y="Null Cells",
        title="Null Values by Dataset",
        y_label="Number of Null Cells"
    )
    st.plotly_chart(fig_nulls, use_container_width=True)

with col2:
    # Null percentage breakdown
    null_pct_data = pd.DataFrame([
        {
            "Dataset": name,
            "Null Percentage": 100 - metrics["completeness"]
        }
        for name, metrics in quality_metrics.items()
    ])

    fig_null_pct = px.pie(
        null_pct_data,
        values="Null Percentage",
        names="Dataset",
        title="Null Value Distribution",
        template="plotly_dark",
        color_discrete_sequence=px.colors.sequential.Reds_r
    )
    st.plotly_chart(fig_null_pct, use_container_width=True)

# Column-Level Quality Analysis
st.subheader("🔬 Column-Level Quality Analysis")

# Create tabs for each dataset
dataset_tabs = st.tabs(list(data_dict.keys()))

for tab, (dataset_name, dataset_df) in zip(dataset_tabs, data_dict.items()):
    with tab:
        # Calculate column-level null counts
        null_counts = dataset_df.isnull().sum().sort_values(ascending=False)
        null_percentages = (null_counts / len(dataset_df) * 100).round(2)

        # Create dataframe for display
        column_quality = pd.DataFrame({
            "Column": null_counts.index,
            "Null Count": null_counts.values,
            "Null %": null_percentages.values,
            "Non-Null Count": len(dataset_df) - null_counts.values,
            "Completeness %": (100 - null_percentages.values).round(2)
        })

        # Display table with conditional formatting
        st.dataframe(
            column_quality,
            use_container_width=True,
            column_config={
                "Null Count": st.column_config.NumberColumn(
                    "Null Count",
                    help="Number of null values in this column",
                    format="%d"
                ),
                "Null %": st.column_config.NumberColumn(
                    "Null %",
                    help="Percentage of null values",
                    format="%.2f%%"
                ),
                "Completeness %": st.column_config.NumberColumn(
                    "Completeness %",
                    help="Percentage of non-null values",
                    format="%.2f%%"
                )
            },
            hide_index=True
        )

        # Visualization of column completeness
        fig_col_completeness = create_bar_chart(
            column_quality.head(10),
            x="Column",
            y="Completeness %",
            title=f"Top 10 Columns by Completeness - {dataset_name}",
            y_label="Completeness (%)"
        )
        fig_col_completeness.update_yaxes(range=[0, 100])
        st.plotly_chart(fig_col_completeness, use_container_width=True)

# County Coverage Analysis
st.subheader("🗺️ County Coverage Analysis")

col1, col2 = st.columns(2)

with col1:
    # Counties in each dataset
    st.write("#### Counties per Dataset")

    county_coverage = []
    for name, df in data_dict.items():
        if "County" in df.columns:
            unique_counties = df["County"].nunique()
            county_coverage.append({
                "Dataset": name,
                "Unique Counties": unique_counties
            })

    if county_coverage:
        county_df = pd.DataFrame(county_coverage)
        st.dataframe(county_df, use_container_width=True, hide_index=True)

with col2:
    # Year coverage
    st.write("#### Temporal Coverage")

    year_coverage = []
    for name, df in data_dict.items():
        if "Year" in df.columns:
            years = df["Year"].dropna()
            if len(years) > 0:
                year_coverage.append({
                    "Dataset": name,
                    "Min Year": int(years.min()),
                    "Max Year": int(years.max()),
                    "Years Span": int(years.max() - years.min() + 1)
                })

    if year_coverage:
        year_df = pd.DataFrame(year_coverage)
        st.dataframe(year_df, use_container_width=True, hide_index=True)

# Data Quality Insights
st.subheader("💡 Data Quality Insights")

# Calculate insights
insights = []

# Completeness insights
avg_completeness = sum(m["completeness"] for m in quality_metrics.values()) / len(quality_metrics)
if avg_completeness >= 95:
    insights.append(("✅", "Excellent Data Quality", f"Overall data completeness is {avg_completeness:.1f}%, indicating high-quality datasets."))
elif avg_completeness >= 85:
    insights.append(("⚠️", "Good Data Quality", f"Overall data completeness is {avg_completeness:.1f}%. Some minor data gaps exist but quality is generally good."))
else:
    insights.append(("❌", "Data Quality Issues", f"Overall data completeness is {avg_completeness:.1f}%. Significant data gaps may affect analysis accuracy."))

# County coverage insights
county_counts = [m.get("unique_counties", 0) for m in quality_metrics.values() if "unique_counties" in m]
if county_counts:
    min_counties = min(county_counts)
    max_counties = max(county_counts)
    if min_counties == max_counties:
        insights.append(("✅", "Consistent County Coverage", f"All datasets cover {min_counties} counties consistently."))
    else:
        insights.append(("⚠️", "Variable County Coverage", f"County coverage varies from {min_counties} to {max_counties} across datasets."))

# Display insights in columns
insight_cols = st.columns(len(insights))
for col, (icon, title, description) in zip(insight_cols, insights):
    with col:
        st.info(f"{icon} **{title}**\n\n{description}")

# Data Freshness
st.subheader("🕐 Data Freshness")

st.markdown("""
**Data Update Frequency:**
- Dispensaries data: Updated monthly from California Cannabis Authority
- Density calculations: Recalculated monthly based on census data
- Tweet sentiment: Real-time collection with daily aggregation

**Last Data Refresh:** {data refresh placeholder - would be populated from actual metadata}
""")

# Data Quality Recommendations
st.subheader("📝 Recommendations")

recommendations = []

# Check for datasets with low completeness
for name, metrics in quality_metrics.items():
    if metrics["completeness"] < 90:
        recommendations.append(
            f"**{name} Dataset:** Consider investigating and addressing the {100 - metrics['completeness']:.1f}% "
            f"of missing values ({metrics['null_cells']:,} null cells)."
        )

# Check for datasets with fewer records
min_records = min(m["total_records"] for m in quality_metrics.values())
max_records = max(m["total_records"] for m in quality_metrics.values())
if max_records > min_records * 10:
    recommendations.append(
        "**Record Count Imbalance:** Consider whether the significant difference in record counts "
        "across datasets might indicate missing data or collection issues."
    )

if recommendations:
    for rec in recommendations:
        st.warning(rec)
else:
    st.success("✅ No major data quality issues detected. All datasets meet quality standards.")

# Footer
st.markdown("---")
st.caption("Data Quality Dashboard | Updated in real-time based on loaded datasets")
