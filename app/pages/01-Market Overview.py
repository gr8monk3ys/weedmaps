"""
Market Overview Page

This page provides comprehensive market metrics for California's cannabis retail market,
including:
- Key performance indicators (total licenses, growth rates)
- Year-over-year growth trends
- Geographic distribution via choropleth map
- License type breakdown
- Market density categorization

Data Sources:
- Dispensaries.csv: Retailer license information
- Dispensary_Density.csv: Population-adjusted metrics
- Tweet_Sentiment.csv: Sentiment scores
- California_County_Boundaries.geojson: Geographic boundaries
"""
import pandas as pd
import streamlit as st

from utils.generate_sidebar import generate_sidebar
from utils.data_loader import load_data
from utils.filters import apply_dispensary_filters, get_filter_summary, has_active_filters
from utils.plot_helpers import create_choropleth_map, create_line_chart

# Page config
st.set_page_config(
    page_title="Market Overview | Cannabis Analytics", page_icon="📊", layout="wide"
)

# Load data
data = load_data()
dispensaries_all = data["dispensaries"]
density = data["density"]
tweet_sentiment = data["tweet_sentiment"]
ca_counties = data["ca_counties"]

# Get sidebar filters
sidebar_filters = generate_sidebar()

# Apply filters to data
dispensaries = apply_dispensary_filters(dispensaries_all, sidebar_filters)

# Check for empty filtered data
if len(dispensaries) == 0:
    st.warning("⚠️ No data matches your current filter selections. Try adjusting the filters in the sidebar.")
    st.stop()

# Title and description
st.title("📊 California Cannabis Market Overview")
st.markdown(
    """
    Comprehensive analysis of the California cannabis market, including retailer distribution,
    market growth, and key industry metrics.
"""
)

# Show active filters
if has_active_filters(sidebar_filters):
    st.info(f"📊 {get_filter_summary(sidebar_filters)}")

# Top-level metrics
st.subheader("Market Snapshot")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_dispensaries = len(dispensaries)
    st.metric("Active Retailers", f"{total_dispensaries:,}", "Licensed Dispensaries")

with col2:
    avg_density = density["Dispensary_PerCapita"].mean()
    st.metric("Average Density", f"{avg_density:.2f}", "per 100k residents")

with col3:
    total_counties = len(density["County"].unique())
    st.metric("Market Coverage", f"{total_counties}", "Counties with Retailers")

with col4:
    avg_sentiment = tweet_sentiment["BERT_Sentiment"].mean()
    st.metric("Market Sentiment", f"{avg_sentiment:.2f}", "Average Score")

# Geographic Distribution
st.subheader("Geographic Distribution")
col1, col2 = st.columns([2, 1])

with col1:
    # Choropleth map
    fig_map = create_choropleth_map(
        density,
        geojson=ca_counties,
        locations="County",
        color="Dispensary_PerCapita",
        title="Cannabis Retailer Distribution by County",
        hover_data=["Dispensary_PerCapita"],
        labels={
            "Dispensary_PerCapita": "Dispensaries per 100k residents",
            "County": "County",
        }
    )
    st.plotly_chart(fig_map, use_container_width=True)

with col2:
    # Top counties by density
    st.write("#### Top Markets by Density")
    top_counties = density.nlargest(5, "Dispensary_PerCapita")[
        ["County", "Dispensary_PerCapita"]
    ]
    formatted_counties = top_counties.copy()
    formatted_counties["Dispensary_PerCapita"] = formatted_counties[
        "Dispensary_PerCapita"
    ].apply(lambda x: f"{x:.1f} per 100k")
    formatted_counties.columns = ["County", "Density"]
    st.dataframe(formatted_counties, use_container_width=True)

# Market Growth Analysis
st.subheader("Market Growth Trends")

# Calculate growth metrics
yearly_data = (
    dispensaries.groupby("Year")
    .agg(
        {
            "License Number": "nunique",  # Count unique licenses
            "Dispensary Name": "nunique",  # Count unique dispensaries
        }
    )
    .reset_index()
)

yearly_data["Growth_Rate"] = yearly_data["Dispensary Name"].pct_change() * 100

# Display growth metrics
col1, col2 = st.columns(2)

with col1:
    st.write("#### Year-over-Year Growth")
    fig_growth = create_line_chart(
        yearly_data,
        x="Year",
        y="Growth_Rate",
        title="Market Growth Rate",
        x_label="Year",
        y_label="Growth Rate (%)"
    )
    st.plotly_chart(fig_growth, use_container_width=True)

with col2:
    # Growth metrics table
    st.write("#### Year-over-Year Growth")
    growth_df = pd.DataFrame(
        {"Year": yearly_data["Year"], "Growth Rate": yearly_data["Growth_Rate"]}
    ).round(1)
    growth_df = growth_df.dropna()  # Remove NaN values
    growth_df["Growth Rate"] = growth_df["Growth Rate"].apply(lambda x: f"{x:+.1f}%")
    st.dataframe(
        growth_df,
        use_container_width=True,
        column_config={
            "Year": st.column_config.NumberColumn(
                "Year", help="Calendar year", format="%d"
            ),
            "Growth Rate": st.column_config.TextColumn(
                "Growth Rate", help="Year-over-year growth rate", width="medium"
            ),
        },
        hide_index=True,
    )

# Market Size Analysis
st.subheader("Market Size Analysis")

# Data is already filtered by sidebar filters
filtered_data = dispensaries

# Display filtered metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Total Licenses",
        value=f"{filtered_data['License Number'].nunique():,}",
        help="Number of unique licenses in selected range",
        label_visibility="visible",
    )

with col2:
    st.metric(
        label="Total Dispensaries",
        value=f"{filtered_data['Dispensary Name'].nunique():,}",
        help="Number of unique dispensaries in selected range",
        label_visibility="visible",
    )

with col3:
    st.metric(
        label="Counties Served",
        value=f"{filtered_data['County'].nunique():,}",
        help="Number of counties with active dispensaries",
        label_visibility="visible",
    )

# Regional Distribution
st.subheader("Regional Distribution")

# Calculate regional metrics
regional_data = (
    filtered_data.groupby("County")
    .agg({"License Number": "nunique", "Dispensary Name": "nunique"})
    .reset_index()
)

col1, col2 = st.columns(2)

with col1:
    # Distribution by licenses
    st.write("#### Distribution by Licenses")
    fig_dist_lic = px.pie(
        regional_data,
        values="License Number",
        names="County",
        title="Regional Distribution (by Licenses)",
        template="plotly_dark",
        color_discrete_sequence=px.colors.sequential.Greens,
    )
    st.plotly_chart(fig_dist_lic, use_container_width=True)

with col2:
    # Distribution by dispensaries
    st.write("#### Distribution by Dispensaries")
    fig_dist_disp = px.pie(
        regional_data,
        values="Dispensary Name",
        names="County",
        title="Regional Distribution (by Dispensaries)",
        template="plotly_dark",
        color_discrete_sequence=px.colors.sequential.Greens,
    )
    st.plotly_chart(fig_dist_disp, use_container_width=True)

# Regional Analysis
st.subheader("Regional Market Analysis")

# Create regional summary
region_summary = density.copy()
region_summary["Density_Category"] = pd.qcut(
    region_summary["Dispensary_PerCapita"],
    q=4,
    labels=["Low", "Medium-Low", "Medium-High", "High"],
)

col1, col2 = st.columns(2)

with col1:
    # Regional distribution pie chart
    region_dist = region_summary["Density_Category"].value_counts()
    fig_region = px.pie(
        values=region_dist.values,
        names=region_dist.index,
        title="Distribution of Market Density Categories",
        template="plotly_dark",
    )
    fig_region.update_traces(marker=dict(colors=px.colors.sequential.Greens))
    st.plotly_chart(fig_region, use_container_width=True)

with col2:
    # Regional statistics
    st.write("#### Market Density Statistics")
    region_stats = (
        region_summary.groupby("Density_Category")
        .agg({"Dispensary_PerCapita": ["mean", "count"]})
        .round(2)
    )
    region_stats.columns = ["Average Density", "Number of Counties"]
    region_stats = region_stats.reset_index()
    st.dataframe(region_stats, use_container_width=True)

# Key Insights
st.subheader("Key Market Insights")

# Calculate dynamic insights
# 1. Market concentration - top 5 counties market share
top_5_dispensaries = dispensaries.groupby("County")["Dispensary Name"].nunique().nlargest(5).sum()
total_dispensaries_by_county = dispensaries.groupby("County")["Dispensary Name"].nunique().sum()
top_5_share = (top_5_dispensaries / total_dispensaries_by_county * 100) if total_dispensaries_by_county > 0 else 0

# 2. Growth trajectory - calculate recent growth rate
if len(yearly_data) >= 2:
    recent_growth = yearly_data["Growth_Rate"].iloc[-1]
    avg_growth = yearly_data["Growth_Rate"].mean()
    growth_trend = "accelerating" if recent_growth > avg_growth else "stable" if abs(recent_growth - avg_growth) < 5 else "slowing"
else:
    recent_growth = 0
    growth_trend = "insufficient data"

# 3. Market opportunities - high population, low density counties
if len(density) > 0:
    density_with_opportunity = density.copy()
    density_with_opportunity["Opportunity_Score"] = (
        density_with_opportunity["Population"] / (density_with_opportunity["Dispensary_PerCapita"] + 1)
    )
    top_opportunity = density_with_opportunity.nlargest(1, "Opportunity_Score").iloc[0]
    opportunity_county = top_opportunity["County"]
    opportunity_pop = top_opportunity["Population"]
else:
    opportunity_county = "N/A"
    opportunity_pop = 0

# Three column layout for insights
insight_col1, insight_col2, insight_col3 = st.columns(3)

with insight_col1:
    st.info(
        f"""
        **Market Concentration**

        Top 5 counties account for **{top_5_share:.1f}%** of all dispensaries,
        showing {'high' if top_5_share > 60 else 'moderate'} market concentration
        in urban areas.
        """
    )

with insight_col2:
    if growth_trend != "insufficient data":
        st.success(
            f"""
            **Growth Trajectory**

            Market growth is **{growth_trend}** with recent rate of
            **{recent_growth:+.1f}%**, compared to average of **{avg_growth:.1f}%**.
            """
        )
    else:
        st.success(
            """
            **Growth Trajectory**

            Insufficient historical data for growth trend analysis.
            More years needed for comprehensive trend assessment.
            """
        )

with insight_col3:
    st.warning(
        f"""
        **Market Opportunities**

        **{opportunity_county}** shows high expansion potential with
        **{opportunity_pop:,.0f}** residents and relatively low market density.
        """
    )

# Footer
st.markdown("---")
st.caption("Data last updated: Daily refresh from California Cannabis Authority")
