"""Chief-level trend analysis commands."""

from pathlib import Path

import typer
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)

from analysis.config.schemas.chief import COVIDConfig, SeasonalityConfig, TrendsConfig
from analysis.data.loading import load_crime_data
from analysis.data.preprocessing import aggregate_by_period, filter_by_date_range
from analysis.utils.classification import classify_crime_category
from analysis.utils.temporal import extract_temporal_features

# Create typer app for this command group
app = typer.Typer(help="Chief-level trend analyses (annual trends, seasonality, COVID impact)")
console = Console()


@app.command()
def trends(
    start_year: int = typer.Option(2015, help="Start year for analysis", min=2006, max=2026),
    end_year: int = typer.Option(2024, help="End year for analysis", min=2006, max=2026),
    version: str = typer.Option("v1.0", help="Output version tag"),
    fast: bool = typer.Option(False, "--fast", help="Fast mode with 10% sample"),
) -> None:
    """Generate annual crime trends analysis."""
    # Load config (fast flag controls behavior, not stored in config)
    config = TrendsConfig(start_year=start_year, end_year=end_year, version=version)

    console.print("[bold blue]Annual Trends Analysis[/bold blue]")
    console.print(f"  Period: {config.start_year}-{config.end_year}")
    console.print(f"  Version: {config.version}")
    console.print(f"  Fast mode: {fast}")
    console.print()

    # Progress bar for multi-stage workflow
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
    ) as progress:
        # Stage 1: Load data
        load_task = progress.add_task("Loading crime data...", total=100)

        df = load_crime_data(clean=True)
        if fast:
            df = df.sample(frac=config.fast_sample_frac, random_state=42)
            console.print(
                f"[yellow]Fast mode: Using {len(df)} rows ({config.fast_sample_frac:.0%} sample)[/yellow]"
            )

        progress.update(load_task, advance=100, description="Data loaded")

        # Stage 2: Preprocess data
        prep_task = progress.add_task("Preprocessing data...", total=100)

        # Add temporal features
        df = extract_temporal_features(df)

        # Filter by date range
        start_date = f"{config.start_year}-01-01"
        end_date = f"{config.end_year}-12-31"
        df = filter_by_date_range(df, start=start_date, end=end_date, date_col="dispatch_date")

        # Classify crimes
        df = classify_crime_category(df)

        progress.update(prep_task, advance=100, description="Preprocessing complete")

        # Stage 3: Generate analysis
        analyze_task = progress.add_task("Analyzing trends...", total=100)

        # Aggregate by year
        annual_df = aggregate_by_period(
            df, period="YE", date_col="dispatch_date", count_col="objectid"
        )

        progress.update(analyze_task, advance=100, description="Analysis complete")

        # Stage 4: Save outputs
        output_task = progress.add_task("Saving outputs...", total=100)

        # Create output directory
        output_path = Path(config.output_dir) / config.version / "chief"
        output_path.mkdir(parents=True, exist_ok=True)

        # Save summary statistics
        summary_file = output_path / f"{config.report_name}_summary.txt"
        with open(summary_file, "w") as f:
            f.write("Annual Trends Analysis Summary\n")
            f.write("=" * 40 + "\n")
            f.write(f"Period: {config.start_year}-{config.end_year}\n")
            f.write(f"Total incidents: {len(df)}\n")
            f.write("\nAnnual totals:\n")
            for row in annual_df.sort_values("dispatch_date").itertuples():
                year = row.dispatch_date.year
                count = row.count
                f.write(f"  {year}: {count:,.0f}\n")

        progress.update(output_task, advance=100, description="Outputs saved")

    console.print()
    console.print("[green]:heavy_check_mark:[/green] [bold green]Analysis complete[/bold green]")
    console.print(f"  Total incidents analyzed: [cyan]{len(df):,.0f}[/cyan]")
    console.print(f"  Output directory: [cyan]{output_path}[/cyan]")
    console.print(f"  Summary file: [cyan]{summary_file.name}[/cyan]")


@app.command()
def seasonality(
    summer_months: list[int] = typer.Option([6, 7, 8], help="Summer months"),
    winter_months: list[int] = typer.Option([12, 1, 2], help="Winter months"),
    version: str = typer.Option("v1.0", help="Output version tag"),
    fast: bool = typer.Option(False, "--fast", help="Fast mode with 10% sample"),
) -> None:
    """Analyze seasonal crime patterns."""
    config = SeasonalityConfig(
        summer_months=summer_months, winter_months=winter_months, version=version
    )

    console.print("[bold blue]Seasonality Analysis[/bold blue]")
    console.print(f"  Summer months: {config.summer_months}")
    console.print(f"  Winter months: {config.winter_months}")
    console.print(f"  Fast mode: {fast}")
    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
    ) as progress:
        load_task = progress.add_task("Loading data...", total=100)
        df = load_crime_data(clean=True)
        if fast:
            df = df.sample(frac=config.fast_sample_frac, random_state=42)
        progress.update(load_task, advance=100)

        prep_task = progress.add_task("Processing data...", total=100)
        df = extract_temporal_features(df)
        df = classify_crime_category(df)
        progress.update(prep_task, advance=100)

        analyze_task = progress.add_task("Analyzing seasonality...", total=100)

        # Filter for complete years
        df_filtered = filter_by_date_range(df, start="2018-01-01", end="2023-12-31", date_col="dispatch_date")

        # Calculate seasonal averages
        df_filtered = df_filtered.copy()
        df_filtered["season"] = df_filtered["month"].apply(
            lambda m: "summer" if m in config.summer_months else ("winter" if m in config.winter_months else "other")
        )
        seasonal_counts = df_filtered.groupby("season")["objectid"].count()

        progress.update(analyze_task, advance=100)

        output_task = progress.add_task("Saving outputs...", total=100)
        output_path = Path(config.output_dir) / config.version / "chief"
        output_path.mkdir(parents=True, exist_ok=True)

        summary_file = output_path / f"{config.report_name}_summary.txt"
        with open(summary_file, "w") as f:
            f.write("Seasonality Analysis Summary\n")
            f.write("=" * 40 + "\n")
            f.write(f"Summer months: {config.summer_months}\n")
            f.write(f"Winter months: {config.winter_months}\n")
            f.write(f"\nSeasonal averages:\n")
            for season, count in seasonal_counts.items():
                f.write(f"  {season.capitalize()}: {count:,.0f} incidents\n")

        progress.update(output_task, advance=100)

    console.print()
    console.print("[green]:heavy_check_mark:[/green] [bold green]Analysis complete[/bold green]")
    console.print(f"  Output directory: [cyan]{output_path}[/cyan]")
    console.print(f"  Summary file: [cyan]{summary_file.name}[/cyan]")


@app.command()
def covid(
    lockdown_date: str = typer.Option("2020-03-01", help="COVID lockdown date"),
    before_years: list[int] = typer.Option([2018, 2019], help="Pre-COVID years for comparison"),
    version: str = typer.Option("v1.0", help="Output version tag"),
    fast: bool = typer.Option(False, "--fast", help="Fast mode with 10% sample"),
) -> None:
    """Analyze COVID impact on crime patterns."""
    config = COVIDConfig(lockdown_date=lockdown_date, before_years=before_years, version=version)

    console.print("[bold blue]COVID Impact Analysis[/bold blue]")
    console.print(f"  Lockdown date: {config.lockdown_date}")
    console.print(f"  Before years: {config.before_years}")
    console.print(f"  Fast mode: {fast}")
    console.print()
    console.print("[yellow]Command logic will be implemented in plan 06-04[/yellow]")

    # TODO: Implement analysis logic in 06-04
