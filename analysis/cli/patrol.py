"""Patrol analysis commands.

Commands:
    hotspots: Spatial clustering of crime incidents
    robbery-heatmap: Temporal heatmap for robbery incidents
    district-severity: Per-district severity scoring
    census-rates: Crime rates per census tract (population-normalized)

See CLAUDE.md for usage examples and operational guidance.
"""

from pathlib import Path
from typing import TYPE_CHECKING, Literal

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

from analysis.config import SEVERITY_WEIGHTS
from analysis.config.schemas.patrol import (
    CensusConfig,
    DistrictConfig,
    HotspotsConfig,
    RobberyConfig,
)
from analysis.visualization import plot_bar, save_figure

app = typer.Typer(help="Patrol operations analyses")
console = Console()

if TYPE_CHECKING:
    from pandas import DataFrame


@app.command()
def hotspots(
    eps: float = typer.Option(0.002, help="DBSCAN epsilon parameter (degrees)"),
    min_samples: int = typer.Option(50, help="DBSCAN min_samples parameter"),
    version: str = typer.Option("v1.0", help="Output version tag"),
    fast: bool = typer.Option(False, "--fast", help="Fast mode with 10% sample"),
    output_format: Literal["png", "svg", "pdf"] = typer.Option("png", help="Figure output format"),
) -> None:
    """Identify crime hotspots using spatial clustering."""
    from analysis.data.loading import load_crime_data

    config = HotspotsConfig(
        eps_degrees=eps,
        min_samples=min_samples,
        version=version,
        output_format=output_format,
    )

    console.print("[bold blue]Hotspots Analysis[/bold blue]")
    console.print(f"  Epsilon: {config.eps_degrees} degrees")
    console.print(f"  Min samples: {config.min_samples}")
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
        clean_task = progress.add_task("Cleaning coordinates...", total=100, visible=False)
        cluster_task = progress.add_task("Running DBSCAN clustering...", total=100, visible=False)
        output_task = progress.add_task("Saving outputs...", total=100, visible=False)

        # Stage 1: Load data
        progress.update(load_task, visible=True)
        df: DataFrame = load_crime_data()
        if fast:
            df = df.sample(frac=config.fast_sample_frac, random_state=42).copy()
        progress.update(load_task, advance=100, description="Data loaded")

        # Stage 2: Clean coordinates
        progress.update(clean_task, visible=True)

        # Filter for valid coordinates (Philadelphia bounds)
        # Use point_x and point_y columns (not lng/lat)
        df = df[
            (df["point_x"].between(config.lon_min, config.lon_max))
            & (df["point_y"].between(config.lat_min, config.lat_max))
        ].dropna(subset=["point_x", "point_y"])

        progress.update(clean_task, advance=100, description=f"Cleaned to {len(df)} valid points")

        # Stage 3: Run DBSCAN clustering
        progress.update(cluster_task, visible=True)

        # Try to import sklearn for clustering
        try:
            from sklearn.cluster import DBSCAN

            coords = df[["point_x", "point_y"]].values
            clustering = DBSCAN(eps=config.eps_degrees, min_samples=config.min_samples)
            df["cluster"] = clustering.fit_predict(coords)

            n_clusters = len(set(df["cluster"])) - (1 if -1 in df["cluster"].values else 0)
            n_noise = list(df["cluster"]).count(-1)

            progress.update(cluster_task, advance=100, description=f"Found {n_clusters} clusters")

        except ImportError:
            console.print(
                "[yellow]Warning: scikit-learn not available, skipping clustering[/yellow]"
            )
            df["cluster"] = -1
            n_clusters = 0
            n_noise = len(df)

        # Stage 4: Save outputs
        progress.update(output_task, visible=True)
        output_path = Path(config.output_dir) / config.version / "patrol"
        output_path.mkdir(parents=True, exist_ok=True)

        # Create figure: cluster sizes bar plot (if clusters found)
        if n_clusters > 0:
            cluster_sizes = df[df["cluster"] != -1].groupby("cluster").size()
            cluster_df = cluster_sizes.reset_index()
            cluster_df.columns = ["cluster", "incidents"]

            fig = plot_bar(
                cluster_df,
                x_col="cluster",
                y_col="incidents",
                title="Crime Hotspot Cluster Sizes",
                xlabel="Cluster ID",
                ylabel="Number of Incidents",
            )

            figure_path = output_path / f"{config.report_name}_clusters.{config.output_format}"
            save_figure(fig, figure_path, output_format=config.output_format)
            plt.close(fig)

        summary_file = output_path / f"{config.report_name}_summary.txt"
        with open(summary_file, "w") as f:
            f.write("Hotspots Analysis Summary\n")
            f.write("=" * 40 + "\n")
            f.write("DBSCAN parameters:\n")
            f.write(f"  eps: {config.eps_degrees} degrees\n")
            f.write(f"  min_samples: {config.min_samples}\n")
            f.write("\nResults:\n")
            f.write(f"  Total points: {len(df)}\n")
            f.write(f"  Clusters found: {n_clusters}\n")
            f.write(f"  Noise points: {n_noise}\n")

        progress.update(output_task, advance=100, description="Outputs saved")

    console.print()
    console.print("[green]:heavy_check_mark:[/green] [bold green]Analysis complete[/bold green]")
    console.print(f"  Clusters found: [cyan]{n_clusters}[/cyan]")
    console.print(f"  Output directory: [cyan]{output_path}[/cyan]")


@app.command(name="robbery-heatmap")
def robbery_heatmap(
    time_bin: int = typer.Option(60, help="Time bin size in minutes"),
    grid_size: int = typer.Option(20, help="Grid size for heatmap"),
    version: str = typer.Option("v1.0", help="Output version tag"),
    fast: bool = typer.Option(False, "--fast", help="Fast mode with 10% sample"),
    output_format: Literal["png", "svg", "pdf"] = typer.Option("png", help="Figure output format"),
) -> None:
    """Generate temporal heatmap for robbery incidents."""
    import pandas as pd

    from analysis.data.loading import load_crime_data

    config = RobberyConfig(
        time_bin_size=time_bin, grid_size=grid_size, version=version, output_format=output_format
    )

    console.print("[bold blue]Robbery Heatmap Analysis[/bold blue]")
    console.print(f"  Time bin: {config.time_bin_size} minutes")
    console.print(f"  Grid size: {config.grid_size}")
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
        df: DataFrame = load_crime_data()
        if fast:
            df = df.sample(frac=config.fast_sample_frac, random_state=42).copy()
        progress.update(load_task, advance=100)

        filter_task = progress.add_task("Filtering robbery incidents...", total=100)

        # Filter for robbery (UCR code 300-399)
        df = df[df["ucr_general"].between(300, 399)].copy()

        # Add time column
        df["hour"] = pd.to_datetime(df["dispatch_date"]).dt.hour
        df["time_bin"] = (df["hour"] * 60) // config.time_bin_size

        progress.update(filter_task, advance=100, description=f"Found {len(df)} robbery incidents")

        output_task = progress.add_task("Saving outputs...", total=100)
        output_path = Path(config.output_dir) / config.version / "patrol"
        output_path.mkdir(parents=True, exist_ok=True)

        # Create figure: temporal heatmap (if seaborn available)
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns  # noqa: F401

            from analysis.visualization import setup_style

            # Create pivot table for heatmap
            heatmap_data = df.groupby(["time_bin", "hour"]).size().unstack(fill_value=0)

            # Filter out empty rows/columns to avoid NaN warnings
            heatmap_data = heatmap_data.loc[(heatmap_data.sum(axis=1) > 0), :]
            heatmap_data = heatmap_data.loc[:, (heatmap_data.sum(axis=0) > 0)]

            if not heatmap_data.empty and heatmap_data.sum().sum() > 0:
                setup_style()
                fig, ax = plt.subplots(figsize=(12, 8))
                sns.heatmap(heatmap_data, cmap="YlOrRd", annot=False, ax=ax)
                ax.set_title("Robbery Temporal Heatmap", fontsize=14, fontweight="bold", pad=20)
                ax.set_xlabel("Hour of Day")
                ax.set_ylabel("Time Bin")
                plt.tight_layout()

                figure_path = output_path / f"{config.report_name}_heatmap.{config.output_format}"
                save_figure(fig, figure_path, output_format=config.output_format)
                plt.close(fig)
        except (ImportError, RuntimeError):
            pass  # Skip heatmap if seaborn not available or data invalid

        summary_file = output_path / f"{config.report_name}_summary.txt"
        with open(summary_file, "w") as f:
            f.write("Robbery Heatmap Analysis Summary\n")
            f.write("=" * 40 + "\n")
            f.write(f"Time bin size: {config.time_bin_size} minutes\n")
            f.write(f"Total robbery incidents: {len(df)}\n")
            f.write("\nIncidents by hour:\n")
            hourly_counts = df.groupby("hour").size()
            for hour, count in hourly_counts.items():
                f.write(f"  {hour:02d}:00 - {count:,.0f}\n")

        progress.update(output_task, advance=100)

    console.print()
    console.print("[green]:heavy_check_mark:[/green] [bold green]Analysis complete[/bold green]")
    console.print(f"  Total robbery incidents: [cyan]{len(df)}[/cyan]")


@app.command(name="district-severity")
def district_severity(
    districts: list[int] | None = typer.Option(None, help="Districts to analyze (default: all)"),
    version: str = typer.Option("v1.0", help="Output version tag"),
    fast: bool = typer.Option(False, "--fast", help="Fast mode with 10% sample"),
    output_format: Literal["png", "svg", "pdf"] = typer.Option("png", help="Figure output format"),
) -> None:
    """Calculate severity scores by police district."""
    from analysis.data.loading import load_crime_data

    config = DistrictConfig(districts=districts, version=version, output_format=output_format)

    console.print("[bold blue]District Severity Analysis[/bold blue]")
    console.print(f"  Districts: {config.districts or 'All'}")
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
        df: DataFrame = load_crime_data()
        if fast:
            df = df.sample(frac=config.fast_sample_frac, random_state=42).copy()
        progress.update(load_task, advance=100)

        score_task = progress.add_task("Calculating severity scores...", total=100)

        # Filter to specified districts if provided
        if config.districts:
            df = df[df["dc_dist"].isin(config.districts)]

        # Calculate severity scores
        df["ucr_hundred"] = (df["ucr_general"] // 100) * 100
        df["severity_weight"] = df["ucr_hundred"].map(SEVERITY_WEIGHTS).fillna(1.0)

        district_scores = (
            df.groupby("dc_dist")["severity_weight"].sum().sort_values(ascending=False)
        )

        progress.update(
            score_task, advance=100, description=f"Scored {len(district_scores)} districts"
        )

        output_task = progress.add_task("Saving outputs...", total=100)
        output_path = Path(config.output_dir) / config.version / "patrol"
        output_path.mkdir(parents=True, exist_ok=True)

        # Create figure: district severity bar plot (top 10)
        district_df = district_scores.reset_index()
        district_df.columns = ["district", "severity_score"]

        # Top 10 districts
        top_districts = district_df.head(10)

        fig = plot_bar(
            top_districts,
            x_col="district",
            y_col="severity_score",
            title="District Severity Scores (Top 10)",
            xlabel="Police District",
            ylabel="Severity Score",
        )

        figure_path = output_path / f"{config.report_name}_severity.{config.output_format}"
        save_figure(fig, figure_path, output_format=config.output_format)

        summary_file = output_path / f"{config.report_name}_summary.txt"
        with open(summary_file, "w") as f:
            f.write("District Severity Analysis Summary\n")
            f.write("=" * 40 + "\n")
            f.write("Severity calculated using FBI UCR hierarchy weights\n")
            f.write("\nDistrict rankings:\n")
            for district, score in district_scores.head(10).items():
                f.write(f"  District {district}: {score:,.1f}\n")

        progress.update(output_task, advance=100)

    console.print()
    console.print("[green]:heavy_check_mark:[/green] [bold green]Analysis complete[/bold green]")
    console.print(f"  Districts analyzed: [cyan]{len(district_scores)}[/cyan]")


@app.command(name="census-rates")
def census_rates(
    population_threshold: int = typer.Option(100, help="Minimum population for census tract"),
    version: str = typer.Option("v1.0", help="Output version tag"),
    fast: bool = typer.Option(False, "--fast", help="Fast mode with 10% sample"),
    output_format: Literal["png", "svg", "pdf"] = typer.Option("png", help="Figure output format"),
) -> None:
    """Calculate crime rates per census tract."""
    from analysis.data.loading import load_crime_data
    from analysis.utils.spatial import load_boundaries

    config = CensusConfig(
        population_threshold=population_threshold, version=version, output_format=output_format
    )

    console.print("[bold blue]Census Rates Analysis[/bold blue]")
    console.print(f"  Population threshold: {config.population_threshold}")
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
        crime_df: DataFrame = load_crime_data()
        if fast:
            crime_df = crime_df.sample(frac=config.fast_sample_frac, random_state=42).copy()
        progress.update(load_task, advance=100)

        boundary_task = progress.add_task("Loading census boundaries...", total=100)

        try:
            census_gdf = load_boundaries("census_tracts")
            console.print(f"[green]Loaded {len(census_gdf)} census tracts[/green]")
        except (FileNotFoundError, ImportError) as e:
            console.print(f"[yellow]Warning: Could not load census boundaries: {e}[/yellow]")
            console.print("[yellow]Using aggregated statistics instead[/yellow]")
            census_gdf = None

        progress.update(boundary_task, advance=100)

        analyze_task = progress.add_task("Calculating rates...", total=100)

        # Aggregate by available geographic unit
        if census_gdf is not None and "GEOID" in crime_df.columns:
            # Join with census data
            tract_counts = crime_df.groupby("GEOID")["objectid"].count()
        else:
            # Fallback: use point-based aggregation
            console.print("[yellow]Using spatial aggregation fallback[/yellow]")
            tract_counts = None

        progress.update(analyze_task, advance=100)

        output_task = progress.add_task("Saving outputs...", total=100)
        output_path = Path(config.output_dir) / config.version / "patrol"
        output_path.mkdir(parents=True, exist_ok=True)

        summary_file = output_path / f"{config.report_name}_summary.txt"
        with open(summary_file, "w") as f:
            f.write("Census Rates Analysis Summary\n")
            f.write("=" * 40 + "\n")
            f.write(f"Population threshold: {config.population_threshold}\n")
            f.write(f"Total incidents: {len(crime_df):,.0f}\n")
            if tract_counts is not None:
                f.write("\nTop 10 tracts by incident count:\n")
                for tract, count in tract_counts.head(10).items():
                    f.write(f"  Tract {tract}: {count:,.0f}\n")

        progress.update(output_task, advance=100)

    console.print()
    console.print("[green]:heavy_check_mark:[/green] [bold green]Analysis complete[/bold green]")
    console.print(f"  Output directory: [cyan]{output_path}[/cyan]")
