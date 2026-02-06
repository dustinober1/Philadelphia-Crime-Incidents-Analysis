"""Publication-quality visualization utilities.

This package provides reusable visualization functions with consistent
styling, multi-format output (PNG, SVG, PDF), and memory-efficient
figure handling.

Modules:
    style: Matplotlib style configuration (color palette and rcParams)
    helpers: Figure saving utilities for reproducible output artifacts
    plots: Reusable high-level plot helpers for CLI analysis commands

Example:
    >>> from analysis.visualization import setup_style, plot_line, save_figure
    >>> setup_style()
    >>> fig = plot_line(df, x_col="year", y_col="count", title="Annual Trend")
    >>> save_figure(fig, "output.png", output_format="png")

See CLAUDE.md for CLI usage patterns and output conventions.
"""

# Style configuration
# Forecast plotting functions (preserved for backward compatibility)
from analysis.visualization import forecast_plots

# Helper functions
from analysis.visualization.helpers import save_figure

# Plot functions
from analysis.visualization.plots import plot_bar, plot_heatmap, plot_line
from analysis.visualization.style import COLORS, setup_style

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
