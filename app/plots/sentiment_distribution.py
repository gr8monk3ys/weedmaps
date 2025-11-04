import streamlit as st
import pandas as pd
import plotly.express as px

# Green color scale for cannabis theme
GREEN_SCALE = "Greens"


@st.cache_data()
def create_sentiment_distribution_plot(data, sentiment_column, title):
    fig = px.histogram(
        data, x=sentiment_column, title=title, color_continuous_scale=GREEN_SCALE
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig
