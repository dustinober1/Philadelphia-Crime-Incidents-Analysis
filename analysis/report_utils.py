"""Utilities for rendering report templates and data quality summaries."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape


def generate_data_quality_summary(df: pd.DataFrame) -> Dict[str, object]:
    """Generate summary statistics for data quality.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataset to summarize.

    Returns
    -------
    dict
        Summary including missing percentages, date range, and year distribution.
    """
    missing_pct = (df.isna().mean() * 100).round(2).sort_values(ascending=False)
    n_records = len(df)

    date_range = None
    year_distribution = None
    if "dispatch_date" in df.columns:
        date_range = {
            "min": df["dispatch_date"].min(),
            "max": df["dispatch_date"].max(),
        }
    if "year" in df.columns:
        year_distribution = df["year"].value_counts().sort_index().to_dict()
    elif "dispatch_date" in df.columns:
        year_distribution = (
            df["dispatch_date"].dt.year.value_counts().sort_index().to_dict()
        )

    return {
        "n_records": n_records,
        "missing_pct": missing_pct.to_dict(),
        "date_range": date_range,
        "year_distribution": year_distribution,
    }


def render_report_template(template_path: Path, context: Dict[str, object]) -> str:
    """Render a Jinja2 markdown template.

    Parameters
    ----------
    template_path : pathlib.Path
        Path to the Jinja2 template.
    context : dict
        Template context values.

    Returns
    -------
    str
        Rendered markdown content.
    """
    env = Environment(
        loader=FileSystemLoader(template_path.parent),
        autoescape=select_autoescape(),
    )
    template = env.get_template(template_path.name)
    return template.render(**context)


def format_data_quality_table(summary: Dict[str, object]) -> str:
    """Format a data quality summary into a markdown table.

    Parameters
    ----------
    summary : dict
        Summary from ``generate_data_quality_summary``.

    Returns
    -------
    str
        Markdown table string.
    """
    missing_pct = summary.get("missing_pct", {}) or {}
    lines = ["| Column | Missing % |", "|---|---:|"]
    for column, pct in missing_pct.items():
        lines.append(f"| {column} | {pct:.2f} |")
    return "\n".join(lines)
