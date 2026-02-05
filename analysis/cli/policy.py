"""Policy evaluation analysis commands."""

import typer
from rich.console import Console

from analysis.config.schemas.policy import (
    CompositionConfig,
    EventsConfig,
    RetailTheftConfig,
    VehicleCrimesConfig,
)

app = typer.Typer(help="Policy evaluation analyses")
console = Console()


@app.command(name="retail-theft")
def retail_theft(
    baseline_start: str = typer.Option("2019-01-01", help="Baseline period start"),
    baseline_end: str = typer.Option("2020-02-01", help="Baseline period end"),
    version: str = typer.Option("v1.0", help="Output version tag"),
    fast: bool = typer.Option(False, "--fast", help="Fast mode with 10% sample"),
) -> None:
    """Analyze retail theft trends."""
    config = RetailTheftConfig(
        baseline_start=baseline_start, baseline_end=baseline_end, version=version
    )
    console.print("[bold blue]Retail Theft Analysis[/bold blue]")
    console.print(f"  Baseline: {config.baseline_start} to {config.baseline_end}")
    console.print(f"  Fast mode: {fast}")
    console.print()
    console.print("[yellow]Command logic will be implemented in plan 06-06[/yellow]")


@app.command(name="vehicle-crimes")
def vehicle_crimes(
    ucr_codes: list[int] = typer.Option([700], help="UCR codes for vehicle crimes"),
    start_date: str = typer.Option("2019-01-01", help="Analysis start date"),
    end_date: str = typer.Option("2023-12-31", help="Analysis end date"),
    version: str = typer.Option("v1.0", help="Output version tag"),
    fast: bool = typer.Option(False, "--fast", help="Fast mode with 10% sample"),
) -> None:
    """Analyze vehicle crime trends."""
    config = VehicleCrimesConfig(
        ucr_codes=ucr_codes, start_date=start_date, end_date=end_date, version=version
    )
    console.print("[bold blue]Vehicle Crimes Analysis[/bold blue]")
    console.print(f"  UCR codes: {config.ucr_codes}")
    console.print(f"  Period: {config.start_date} to {config.end_date}")
    console.print(f"  Fast mode: {fast}")
    console.print()
    console.print("[yellow]Command logic will be implemented in plan 06-06[/yellow]")


@app.command(name="composition")
def composition(
    top_n: int = typer.Option(10, help="Number of top categories to show"),
    version: str = typer.Option("v1.0", help="Output version tag"),
    fast: bool = typer.Option(False, "--fast", help="Fast mode with 10% sample"),
) -> None:
    """Analyze crime composition over time."""
    config = CompositionConfig(top_n=top_n, version=version)
    console.print("[bold blue]Crime Composition Analysis[/bold blue]")
    console.print(f"  Top N: {config.top_n}")
    console.print(f"  Fast mode: {fast}")
    console.print()
    console.print("[yellow]Command logic will be implemented in plan 06-06[/yellow]")


@app.command(name="events")
def events(
    days_before: int = typer.Option(7, help="Days before event to include"),
    days_after: int = typer.Option(7, help="Days after event to include"),
    version: str = typer.Option("v1.0", help="Output version tag"),
    fast: bool = typer.Option(False, "--fast", help="Fast mode with 10% sample"),
) -> None:
    """Analyze impact of events on crime."""
    config = EventsConfig(days_before=days_before, days_after=days_after, version=version)
    console.print("[bold blue]Event Impact Analysis[/bold blue]")
    console.print(f"  Window: {config.days_before} days before, {config.days_after} days after")
    console.print(f"  Fast mode: {fast}")
    console.print()
    console.print("[yellow]Command logic will be implemented in plan 06-06[/yellow]")
