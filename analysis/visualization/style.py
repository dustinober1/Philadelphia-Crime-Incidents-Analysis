"""Matplotlib style configuration.

This module provides functions for setting up consistent matplotlib
styling across all analysis scripts.

Functions:
    setup_style: Configure matplotlib rcParams with project style defaults

Style configuration:
    - Color palette from ``analysis.config.COLORS``
    - Sans-serif font stack for readable report exports
    - Publication-focused save defaults (tight bbox, white facecolor, 300 DPI)

See CLAUDE.md for style and export conventions used by CLI commands.
"""

from analysis.config import COLORS

# Re-export COLORS for convenience
COLORS = COLORS


def setup_style() -> None:
    """Configure matplotlib with project-standard style settings.

    This function applies consistent styling across all visualizations including:
    - Figure size: (12, 6) for standard plots
    - Font sizes: 11pt base, 14pt titles, 12pt axis labels
    - Grid: Enabled with 30% transparency
    - Save settings: 300 DPI, tight bounding box, white background
    - Legend: Semi-transparent with 10pt font

    The color palette from analysis.config.COLORS is applied to seaborn.
    """
    import matplotlib.pyplot as plt
    import seaborn as sns

    # Set seaborn color palette using project COLORS
    sns.set_palette(list(COLORS.values()))

    # Configure matplotlib rcParams
    plt.rcParams["figure.figsize"] = (12, 6)
    plt.rcParams["font.size"] = 11
    plt.rcParams["axes.titlesize"] = 14
    plt.rcParams["axes.titleweight"] = "bold"
    plt.rcParams["axes.labelsize"] = 12
    plt.rcParams["axes.labelweight"] = "bold"
    plt.rcParams["axes.grid"] = True
    plt.rcParams["grid.alpha"] = 0.3
    plt.rcParams["savefig.dpi"] = 300
    plt.rcParams["savefig.bbox"] = "tight"
    plt.rcParams["savefig.facecolor"] = "white"
    plt.rcParams["legend.framealpha"] = 0.9
    plt.rcParams["legend.fontsize"] = 10
