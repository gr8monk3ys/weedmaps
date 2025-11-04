"""
Geographic Analysis Page

This page provides detailed geographic analysis of cannabis market distribution across
California counties, including:
- Interactive choropleth maps showing retailer density
- County-level density rankings
- Regional market comparisons (Northern, Bay Area, Central, Southern)
- Market opportunity analysis combining density and sentiment
- Population-adjusted metrics

Data Sources:
- Dispensary_Density.csv: Population and density metrics
- Tweet_Sentiment.csv: County-level sentiment
- California_County_Boundaries.geojson: County boundaries for mapping

Regional Definitions:
Uses centralized region mappings from config.regions to group California's 58 counties
into meaningful market regions for analysis.
"""
import pandas as pd
import streamlit as st

from utils.generate_sidebar import generate_sidebar
from utils.data_loader import load_data
from utils.filters import apply_dispensary_filters, apply_density_filters, apply_sentiment_filters, get_filter_summary, has_active_filters
from utils.data_utils import normalize_county_name
from utils.plot_helpers import create_choropleth_map, create_bar_chart, create_histogram, create_scatter_plot
from config.regions import SIMPLE_REGIONS, CALIFORNIA_REGIONS

# Page config
st.set_page_config(
    page_title="Geographic Analysis | Cannabis Analytics", page_icon="🗺️", layout="wide"
)

# Load data
data = load_data()
dispensaries_all = data["dispensaries"]
density_all = data["density"]
tweet_sentiment_all = data["tweet_sentiment"]
counties = data["ca_counties"]

# Get sidebar filters
sidebar_filters = generate_sidebar()

# Apply filters to data
dispensaries = apply_dispensary_filters(dispensaries_all, sidebar_filters)
density = apply_density_filters(density_all, sidebar_filters)
tweet_sentiment = apply_sentiment_filters(tweet_sentiment_all, sidebar_filters)

# Check for empty filtered data
if len(density) == 0:
    st.warning("⚠️ No data matches your current filter selections. Try adjusting the filters in the sidebar.")
    st.stop()

# Title and description
st.title("🗺️ Geographic Market Analysis")
st.markdown(
    """
    Detailed analysis of cannabis market distribution across California counties,
    including population-adjusted metrics and regional patterns.
"""
)

# Show active filters
if has_active_filters(sidebar_filters):
    st.info(f"📊 {get_filter_summary(sidebar_filters)}")

# Normalize county names using centralized utility
density["County"] = density["County"].apply(normalize_county_name)

# Geographic Overview
st.subheader("Geographic Distribution Overview")

# Create choropleth map
fig_map = create_choropleth_map(
    density,
    geojson=counties,
    locations="County",
    color="Dispensary_PerCapita",
    title="Cannabis Retailer Density by County",
    hover_data=["County"],
    labels={"Dispensary_PerCapita": "Retailers per 100k Residents", "County": "County"}
)

# Display map
st.plotly_chart(fig_map, use_container_width=True)

# County Analysis
st.subheader("County-Level Analysis")

# Two column layout for analysis
col1, col2 = st.columns(2)

with col1:
    # Top counties table
    st.write("#### Top Counties by Market Density")
    top_counties = density.nlargest(10, "Dispensary_PerCapita")[
        ["County", "Dispensary_PerCapita"]
    ]
    formatted_counties = top_counties.copy()
    formatted_counties["Dispensary_PerCapita"] = formatted_counties[
        "Dispensary_PerCapita"
    ].apply(lambda x: f"{x:.2f} per 100k")
    formatted_counties.columns = ["County", "Density"]
    st.dataframe(formatted_counties, use_container_width=True)

with col2:
    # Distribution histogram
    st.write("#### Distribution of Market Density")
    fig_dist = create_histogram(
        density,
        x="Dispensary_PerCapita",
        title="Distribution of Retailer Density",
        x_label="Retailers per 100k Residents"
    )
    st.plotly_chart(fig_dist, use_container_width=True)

# Calculate county-level density
density["Dispensary_PerCapita"] = density["Dispensary_PerCapita"].astype(float)

# Display density metrics
st.subheader("Cannabis Retailer Density")

col1, col2 = st.columns(2)

with col1:
    # County-level density
    st.write("#### Retailer Density by County")
    top_counties = density.nlargest(10, "Dispensary_PerCapita")
    fig_density = create_bar_chart(
        top_counties,
        x="County",
        y="Dispensary_PerCapita",
        title="Top 10 Counties by Retailer Density",
        x_label="County",
        y_label="Retailers per 100k Residents"
    )
    fig_density.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_density, use_container_width=True)

with col2:
    # Regional density
    st.write("#### Average Market Density by Region")

    # Use centralized region definitions from config
    # Calculate regional averages
    regional_density = []
    for region, counties in SIMPLE_REGIONS.items():
        counties = [c + " County" if not c.endswith(" County") else c for c in counties]
        avg_density = density[density["County"].isin(counties)][
            "Dispensary_PerCapita"
        ].mean()
        regional_density.append(
            {
                "Region": region,
                "Average_Density": avg_density if not pd.isna(avg_density) else 0,
            }
        )

    regional_df = pd.DataFrame(regional_density)

    fig_regional = create_bar_chart(
        regional_df,
        x="Region",
        y="Average_Density",
        title="Average Retailer Density by Region",
        x_label="Region",
        y_label="Average Retailers per 100k Residents",
        color_discrete_sequence=["#81C784"]
    )
    st.plotly_chart(fig_regional, use_container_width=True)

# Regional Patterns
st.subheader("Regional Market Patterns")

# Use centralized detailed region definitions from config
# Calculate regional metrics
region_metrics = []
for region, counties in CALIFORNIA_REGIONS.items():
    region_data = density[density["County"].isin(counties)]
    region_metrics.append(
        {
            "Region": region,
            "Average Density": region_data["Dispensary_PerCapita"].mean(),
            "Total Counties": len(region_data),
            "Total Retailers": len(region_data)
            * region_data["Dispensary_PerCapita"].mean(),
        }
    )

region_df = pd.DataFrame(region_metrics)

# Display regional comparison
col1, col2 = st.columns(2)

with col1:
    # Regional metrics table
    st.write("#### Regional Market Comparison")
    formatted_region_df = region_df.copy()
    formatted_region_df["Average Density"] = formatted_region_df[
        "Average Density"
    ].round(2)
    formatted_region_df["Total Retailers"] = formatted_region_df[
        "Total Retailers"
    ].round(0)
    st.dataframe(formatted_region_df, use_container_width=True)

with col2:
    # Regional density comparison
    fig_region = create_bar_chart(
        region_df,
        x="Region",
        y="Average Density",
        title="Average Market Density by Region",
        color="Average Density",
        color_continuous_scale="Greens"
    )
    st.plotly_chart(fig_region, use_container_width=True)

# Market Opportunity Analysis
st.subheader("Market Opportunity Analysis")

# Calculate opportunity scores
opportunity_counties = density.copy()
opportunity_counties["Sentiment"] = (
    tweet_sentiment.groupby("County")["BERT_Sentiment"]
    .mean()
    .reset_index(name="Sentiment")["Sentiment"]
)
opportunity_counties["Density_Score"] = 1 - (
    opportunity_counties["Dispensary_PerCapita"]
    / opportunity_counties["Dispensary_PerCapita"].max()
)
opportunity_counties["Sentiment_Score"] = opportunity_counties["Sentiment"].fillna(
    0
)  # Fill NA values with neutral sentiment
opportunity_counties["Market_Score"] = (
    opportunity_counties["Density_Score"] * 0.7
    + opportunity_counties["Sentiment_Score"] * 0.3
).round(2)

col1, col2 = st.columns(2)

with col1:
    # Top opportunity markets
    st.write("#### Top Market Opportunities")
    st.dataframe(
        opportunity_counties.nlargest(5, "Market_Score")[
            ["County", "Dispensary_PerCapita", "Market_Score"]
        ].round(2),
        use_container_width=True,
    )

with col2:
    # Opportunity visualization
    st.write("#### Market Opportunity Matrix")
    fig_opportunity = create_scatter_plot(
        opportunity_counties,
        x="Dispensary_PerCapita",
        y="Sentiment_Score",
        title="Market Opportunity Matrix",
        x_label="Retailers per 100k Residents",
        y_label="Sentiment Score",
        size="Population",
        color="Market_Score",
        hover_data=["County"],
        color_continuous_scale="Greens"
    )

    st.plotly_chart(fig_opportunity, use_container_width=True)

# Key Insights
st.subheader("Key Geographic Insights")

# Calculate dynamic insights
# 1. Market distribution - urban vs rural density spread
if len(density) > 0:
    highest_density = density["Dispensary_PerCapita"].max()
    lowest_density = density["Dispensary_PerCapita"].min()
    density_ratio = highest_density / lowest_density if lowest_density > 0 else 0
    highest_county = density.nlargest(1, "Dispensary_PerCapita").iloc[0]["County"]
else:
    density_ratio = 0
    highest_county = "N/A"

# 2. Growth opportunities - high population, low density
if len(density) > 5:
    # Calculate opportunity score: high population + low density
    opportunity_analysis = density.copy()
    opportunity_analysis["Opportunity_Score"] = (
        opportunity_analysis["Population"] /
        (opportunity_analysis["Dispensary_PerCapita"] + 0.1)
    )
    top_opportunity_county = opportunity_analysis.nlargest(1, "Opportunity_Score").iloc[0]
    opportunity_name = top_opportunity_county["County"]
    opportunity_pop = top_opportunity_county["Population"]
    opportunity_density = top_opportunity_county["Dispensary_PerCapita"]
else:
    opportunity_name = "N/A"
    opportunity_pop = 0
    opportunity_density = 0

# 3. Regional dynamics - variation across regions
if len(regional_df) > 1 and "Average Density" in regional_df.columns:
    regional_variation = regional_df["Average Density"].std()
    highest_region = regional_df.nlargest(1, "Average Density").iloc[0]["Region"]
    lowest_region = regional_df.nsmallest(1, "Average Density").iloc[0]["Region"]
    variation_level = "high" if regional_variation > 5 else "moderate" if regional_variation > 2 else "low"
else:
    highest_region = "N/A"
    lowest_region = "N/A"
    variation_level = "unknown"

# Three column layout for insights
insight_col1, insight_col2, insight_col3 = st.columns(3)

with insight_col1:
    st.info(
        f"""
        **Market Distribution**

        **{highest_county}** has the highest density, showing
        **{density_ratio:.1f}x** more retailers per capita than the lowest,
        indicating significant urban-rural divide.
        """
    )

with insight_col2:
    st.success(
        f"""
        **Growth Opportunities**

        **{opportunity_name}** offers strong expansion potential with
        **{opportunity_pop:,.0f}** residents but only **{opportunity_density:.1f}**
        retailers per 100k.
        """
    )

with insight_col3:
    st.warning(
        f"""
        **Regional Dynamics**

        **{variation_level.capitalize()}** variation across regions,
        with **{highest_region}** leading and **{lowest_region}** trailing,
        requiring tailored strategies.
        """
    )

# Footer
st.markdown("---")
st.caption("Data last updated: Daily refresh from California Cannabis Authority")
