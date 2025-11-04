"""
Social Insights Page

This page analyzes social media sentiment towards cannabis across California,
providing insights into public perception and temporal trends:
- Overall sentiment distribution and statistics
- Temporal sentiment trends (sentiment over time)
- Geographic sentiment distribution by county
- Correlation between market density and sentiment
- Sentiment volatility analysis

Data Sources:
- Tweet_Sentiment.csv: Social media posts with BERT sentiment scores
- Dispensary_Density.csv: For correlation analysis with market metrics

Sentiment Processing:
Sentiment scores are pre-processed using convert_sentiment_score() which normalizes
various formats (star ratings, numeric scores) to a -1.0 to 1.0 scale where:
- 1.0 = Very positive
- 0.0 = Neutral
- -1.0 = Very negative
"""
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.generate_sidebar import generate_sidebar
from utils.data_loader import load_data
from utils.filters import apply_sentiment_filters, apply_density_filters, get_filter_summary, has_active_filters
from utils.data_utils import add_county_suffix
from utils.plot_helpers import create_bar_chart, create_scatter_plot
from utils.error_messages import (
    show_no_data_error,
    show_temporal_analysis_error,
    show_correlation_warning
)

# Page config
st.set_page_config(
    page_title="Cannabis Analytics | Social Insights", page_icon="💭", layout="wide"
)

# Load data
data = load_data()
tweet_sentiment_all = data["tweet_sentiment"]
density_all = data["density"]

# Get sidebar filters
sidebar_filters = generate_sidebar()

# Apply filters to data
tweet_sentiment = apply_sentiment_filters(tweet_sentiment_all, sidebar_filters)
density = apply_density_filters(density_all, sidebar_filters)

# Check for empty filtered data
if len(tweet_sentiment) == 0:
    filter_summary = get_filter_summary(sidebar_filters) if has_active_filters(sidebar_filters) else None
    show_no_data_error(filter_info=filter_summary, page_name="Social Insights")
    st.stop()

# Title and description
st.title("💭 Social Media Insights")
st.markdown(
    """
    Analysis of social media sentiment towards cannabis across California,
    including temporal trends and geographic distribution.
    """
)

# Show active filters
if has_active_filters(sidebar_filters):
    st.info(f"📊 {get_filter_summary(sidebar_filters)}")

# Overall Sentiment Metrics
st.subheader("Sentiment Overview")

# Convert sentiment to numeric and handle any non-numeric values
tweet_sentiment["BERT_Sentiment"] = pd.to_numeric(
    tweet_sentiment["BERT_Sentiment"], errors="coerce"
)

# Calculate key metrics
avg_sentiment = tweet_sentiment["BERT_Sentiment"].mean()
positive_ratio = (tweet_sentiment["BERT_Sentiment"] > 0).mean() * 100
tweet_count = len(tweet_sentiment)

# Display metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Average Sentiment",
        f"{avg_sentiment:.2f}",
        "Scale: -1 to 1",
        help="Average sentiment score across all tweets",
    )

with col2:
    st.metric(
        "Positive Sentiment",
        f"{positive_ratio:.1f}%",
        "of total tweets",
        help="Percentage of tweets with positive sentiment",
    )

with col3:
    st.metric(
        "Total Tweets",
        f"{tweet_count:,}",
        "analyzed",
        help="Total number of tweets analyzed",
    )

# Temporal Analysis
st.subheader("Temporal Sentiment Analysis")

# Ensure Tweet_Date is datetime and create a proper date column
tweet_sentiment["Tweet_Date"] = pd.to_datetime(
    tweet_sentiment["Year"].astype(str)
    + "-"
    + tweet_sentiment["Month"].astype(str)
    + "-01"
)

# Calculate temporal metrics with error handling
try:
    # Calculate monthly metrics using 'ME' (month end)
    monthly_sentiment = (
        tweet_sentiment.groupby(pd.Grouper(key="Tweet_Date", freq="ME"))
        .agg({"BERT_Sentiment": ["mean", "size", lambda x: (x > 0).mean() * 100]})
        .reset_index()
    )

    # Flatten column names
    monthly_sentiment.columns = ["Date", "Sentiment", "Volume", "Positive_Ratio"]

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add sentiment line
    fig.add_trace(
        go.Scatter(
            x=monthly_sentiment["Date"],
            y=monthly_sentiment["Sentiment"],
            name="Sentiment",
            line=dict(color="#4CAF50", width=2),
        ),
        secondary_y=False,
    )

    # Add volume bars
    fig.add_trace(
        go.Bar(
            x=monthly_sentiment["Date"],
            y=monthly_sentiment["Volume"],
            name="Volume",
            marker_color="rgba(129, 199, 132, 0.3)",
        ),
        secondary_y=True,
    )

    # Update layout
    fig.update_layout(
        template="plotly_dark",
        title_text="Sentiment and Volume Trends",
        showlegend=True,
    )

    # Update axes titles
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Sentiment Score", secondary_y=False)
    fig.update_yaxes(title_text="Tweet Volume", secondary_y=True)

    # Display plot
    st.plotly_chart(fig, use_container_width=True)

    # Show trend statistics (only if there are at least 2 months of data)
    if len(monthly_sentiment) >= 2:
        st.write("#### Trend Statistics")
        col1, col2, col3 = st.columns(3)

        with col1:
            recent_sentiment = monthly_sentiment.iloc[-1]["Sentiment"]
            sentiment_change = recent_sentiment - monthly_sentiment.iloc[-2]["Sentiment"]
            st.metric(
                "Recent Sentiment",
                f"{recent_sentiment:.2f}",
                f"{sentiment_change:+.2f}",
                help="Most recent month's average sentiment",
            )

        with col2:
            recent_volume = monthly_sentiment.iloc[-1]["Volume"]
            volume_change = recent_volume - monthly_sentiment.iloc[-2]["Volume"]
            # Handle division by zero for volume change percentage
            prev_volume = monthly_sentiment.iloc[-2]["Volume"]
            if prev_volume > 0:
                volume_change_pct = (volume_change / prev_volume) * 100
                delta_str = f"{volume_change_pct:+.1f}%"
            else:
                delta_str = "N/A"
            st.metric(
                "Recent Volume",
                f"{int(recent_volume):,}",
                delta_str,
                help="Most recent month's tweet volume",
            )

        with col3:
            recent_positive = monthly_sentiment.iloc[-1]["Positive_Ratio"]
            positive_change = recent_positive - monthly_sentiment.iloc[-2]["Positive_Ratio"]
            st.metric(
                "Positive Ratio",
                f"{recent_positive:.1f}%",
                f"{positive_change:+.1f}%",
                help="Percentage of positive tweets in the most recent month",
            )
    elif len(monthly_sentiment) == 1:
        # Show current metrics without comparison if only 1 month of data
        st.write("#### Current Month Statistics")
        st.info("💡 Trend comparison requires at least 2 months of data. Showing current month only.")
        col1, col2, col3 = st.columns(3)

        with col1:
            recent_sentiment = monthly_sentiment.iloc[-1]["Sentiment"]
            st.metric(
                "Recent Sentiment",
                f"{recent_sentiment:.2f}",
                help="Current month's average sentiment",
            )

        with col2:
            recent_volume = monthly_sentiment.iloc[-1]["Volume"]
            st.metric(
                "Recent Volume",
                f"{int(recent_volume):,}",
                help="Current month's tweet volume",
            )

        with col3:
            recent_positive = monthly_sentiment.iloc[-1]["Positive_Ratio"]
            st.metric(
                "Positive Ratio",
                f"{recent_positive:.1f}%",
                help="Percentage of positive tweets in current month",
            )
    else:
        st.warning("⚠️ Insufficient data for trend statistics. Need at least 1 month of data.")

except Exception as e:
    show_temporal_analysis_error(e)

# Geographic Sentiment Analysis
st.subheader("Geographic Sentiment Distribution")

# Standardize county names using centralized utility
tweet_sentiment["County"] = tweet_sentiment["County"].apply(add_county_suffix)

# Calculate county-level sentiment
county_sentiment = (
    tweet_sentiment.groupby("County")
    .agg({"BERT_Sentiment": ["mean", "count", lambda x: (x > 0).mean() * 100]})
    .reset_index()
)

county_sentiment.columns = [
    "County",
    "Average Sentiment",
    "Tweet Count",
    "Positive Ratio",
]
county_sentiment = county_sentiment.round(2)

# Sort by tweet count to show most active counties
top_counties = county_sentiment.nlargest(10, "Tweet Count")

# Create bar chart
fig_counties = create_bar_chart(
    top_counties,
    x="County",
    y="Average Sentiment",
    title="Top Counties by Tweet Volume",
    x_label="County",
    y_label="Average Sentiment",
    color="Positive Ratio",
    color_continuous_scale="Greens",
    hover_data=["Tweet Count"]
)

fig_counties.update_layout(xaxis_tickangle=-45)

st.plotly_chart(fig_counties, use_container_width=True)

# Detailed County Analysis
st.subheader("County-Level Analysis")


# Create color scale for sentiment
def style_sentiment(value):
    """Create a color scale for sentiment values"""
    if pd.isna(value):
        return "background-color: #2E2E2E"
    normalized = (value + 1) / 2  # Convert from [-1,1] to [0,1]
    return f"background-color: rgba(76, 175, 80, {normalized:.2f})"


# Sort counties by tweet count
sorted_counties = county_sentiment.sort_values("Tweet Count", ascending=False)

# Apply styling to the dataframe
styled_counties = sorted_counties.style.format(
    {
        "Average Sentiment": "{:.2f}",
        "Tweet Count": "{:,.0f}",
        "Positive Ratio": "{:.1f}%",
    }
).map(style_sentiment, subset=["Average Sentiment"])

# Display styled dataframe with proper labels
st.dataframe(
    styled_counties,
    use_container_width=True,
    column_config={
        "County": st.column_config.TextColumn(
            "County Name", help="Name of the county", width="medium"
        ),
        "Average Sentiment": st.column_config.NumberColumn(
            "Average Sentiment",
            help="Average sentiment score from -1 (negative) to 1 (positive)",
            format="%.2f",
            width="medium",
        ),
        "Tweet Count": st.column_config.NumberColumn(
            "Tweet Volume",
            help="Number of tweets analyzed for this county",
            format="%d",
            width="medium",
        ),
        "Positive Ratio": st.column_config.NumberColumn(
            "Positive %",
            help="Percentage of positive sentiment tweets",
            format="%.1f%%",
            width="medium",
        ),
    },
    hide_index=True,
)

# Correlation Analysis
st.subheader("Market Correlation Analysis")

# Standardize county names using centralized utility
density["County"] = density["County"].apply(add_county_suffix)

# Merge sentiment with density data
market_correlation = pd.merge(
    county_sentiment,
    density[["County", "Dispensary_PerCapita", "Population"]],
    on="County",
    how="inner",
)

# Check if merge resulted in sufficient data
if len(market_correlation) >= 2:
    # Create scatter plot
    fig_correlation = create_scatter_plot(
        market_correlation,
        x="Dispensary_PerCapita",
        y="Average Sentiment",
        title="Market Density vs. Social Sentiment",
        x_label="Retailers per 100k Residents",
        y_label="Average Sentiment Score",
        size="Population",
        color="Tweet Count",
        hover_data=["County", "Positive Ratio"],
        color_continuous_scale="Greens",
        trendline="ols",
        trendline_color_override="#4CAF50"
    )

    fig_correlation.update_layout(showlegend=False)

    st.plotly_chart(fig_correlation, use_container_width=True)

    # Add correlation statistics
    correlation = market_correlation["Dispensary_PerCapita"].corr(
        market_correlation["Average Sentiment"]
    )

    # Check if correlation is valid (not NaN)
    if pd.notna(correlation):
        st.info(
            f"""
            **Market-Sentiment Correlation**
            - Correlation Coefficient: {correlation:.2f}
            - This suggests a {'strong' if abs(correlation) > 0.5 else 'moderate' if abs(correlation) > 0.3 else 'weak'}
              {'positive' if correlation > 0 else 'negative'} relationship between market density and public sentiment.
        """
        )
    else:
        st.warning("⚠️ Unable to calculate correlation. The data may have insufficient variation.")
elif len(market_correlation) == 1:
    show_correlation_warning(1)
    st.dataframe(market_correlation[["County", "Dispensary_PerCapita", "Average Sentiment"]], use_container_width=True)
else:
    show_correlation_warning(0)

# Key Insights
st.subheader("Key Insights")

# Calculate dynamic insights
# 1. Temporal patterns
try:
    if len(monthly_sentiment) >= 3:
        # Calculate trend direction
        recent_3_months = monthly_sentiment.tail(3)["Sentiment"]
        sentiment_trend = "increasing" if recent_3_months.iloc[-1] > recent_3_months.iloc[0] else "decreasing"

        # Calculate volume correlation with sentiment
        volume_sentiment_corr = monthly_sentiment["Volume"].corr(monthly_sentiment["Sentiment"])
        correlation_strength = "strong" if abs(volume_sentiment_corr) > 0.5 else "moderate" if abs(volume_sentiment_corr) > 0.3 else "weak"
        correlation_direction = "positive" if volume_sentiment_corr > 0 else "negative"

        # Find peak sentiment month
        peak_month = monthly_sentiment.nlargest(1, "Sentiment").iloc[0]
        peak_date = peak_month["Date"].strftime("%B %Y")
    else:
        sentiment_trend = "insufficient data"
        correlation_strength = "unknown"
        correlation_direction = "unknown"
        peak_date = "N/A"
except:
    sentiment_trend = "unknown"
    correlation_strength = "unknown"
    correlation_direction = "unknown"
    peak_date = "N/A"

# 2. Geographic insights
if len(county_sentiment) >= 3:
    # Compare urban (high tweet count) vs rural (low tweet count) sentiment
    median_tweet_count = county_sentiment["Tweet Count"].median()
    urban_counties = county_sentiment[county_sentiment["Tweet Count"] > median_tweet_count]
    rural_counties = county_sentiment[county_sentiment["Tweet Count"] <= median_tweet_count]

    if len(urban_counties) > 0 and len(rural_counties) > 0:
        urban_sentiment = urban_counties["Average Sentiment"].mean()
        rural_sentiment = rural_counties["Average Sentiment"].mean()
        sentiment_difference = urban_sentiment - rural_sentiment
        urban_more_positive = urban_sentiment > rural_sentiment
    else:
        sentiment_difference = 0
        urban_more_positive = True

    # Market-sentiment correlation
    if len(market_correlation) >= 2 and pd.notna(correlation):
        correlation_interpretation = (
            "positive" if correlation > 0.1 else
            "negative" if correlation < -0.1 else
            "neutral"
        )
    else:
        correlation_interpretation = "unclear"
else:
    sentiment_difference = 0
    urban_more_positive = True
    correlation_interpretation = "unclear"

col1, col2 = st.columns(2)

with col1:
    if sentiment_trend != "unknown" and sentiment_trend != "insufficient data":
        st.info(
            f"""
            **Temporal Patterns**
            - Sentiment is **{sentiment_trend}** over recent months
            - **{correlation_strength.capitalize()} {correlation_direction}** correlation between volume and sentiment
            - Peak sentiment occurred in **{peak_date}**
            """
        )
    else:
        st.info(
            """
            **Temporal Patterns**
            - Insufficient historical data for trend analysis
            - More data points needed for pattern detection
            - Continue monitoring for emerging trends
            """
        )

with col2:
    if correlation_interpretation != "unclear":
        st.success(
            f"""
            **Geographic Insights**
            - {'Urban' if urban_more_positive else 'Rural'} areas show **{abs(sentiment_difference):.2f}** points higher sentiment
            - Market density shows **{correlation_interpretation}** correlation with sentiment
            - Regional acceptance levels vary significantly across counties
            """
        )
    else:
        st.success(
            """
            **Geographic Insights**
            - Limited geographic data for comprehensive analysis
            - County-level patterns emerging as data grows
            - Regional variations require more data points
            """
        )

# Footer
st.markdown("---")
st.caption("Data based on BERT sentiment analysis of Twitter data")
