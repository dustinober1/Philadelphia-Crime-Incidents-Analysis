"""Command-line interface for crime incident analysis.

This package provides typer-based CLI commands for running crime analysis
scripts with Rich progress bars and configurable output.

Entry point: python -m analysis.cli

Command groups:
    chief: Chief-level analyses (trends, seasonality, covid)
    patrol: Patrol analyses (hotspots, robbery-heatmap, etc.)
    policy: Policy analyses (retail-theft, vehicle-crimes, etc.)
    forecasting: Forecasting analyses (time-series, classification)

Common arguments:
    --fast: Fast mode with 10% sample (for testing)
    --version: Output version tag (default: v1.0)
    --output-format: Figure format (png, svg, pdf)
"""

from analysis.cli.main import app

__all__ = ["app"]
