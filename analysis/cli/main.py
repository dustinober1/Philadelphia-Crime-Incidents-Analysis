"""CLI entry point using typer.

This module defines the main typer app and command groups for the
crime analysis CLI system.

Usage:
    python -m analysis.cli --help
    python -m analysis.cli chief trends --help
    python -m analysis.cli chief trends --fast

Architecture:
    - typer.App for command registration
    - Rich for console output (progress bars, tables, panels)
    - CliRunner for testing (typer.testing)

See CLAUDE.md for command usage and workflow guidance.
"""

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Import command groups
from analysis.cli import chief, forecasting, patrol, policy

# Create main app
app = typer.Typer(
    name="crime-analysis",
    help="Philadelphia Crime Incidents Analysis CLI",
    no_args_is_help=True,
    add_completion=False,
)

# Rich console for output
console = Console()


# Register command groups
app.add_typer(
    chief.app,
    name="chief",
    help="Chief-level trend analyses (trends, seasonality, COVID impact)",
)
app.add_typer(
    patrol.app,
    name="patrol",
    help="Patrol operations analyses (hotspots, robbery, district severity, census rates)",
)
app.add_typer(
    policy.app,
    name="policy",
    help="Policy evaluation analyses (retail theft, vehicle crimes, composition, events)",
)
app.add_typer(
    forecasting.app,
    name="forecasting",
    help="Forecasting and prediction analyses (time series, violence classification)",
)


@app.command()
def version() -> None:
    """Show CLI and runtime version details.

    Returns:
        None: Prints a Rich table with CLI, typer, and Python versions.
    """
    # Create a formatted table for version info
    table = Table(title="Crime Analysis CLI", show_header=False)
    table.add_column("Component", style="cyan")
    table.add_column("Version", style="green")

    table.add_row("CLI Version", "v1.1")
    table.add_row("typer", f"{typer.__version__}")
    table.add_row("Python", "3.14+")

    console.print(table)


@app.command()
def info() -> None:
    """Show project context and data source information.

    Returns:
        None: Prints a Rich panel with data sources, analysis areas, and
        resolved reports path.
    """
    info_text = """
[bold cyan]Data sources:[/bold cyan]
  * Philadelphia Police Department crime incidents
  * U.S. Census Bureau demographic data
  * City event schedules

[bold cyan]Analysis areas:[/bold cyan]
  * Chief: High-level trends and seasonality
  * Patrol: Spatial hotspots and district severity
  * Policy: Retail theft, vehicle crimes, event impacts
  * Forecasting: Time series and violence classification

[bold cyan]Reports directory:[/bold cyan] [green]reports/[/green]
"""

    panel = Panel(
        info_text.strip(),
        title="[bold]Philadelphia Crime Incidents Analysis[/bold]",
        border_style="blue",
    )
    console.print(panel)
    console.print()
    console.print(f"Resolved path: [cyan]{Path('reports').resolve()}[/cyan]")


if __name__ == "__main__":
    app()
