"""
Plot helper functions for creating consistent visualizations across the dashboard.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional, Any
from config.theme import PLOTLY_THEME, GREEN_PALETTE, COLOR_SCALES


def get_california_map_layout() -> Dict[str, Any]:
    """
    Get standardized layout configuration for California county maps.

    Returns:
        Layout configuration for California-focused choropleth maps
    """
    return {
        "margin": {"r": 0, "t": 30, "l": 0, "b": 0},
        "height": 600,
        "geo": dict(
            center=dict(lat=37.0902, lon=-120.7129),
            projection_scale=5.5,
            visible=False,
            fitbounds="locations",
        ),
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
    }


def create_bar_chart(
    data: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
    color: Optional[str] = None,
    **kwargs
) -> go.Figure:
    """
    Create a standardized bar chart with cannabis theme.

    Args:
        data: DataFrame containing the data
        x: Column name for x-axis
        y: Column name for y-axis
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        color: Column name for color grouping
        **kwargs: Additional arguments to pass to px.bar()

    Returns:
        Configured bar chart
    """
    # Set default color if not provided and no color column specified
    if color is None and 'color_discrete_sequence' not in kwargs:
        kwargs['color_discrete_sequence'] = [GREEN_PALETTE["primary"]]

    fig = px.bar(
        data,
        x=x,
        y=y,
        title=title,
        template=PLOTLY_THEME,
        color=color,
        **kwargs
    )

    # Apply axis labels if provided
    layout_updates = {}
    if x_label:
        layout_updates['xaxis_title'] = x_label
    if y_label:
        layout_updates['yaxis_title'] = y_label

    if layout_updates:
        fig.update_layout(**layout_updates)

    return fig


def create_line_chart(
    data: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
    color: Optional[str] = None,
    **kwargs
) -> go.Figure:
    """
    Create a standardized line chart with cannabis theme.

    Args:
        data: DataFrame containing the data
        x: Column name for x-axis
        y: Column name for y-axis
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        color: Column name for color grouping
        **kwargs: Additional arguments to pass to px.line()

    Returns:
        Configured line chart
    """
    fig = px.line(
        data,
        x=x,
        y=y,
        title=title,
        template=PLOTLY_THEME,
        color=color,
        **kwargs
    )

    # Apply green color to line if no color column specified
    if color is None:
        fig.update_traces(line_color=GREEN_PALETTE["primary"])

    # Apply axis labels if provided
    layout_updates = {}
    if x_label:
        layout_updates['xaxis_title'] = x_label
    if y_label:
        layout_updates['yaxis_title'] = y_label

    if layout_updates:
        fig.update_layout(**layout_updates)

    return fig


def create_histogram(data, x, title, x_label=None, y_label=None, **kwargs):
    """
    Create a standardized histogram with cannabis theme.

    Args:
        data: DataFrame containing the data
        x (str): Column name for histogram
        title (str): Chart title
        x_label (str, optional): X-axis label
        y_label (str, optional): Y-axis label
        **kwargs: Additional arguments to pass to px.histogram()

    Returns:
        plotly.graph_objects.Figure: Configured histogram
    """
    fig = px.histogram(
        data,
        x=x,
        title=title,
        template=PLOTLY_THEME,
        **kwargs
    )

    # Apply green color
    fig.update_traces(marker_color=GREEN_PALETTE["primary"])

    # Apply axis labels if provided
    layout_updates = {}
    if x_label:
        layout_updates['xaxis_title'] = x_label
    if y_label:
        layout_updates['yaxis_title'] = y_label

    if layout_updates:
        fig.update_layout(**layout_updates)

    return fig


def create_choropleth_map(
    data: pd.DataFrame,
    geojson: Dict[str, Any],
    locations: str,
    color: str,
    title: str,
    hover_data: Optional[List[str]] = None,
    labels: Optional[Dict[str, str]] = None
) -> go.Figure:
    """
    Create a standardized California county choropleth map.

    Args:
        data: DataFrame containing the data
        geojson: GeoJSON data for California counties
        locations: Column name for location matching
        color: Column name for color values
        title: Map title
        hover_data: Columns to show on hover
        labels: Custom labels for columns

    Returns:
        Configured choropleth map
    """
    fig = px.choropleth(
        data,
        geojson=geojson,
        locations=locations,
        featureidkey="properties.NAME",
        color=color,
        color_continuous_scale=COLOR_SCALES["sequential"],
        scope="usa",
        title=title,
        hover_data=hover_data,
        labels=labels,
    )

    # Apply California-specific map layout
    fig.update_layout(**get_california_map_layout())

    return fig


def create_scatter_plot(data, x, y, title, x_label=None, y_label=None, color=None, size=None, **kwargs):
    """
    Create a standardized scatter plot with cannabis theme.

    Args:
        data: DataFrame containing the data
        x (str): Column name for x-axis
        y (str): Column name for y-axis
        title (str): Chart title
        x_label (str, optional): X-axis label
        y_label (str, optional): Y-axis label
        color (str, optional): Column name for color grouping
        size (str, optional): Column name for marker size
        **kwargs: Additional arguments to pass to px.scatter()

    Returns:
        plotly.graph_objects.Figure: Configured scatter plot
    """
    fig = px.scatter(
        data,
        x=x,
        y=y,
        title=title,
        template=PLOTLY_THEME,
        color=color,
        size=size,
        **kwargs
    )

    # Apply green color if no color column specified
    if color is None:
        fig.update_traces(marker_color=GREEN_PALETTE["primary"])

    # Apply axis labels if provided
    layout_updates = {}
    if x_label:
        layout_updates['xaxis_title'] = x_label
    if y_label:
        layout_updates['yaxis_title'] = y_label

    if layout_updates:
        fig.update_layout(**layout_updates)

    return fig
