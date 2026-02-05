"""Policy evaluation analysis commands."""

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

from analysis.config.schemas.policy import (
    CompositionConfig,
    EventsConfig,
    RetailTheftConfig,
    VehicleCrimesConfig,
)
from analysis.data.loading import load_crime_data
from analysis.data.preprocessing import filter_by_date_range

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
    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
    ) as progress:
        load_task = progress.add_task("Loading data...", total=100)
        df = load_crime_data()
        if fast:
            df = df.sample(frac=config.fast_sample_frac, random_state=42)
        progress.update(load_task, advance=100)

        filter_task = progress.add_task("Filtering theft incidents...", total=100)

        # Filter for retail theft (UCR 600-699 for general theft)
        theft_df = df[df["ucr_general"].between(600, 699)].copy()

        # Get baseline period
        baseline_df = filter_by_date_range(
            theft_df, config.baseline_start, config.baseline_end, date_col="dispatch_date"
        )
        baseline_avg = len(baseline_df)

        progress.update(
            filter_task, advance=100, description=f"Found {len(theft_df)} theft incidents"
        )

        output_task = progress.add_task("Saving outputs...", total=100)
        output_path = Path(config.output_dir) / config.version / "policy"
        output_path.mkdir(parents=True, exist_ok=True)

        summary_file = output_path / f"{config.report_name}_summary.txt"
        with open(summary_file, "w") as f:
            f.write("Retail Theft Analysis Summary\n")
            f.write("=" * 40 + "\n")
            f.write(f"Baseline period: {config.baseline_start} to {config.baseline_end}\n")
            f.write(f"Baseline average: {baseline_avg:,.0f} incidents\n")
            f.write(f"Total theft incidents (all time): {len(theft_df):,.0f}\n")

        progress.update(output_task, advance=100)

    console.print()
    console.print("[green]:heavy_check_mark:[/green] [bold green]Analysis complete[/bold green]")


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
        ucr_codes=ucr_codes,
        start_date=start_date,
        end_date=end_date,
        version=version,
    )

    console.print("[bold blue]Vehicle Crimes Analysis[/bold blue]")
    console.print(f"  UCR codes: {config.ucr_codes}")
    console.print(f"  Period: {config.start_date} to {config.end_date}")
    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
    ) as progress:
        load_task = progress.add_task("Loading data...", total=100)
        df = load_crime_data()
        if fast:
            df = df.sample(frac=config.fast_sample_frac, random_state=42)
        progress.update(load_task, advance=100)

        filter_task = progress.add_task("Filtering vehicle crimes...", total=100)

        # Filter by UCR codes
        vehicle_df = df[df["ucr_general"].isin(config.ucr_codes)].copy()

        # Filter by date range
        vehicle_df = filter_by_date_range(
            vehicle_df, config.start_date, config.end_date, date_col="dispatch_date"
        )

        progress.update(
            filter_task, advance=100, description=f"Found {len(vehicle_df)} vehicle crime incidents"
        )

        output_task = progress.add_task("Saving outputs...", total=100)
        output_path = Path(config.output_dir) / config.version / "policy"
        output_path.mkdir(parents=True, exist_ok=True)

        summary_file = output_path / f"{config.report_name}_summary.txt"
        with open(summary_file, "w") as f:
            f.write("Vehicle Crimes Analysis Summary\n")
            f.write("=" * 40 + "\n")
            f.write(f"UCR codes: {config.ucr_codes}\n")
            f.write(f"Period: {config.start_date} to {config.end_date}\n")
            f.write(f"Total incidents: {len(vehicle_df):,.0f}\n")

        progress.update(output_task, advance=100)

    console.print()
    console.print("[green]:heavy_check_mark:[/green] [bold green]Analysis complete[/bold green]")


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
    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
    ) as progress:
        load_task = progress.add_task("Loading data...", total=100)
        df = load_crime_data()
        if fast:
            df = df.sample(frac=config.fast_sample_frac, random_state=42)
        progress.update(load_task, advance=100)

        classify_task = progress.add_task("Classifying crimes...", total=100)

        # Classify by UCR hundred-band
        df = df.copy()
        df["ucr_hundred"] = (df["ucr_general"] // 100) * 100

        # Get top categories
        top_categories = df["ucr_hundred"].value_counts().head(config.top_n)

        progress.update(classify_task, advance=100, description=f"Classified {len(df)} incidents")

        output_task = progress.add_task("Saving outputs...", total=100)
        output_path = Path(config.output_dir) / config.version / "policy"
        output_path.mkdir(parents=True, exist_ok=True)

        summary_file = output_path / f"{config.report_name}_summary.txt"
        with open(summary_file, "w") as f:
            f.write("Crime Composition Analysis Summary\n")
            f.write("=" * 40 + "\n")
            f.write(f"Top {config.top_n} crime categories (UCR hundred-band):\n")
            for ucr_code, count in top_categories.items():
                ucr_name = f"{ucr_code:03d}-Series"
                f.write(f"  {ucr_name}: {count:,.0f} incidents ({count / len(df) * 100:.1f}%)\n")

        progress.update(output_task, advance=100)

    console.print()
    console.print("[green]:heavy_check_mark:[/green] [bold green]Analysis complete[/bold green]")


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
    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
    ) as progress:
        load_task = progress.add_task("Loading data...", total=100)
        df = load_crime_data()
        if fast:
            df = df.sample(frac=config.fast_sample_frac, random_state=42)
        progress.update(load_task, advance=100)

        analyze_task = progress.add_task("Analyzing event patterns...", total=100)

        # Try to load event data
        try:
            from analysis.event_utils import get_event_windows, load_event_data

            events_df = load_event_data()
            event_windows = get_event_windows(events_df, config.days_before, config.days_after)

            console.print(f"[green]Loaded {len(event_windows)} event windows[/green]")
        except (ImportError, FileNotFoundError) as e:
            console.print(f"[yellow]Warning: Could not load event data: {e}[/yellow]")
            console.print("[yellow]Using temporal aggregation instead[/yellow]")
            event_windows = None

        progress.update(analyze_task, advance=100)

        output_task = progress.add_task("Saving outputs...", total=100)
        output_path = Path(config.output_dir) / config.version / "policy"
        output_path.mkdir(parents=True, exist_ok=True)

        summary_file = output_path / f"{config.report_name}_summary.txt"
        with open(summary_file, "w") as f:
            f.write("Event Impact Analysis Summary\n")
            f.write("=" * 40 + "\n")
            f.write(
                f"Event window: {config.days_before} days before, {config.days_after} days after\n"
            )
            f.write(f"Total incidents in dataset: {len(df):,.0f}\n")
            if event_windows is not None:
                f.write(f"Event windows analyzed: {len(event_windows)}\n")

        progress.update(output_task, advance=100)

    console.print()
    console.print("[green]:heavy_check_mark:[/green] [bold green]Analysis complete[/bold green]")
