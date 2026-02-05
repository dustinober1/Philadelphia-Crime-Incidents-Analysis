"""Visualization module for crime analysis.

This module provides a unified API for creating and saving visualizations
with consistent styling across all analysis outputs. It supports multiple
output formats (PNG, SVG, PDF) and publication-quality settings.

Key exports:
    - setup_style(): Configure matplotlib with project-standard settings
    - COLORS: Project color palette (Violent, Property, Other)
    - save_figure(): Save figures in PNG, SVG, or PDF format
    - plot_line(), plot_bar(), plot_heatmap(): Common plot functions

Example:
    >>> from analysis.visualization import setup_style, save_figure, plot_line
    >>> import pandas as pd
    >>>
    >>> # Create and save a line plot
    >>> df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
    >>> fig = plot_line(df, 'x', 'y', title='Crime Trend')
    >>> save_figure(fig, 'output.png', 'png')

The forecast_plots module is also available for specialized forecast
visualizations and is preserved for backward compatibility.
"""

# Style configuration
from analysis.visualization.style import COLORS, setup_style

# Helper functions
from analysis.visualization.helpers import save_figure

# Plot functions
from analysis.visualization.plots import plot_bar, plot_heatmap, plot_line

# Forecast plotting functions (preserved for backward compatibility)
from analysis.visualization import forecast_plots

__all__ = [
    # Style
    "setup_style",
    "COLORS",
    # Helpers
    "save_figure",
    # Plots
    "plot_line",
    "plot_bar",
    "plot_heatmap",
    # Legacy (backward compatibility)
    "forecast_plots",
]
