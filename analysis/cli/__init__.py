"""CLI entry points for crime analysis scripts.

Usage:
    python -m analysis.cli --help
    python -m analysis.cli chief trends --help
    python -m analysis.cli chief trends --start-year 2020 --fast
"""

from analysis.cli.main import app

__all__ = ["app"]
