"""Chief-level trend analysis commands."""

from pathlib import Path
from typing import Literal

import matplotlib.pyplot as plt
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
from analysis.visualization import plot_bar, plot_line, save_figure

# Create typer app for this command group
app = typer.Typer(help="Chief-level trend analyses (annual trends, seasonality, COVID impact)")
console = Console()


@app.command()
def trends(
    start_year: int = typer.Option(2015, help="Start year for analysis", min=2006, max=2026),
    end_year: int = typer.Option(2024, help="End year for analysis", min=2006, max=2026),
    version: str = typer.Option("v1.0", help="Output version tag"),
    fast: bool = typer.Option(False, "--fast", help="Fast mode with 10% sample"),
    output_format: Literal["png", "svg", "pdf"] = typer.Option("png", help="Figure output format"),
) -> None:
    """Generate annual crime trends analysis."""
    # Load config (fast flag controls behavior, not stored in config)
    config = TrendsConfig(
        start_year=start_year, end_year=end_year, version=version, output_format=output_format
    )

    console.print("[bold blue]Annual Trends Analysis[/bold blue]")
    console.print(f"  Period: {config.start_year}-{config.end_year}")
    console.print(f"  Version: {config.version}")
    console.print(f"  Fast mode: {fast}")
    console.print()

    # Multi-task progress bar for sequential workflow
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
    ) as progress:
        # Create all tasks upfront (hidden initially)
        load_task = progress.add_task("Loading crime data...", total=100, visible=False)
        prep_task = progress.add_task("Preprocessing data...", total=100, visible=False)
        analyze_task = progress.add_task("Analyzing trends...", total=100, visible=False)
        output_task = progress.add_task("Saving outputs...", total=100, visible=False)

        # Stage 1: Load data
        progress.update(load_task, visible=True)
        df = load_crime_data(clean=True)
        if fast:
            df = df.sample(frac=config.fast_sample_frac, random_state=42)
            console.print(
                f"[yellow]Fast mode: Using {len(df)} rows ({config.fast_sample_frac:.0%} sample)[/yellow]"
            )
        progress.update(load_task, advance=100, description="Data loaded")

        # Stage 2: Preprocess data
        progress.update(prep_task, visible=True)

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
        progress.update(analyze_task, visible=True)

        # Aggregate by year
        annual_df = aggregate_by_period(
            df, period="YE", date_col="dispatch_date", count_col="objectid"
        )

        progress.update(analyze_task, advance=100, description="Analysis complete")

        # Stage 4: Save outputs
        progress.update(output_task, visible=True)

        # Create output directory
        output_path = Path(config.output_dir) / config.version / "chief"
        output_path.mkdir(parents=True, exist_ok=True)

        # Create figure: annual crime trend line
        fig = plot_line(
            annual_df,
            x_col="dispatch_date",
            y_col="count",
            title=f"Annual Crime Trends ({config.start_year}-{config.end_year})",
            xlabel="Year",
            ylabel="Number of Incidents",
        )

        # Save figure
        figure_path = output_path / f"{config.report_name}_trend.{config.output_format}"
        save_figure(fig, figure_path, output_format=config.output_format)
        plt.close(fig)

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
    output_format: Literal["png", "svg", "pdf"] = typer.Option("png", help="Figure output format"),
) -> None:
    """Analyze seasonal crime patterns."""
    config = SeasonalityConfig(
        summer_months=summer_months,
        winter_months=winter_months,
        version=version,
        output_format=output_format,
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
        df_filtered = filter_by_date_range(
            df, start="2018-01-01", end="2023-12-31", date_col="dispatch_date"
        )

        # Calculate seasonal averages
        df_filtered = df_filtered.copy()
        df_filtered["season"] = df_filtered["month"].apply(
            lambda m: (
                "summer"
                if m in config.summer_months
                else ("winter" if m in config.winter_months else "other")
            )
        )
        seasonal_counts = df_filtered.groupby("season")["objectid"].count()

        progress.update(analyze_task, advance=100)

        output_task = progress.add_task("Saving outputs...", total=100)
        output_path = Path(config.output_dir) / config.version / "chief"
        output_path.mkdir(parents=True, exist_ok=True)

        # Create figure: seasonal comparison bar plot
        seasonal_df = seasonal_counts.reset_index()
        fig = plot_bar(
            seasonal_df,
            x_col="season",
            y_col="objectid",
            title="Seasonal Crime Comparison",
            xlabel="Season",
            ylabel="Average Incidents",
        )

        # Save figure
        figure_path = output_path / f"{config.report_name}_seasonal.{config.output_format}"
        save_figure(fig, figure_path, output_format=config.output_format)
        plt.close(fig)

        summary_file = output_path / f"{config.report_name}_summary.txt"
        with open(summary_file, "w") as f:
            f.write("Seasonality Analysis Summary\n")
            f.write("=" * 40 + "\n")
            f.write(f"Summer months: {config.summer_months}\n")
            f.write(f"Winter months: {config.winter_months}\n")
            f.write("\nSeasonal averages:\n")
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
    output_format: Literal["png", "svg", "pdf"] = typer.Option("png", help="Figure output format"),
) -> None:
    """Analyze COVID impact on crime patterns."""
    import pandas as pd

    config = COVIDConfig(
        lockdown_date=lockdown_date,
        before_years=before_years,
        version=version,
        output_format=output_format,
    )

    console.print("[bold blue]COVID Impact Analysis[/bold blue]")
    console.print(f"  Lockdown date: {config.lockdown_date}")
    console.print(f"  Before years: {config.before_years}")
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

        analyze_task = progress.add_task("Comparing periods...", total=100)

        # Get pre-COVID baseline
        before_periods = []
        for year in config.before_years:
            year_data = filter_by_date_range(
                df, start=f"{year}-01-01", end=f"{year}-12-31", date_col="dispatch_date"
            )
            before_periods.append(year_data)

        baseline_df = pd.concat(before_periods, ignore_index=True)
        baseline_avg = len(baseline_df) / len(config.before_years)

        # Get post-COVID period (2021-2022)
        after_df = filter_by_date_range(
            df, start="2021-01-01", end="2022-12-31", date_col="dispatch_date"
        )

        progress.update(analyze_task, advance=100)

        output_task = progress.add_task("Saving outputs...", total=100)
        output_path = Path(config.output_dir) / config.version / "chief"
        output_path.mkdir(parents=True, exist_ok=True)

        # Create figure: before/after comparison bar plot
        comparison_df = pd.DataFrame(
            {"Period": ["Before (avg)", "After"], "Incidents": [baseline_avg, len(after_df)]}
        )
        fig = plot_bar(
            comparison_df,
            x_col="Period",
            y_col="Incidents",
            title="COVID Impact on Crime",
            xlabel="Period",
            ylabel="Number of Incidents",
        )

        # Save figure
        figure_path = output_path / f"{config.report_name}_covid_impact.{config.output_format}"
        save_figure(fig, figure_path, output_format=config.output_format)
        plt.close(fig)

        summary_file = output_path / f"{config.report_name}_summary.txt"
        with open(summary_file, "w") as f:
            f.write("COVID Impact Analysis Summary\n")
            f.write("=" * 40 + "\n")
            f.write(f"Lockdown date: {config.lockdown_date}\n")
            f.write(f"Before years: {config.before_years}\n")
            f.write(f"\nAverage incidents (before): {baseline_avg:,.0f}\n")
            f.write(f"Incidents (after): {len(after_df):,.0f}\n")
            change_pct = (len(after_df) - baseline_avg) / baseline_avg * 100
            f.write(f"Change: {change_pct:+.1f}%\n")

        progress.update(output_task, advance=100)

    console.print()
    console.print("[green]:heavy_check_mark:[/green] [bold green]Analysis complete[/bold green]")
    console.print(f"  Output directory: [cyan]{output_path}[/cyan]")
    console.print(f"  Summary file: [cyan]{summary_file.name}[/cyan]")
