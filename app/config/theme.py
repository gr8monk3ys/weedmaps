"""
Theme and styling configuration for the Cannabis Analytics Dashboard.

This module contains centralized theme settings for Plotly visualizations
to ensure consistent styling across all charts and graphs.
"""

# Plotly template to use for all charts
PLOTLY_THEME = "plotly_dark"

# Cannabis-themed green color palette
GREEN_PALETTE = {
    "primary": "#4CAF50",      # Medium green
    "secondary": "#81C784",    # Light green
    "accent": "#66BB6A",       # Soft green
    "dark": "#388E3C",         # Dark green
    "light": "#C8E6C9",        # Very light green
}

# Color scales for different visualization types
COLOR_SCALES = {
    "sequential": "Greens",           # For heatmaps, choropleths
    "diverging": "RdYlGn",            # For sentiment analysis
    "categorical": [                   # For discrete categories
        GREEN_PALETTE["primary"],
        GREEN_PALETTE["secondary"],
        GREEN_PALETTE["accent"],
        GREEN_PALETTE["dark"],
        GREEN_PALETTE["light"],
    ]
}


def get_default_layout(height=None, title=None):
    """
    Get default layout configuration for Plotly charts.

    Args:
        height (int, optional): Chart height in pixels
        title (str, optional): Chart title

    Returns:
        dict: Layout configuration dictionary
    """
    layout = {
        "template": PLOTLY_THEME,
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {
            "color": "#FFFFFF",
            "family": "Arial, sans-serif"
        },
    }

    if height:
        layout["height"] = height

    if title:
        layout["title"] = {
            "text": title,
            "x": 0.5,
            "xanchor": "center"
        }

    return layout


def apply_green_theme(fig):
    """
    Apply the green cannabis theme to a Plotly figure.

    Args:
        fig: Plotly figure object

    Returns:
        fig: Updated figure with theme applied
    """
    fig.update_layout(**get_default_layout())
    return fig
