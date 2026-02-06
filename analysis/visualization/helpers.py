"""Figure saving helpers with format-aware export settings.

This module provides utilities for saving matplotlib figures in multiple
formats while keeping output settings consistent across commands.

Functions:
    save_figure: Save a figure using png, svg, or pdf output formats

Important:
    Always call ``plt.close(fig)`` after ``save_figure`` in long-running
    scripts and tests to avoid matplotlib memory growth.

See CLAUDE.md for report output paths and testing conventions.
"""

from pathlib import Path
from typing import Literal

import matplotlib.pyplot as plt


def save_figure(
    fig: plt.Figure,
    output_path: str | Path,
    output_format: Literal["png", "svg", "pdf"] = "png",
    dpi: int = 300,
) -> None:
    """Save a matplotlib figure to the specified file path and format.

    This function handles format-specific DPI settings to ensure appropriate
    quality for each output type. PNG uses high DPI for raster output, while
    SVG and PDF use vector settings (no DPI needed).

    Args:
        fig: The matplotlib Figure object to save.
        output_path: The destination path for the saved figure.
        output_format: The file format to save as ('png', 'svg', or 'pdf').
            Defaults to 'png'.
        dpi: DPI for raster formats (PNG only). Vector formats (SVG, PDF)
            ignore this parameter. Defaults to 300.

    Raises:
        ValueError: If output_format is not one of 'png', 'svg', or 'pdf'.

    Note:
        This function does not create directories. Ensure the parent directory
        exists before calling.
        HTML/JSON output is deferred until use case emerges in Phase 8.
    """
    if output_format not in ("png", "svg", "pdf"):
        raise ValueError(f"output_format must be 'png', 'svg', or 'pdf', got '{output_format}'")

    output_path = Path(output_path)

    # Set format-specific DPI
    # PNG: raster format, needs DPI setting
    # SVG/PDF: vector formats, DPI is irrelevant
    save_dpi = dpi if output_format == "png" else None

    # Save with consistent settings
    fig.savefig(
        output_path,
        format=output_format,
        dpi=save_dpi,
        bbox_inches="tight",
        facecolor="white",
    )
