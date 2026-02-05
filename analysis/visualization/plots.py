"""Common plot functions for crime analysis visualizations.

This module provides reusable plotting functions that return matplotlib Figure
objects with consistent styling using the project's color palette.

All functions return Figure objects - the caller is responsible for saving
using the save_figure() helper.
"""

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.figure import Figure

from analysis.visualization.style import COLORS, setup_style


def plot_line(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    xlabel: str = "",
    ylabel: str = "",
    color: str | None = None,
) -> Figure:
    """Create a line plot with consistent styling.

    Args:
        data: DataFrame containing the data to plot.
        x_col: Column name for x-axis values.
        y_col: Column name for y-axis values.
        title: Plot title.
        xlabel: X-axis label. Defaults to empty string (uses x_col if not provided).
        ylabel: Y-axis label. Defaults to empty string (uses y_col if not provided).
        color: Line color. If None, uses the first color from COLORS palette.

    Returns:
        matplotlib Figure object ready for display or saving.

    Note:
        The function applies setup_style() to ensure consistent styling.
    """
    setup_style()

    fig, ax = plt.subplots()

    # Use project color if not specified
    if color is None:
        color = COLORS.get("Violent", "#E63946")

    ax.plot(data[x_col], data[y_col], color=color, linewidth=2, marker="o", markersize=4)

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel(xlabel or x_col, fontsize=12, fontweight="bold")
    ax.set_ylabel(ylabel or y_col, fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def plot_bar(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    xlabel: str = "",
    ylabel: str = "",
    color: str | None = None,
) -> Figure:
    """Create a vertical bar plot with consistent styling.

    Args:
        data: DataFrame containing the data to plot.
        x_col: Column name for x-axis categories.
        y_col: Column name for y-axis values.
        title: Plot title.
        xlabel: X-axis label. Defaults to empty string (uses x_col if not provided).
        ylabel: Y-axis label. Defaults to empty string (uses y_col if not provided).
        color: Bar color. If None, uses the first color from COLORS palette.

    Returns:
        matplotlib Figure object ready for display or saving.

    Note:
        The function applies setup_style() to ensure consistent styling.
    """
    setup_style()

    fig, ax = plt.subplots()

    # Use project color if not specified
    if color is None:
        color = COLORS.get("Property", "#457B9D")

    ax.bar(data[x_col], data[y_col], color=color, alpha=0.8)

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel(xlabel or x_col, fontsize=12, fontweight="bold")
    ax.set_ylabel(ylabel or y_col, fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    return fig


def plot_heatmap(
    data: pd.DataFrame,
    title: str,
    figsize: tuple[int, int] = (12, 10),
    cmap: str = "coolwarm",
    center: float = 0,
    annot: bool = True,
    fmt: str = ".2f",
) -> Figure:
    """Create a correlation heatmap with consistent styling.

    Args:
        data: DataFrame containing the data for heatmap (typically correlation matrix).
        title: Plot title.
        figsize: Figure size as (width, height) in inches. Defaults to (12, 10).
        cmap: Colormap name. Defaults to 'coolwarm'.
        center: Value at which to center the colormap. Defaults to 0.
        annot: Whether to annotate cells with values. Defaults to True.
        fmt: Format string for annotations. Defaults to '.2f'.

    Returns:
        matplotlib Figure object ready for display or saving.

    Note:
        The function applies setup_style() to ensure consistent styling.
        Uses seaborn's heatmap function with a triangular mask for cleaner display.
    """
    import numpy as np
    import seaborn as sns

    setup_style()

    fig, ax = plt.subplots(figsize=figsize)

    # Create triangular mask for cleaner display
    mask = np.triu(np.ones_like(data, dtype=bool))

    sns.heatmap(
        data,
        mask=mask,
        annot=annot,
        fmt=fmt,
        cmap=cmap,
        center=center,
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": 0.8},
        ax=ax,
    )

    ax.set_title(title, fontsize=14, fontweight="bold", pad=20)

    plt.tight_layout()
    return fig
