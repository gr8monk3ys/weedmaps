"""
Configuration module for the Cannabis Analytics Dashboard.
"""

from .regions import CALIFORNIA_REGIONS, SIMPLE_REGIONS
from .theme import PLOTLY_THEME, GREEN_PALETTE, get_default_layout
from .env import Config

__all__ = [
    "CALIFORNIA_REGIONS",
    "SIMPLE_REGIONS",
    "PLOTLY_THEME",
    "GREEN_PALETTE",
    "get_default_layout",
    "Config",
]
