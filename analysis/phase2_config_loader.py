"""Phase 2 configuration loader for Spatial & Socioeconomic Analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

import yaml


@dataclass
class ClusteringConfig:
    """DBSCAN clustering parameters."""

    eps_degrees: float = 0.002
    min_samples: int = 50
    algorithm: str = "DBSCAN"


@dataclass
class HeatmapConfig:
    """Heatmap analysis parameters."""

    robbery_ucr_range: Tuple[int, int] = (300, 400)
    hours: Tuple[int, int] = (0, 23)
    days: List[str] = field(
        default_factory=lambda: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    )


@dataclass
class CensusConfig:
    """Census tract analysis parameters."""

    population_column: str = "total_pop"
    rate_per: int = 100000
    min_population: int = 100


@dataclass
class CoordinateBounds:
    """Philadelphia coordinate bounds for validation."""

    min_lon: float = -75.30
    max_lon: float = -74.95
    min_lat: float = 39.85
    max_lat: float = 40.15


@dataclass
class BoundaryPaths:
    """Paths to boundary data files."""

    police_districts_file: str = "data/boundaries/police_districts.geojson"
    census_tracts_file: str = "data/boundaries/census_tracts_pop.geojson"


@dataclass
class Phase2Config:
    """Complete Phase 2 configuration."""

    version: str = "1.0"
    clustering: ClusteringConfig = field(default_factory=ClusteringConfig)
    severity_weights: Dict[int, float] = field(
        default_factory=lambda: {
            100: 10.0,
            200: 8.0,
            300: 6.0,
            400: 5.0,
            500: 3.0,
            600: 1.0,
            700: 2.0,
            800: 4.0,
            900: 0.5,
        }
    )
    heatmap: HeatmapConfig = field(default_factory=HeatmapConfig)
    census: CensusConfig = field(default_factory=CensusConfig)
    coordinate_bounds: CoordinateBounds = field(default_factory=CoordinateBounds)
    boundaries: BoundaryPaths = field(default_factory=BoundaryPaths)

    @classmethod
    def from_yaml(cls, yaml_path: Path) -> "Phase2Config":
        """Load configuration from YAML file."""
        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)

        config = cls(version=data.get("version", "1.0"))

        # Parse clustering
        if "clustering" in data:
            c = data["clustering"]
            config.clustering = ClusteringConfig(
                eps_degrees=c.get("eps_degrees", 0.002),
                min_samples=c.get("min_samples", 50),
                algorithm=c.get("algorithm", "DBSCAN"),
            )

        # Parse severity weights (convert string keys to int)
        if "severity_weights" in data:
            config.severity_weights = {
                int(k): float(v) for k, v in data["severity_weights"].items()
            }

        # Parse heatmap
        if "heatmap" in data:
            h = data["heatmap"]
            ucr_range = h.get("robbery_ucr_range", [300, 400])
            hours = h.get("hours", [0, 23])
            config.heatmap = HeatmapConfig(
                robbery_ucr_range=tuple(ucr_range),
                hours=tuple(hours),
                days=h.get("days", HeatmapConfig().days),
            )

        # Parse census
        if "census" in data:
            c = data["census"]
            config.census = CensusConfig(
                population_column=c.get("population_column", "total_pop"),
                rate_per=c.get("rate_per", 100000),
                min_population=c.get("min_population", 100),
            )

        # Parse coordinate bounds
        if "coordinate_bounds" in data:
            cb = data["coordinate_bounds"]
            config.coordinate_bounds = CoordinateBounds(
                min_lon=cb.get("min_lon", -75.30),
                max_lon=cb.get("max_lon", -74.95),
                min_lat=cb.get("min_lat", 39.85),
                max_lat=cb.get("max_lat", 40.15),
            )

        # Parse boundaries
        if "boundaries" in data:
            b = data["boundaries"]
            config.boundaries = BoundaryPaths(
                police_districts_file=b.get(
                    "police_districts_file", "data/boundaries/police_districts.geojson"
                ),
                census_tracts_file=b.get(
                    "census_tracts_file", "data/boundaries/census_tracts_pop.geojson"
                ),
            )

        return config


def load_phase2_config(config_path: Path | None = None) -> Phase2Config:
    """Load Phase 2 configuration from default or specified path.

    Parameters
    ----------
    config_path : Path, optional
        Path to configuration YAML file. If None, uses default location.

    Returns
    -------
    Phase2Config
        Loaded configuration dataclass.
    """
    if config_path is None:
        # Default: config/phase2_config.yaml relative to repo root
        repo_root = Path(__file__).resolve().parent.parent
        config_path = repo_root / "config" / "phase2_config.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Phase 2 config not found: {config_path}")

    return Phase2Config.from_yaml(config_path)
