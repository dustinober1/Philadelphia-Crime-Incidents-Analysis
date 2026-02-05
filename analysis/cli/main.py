"""Main CLI application for crime analysis.

Provides command groups for each analysis area:
- chief: High-level trend analyses (trends, seasonality, covid)
- patrol: Patrol operations analyses (hotspots, robbery, district, census)
- policy: Policy evaluation analyses (retail theft, vehicle, composition, events)
- forecasting: Forecasting analyses (time series, classification)
"""

import typer
from rich.console import Console

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
    """Show version information."""
    console.print("[bold blue]Crime Analysis CLI[/bold blue]")
    console.print("  Version: [cyan]v1.1[/cyan]")
    console.print(f"  typer: [cyan]{typer.__version__}[/cyan]")


@app.command()
def info() -> None:
    """Show project information."""
    from pathlib import Path

    console.print("[bold blue]Philadelphia Crime Incidents Analysis[/bold blue]")
    console.print()
    console.print("Data sources:")
    console.print("  - Philadelphia Police Department crime incidents")
    console.print("  - U.S. Census Bureau demographic data")
    console.print("  - City event schedules")
    console.print()
    console.print("Reports directory: [cyan]reports/[/cyan]")
    console.print(f"  (resolved to: [cyan]{Path('reports').resolve()}[/cyan])")


if __name__ == "__main__":
    app()
