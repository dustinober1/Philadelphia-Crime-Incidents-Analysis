"""Export pre-aggregated crime analysis data for the web API."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import typer

from analysis.config import COLORS
from analysis.data.loading import load_crime_data
from analysis.data.preprocessing import aggregate_by_period
from analysis.utils.classification import classify_crime_category
from analysis.utils.temporal import extract_temporal_features

try:
    import geopandas as gpd

    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False

try:
    from prophet import Prophet

    HAS_PROPHET = True
except ImportError:
    HAS_PROPHET = False

try:
    from sklearn.ensemble import RandomForestClassifier

    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

app = typer.Typer(help="Export analysis outputs as API-ready JSON/GeoJSON")


@dataclass
class ExportMetadata:
    total_incidents: int
    date_start: str
    date_end: str
    last_updated: str
    source: str
    colors: dict[str, str]


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _to_records(df: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in df.to_dict(orient="records"):
        clean: dict[str, Any] = {}
        for key, value in row.items():
            if hasattr(value, "isoformat"):
                clean[key] = value.isoformat()
            elif isinstance(value, (int, float, str, bool)) or value is None:
                clean[key] = value
            else:
                clean[key] = str(value)
        rows.append(clean)
    return rows


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _group_size_to_records_frame(grouped: Any, count_name: str = "count") -> Any:
    sized = grouped.size()
    return sized.rename(count_name).reset_index()


def _export_trends(df: Any, output_dir: Path) -> None:
    categorized = classify_crime_category(df)
    categorized["dispatch_date"] = categorized["dispatch_date"].astype("datetime64[ns]")
    categorized = extract_temporal_features(categorized)

    annual = _group_size_to_records_frame(
        categorized.groupby(["year", "crime_category"], observed=False)
    ).sort_values(["year", "crime_category"])
    _write_json(output_dir / "annual_trends.json", _to_records(annual))

    monthly = _group_size_to_records_frame(
        categorized.assign(
            month=categorized["dispatch_date"].dt.to_period("M").dt.to_timestamp()
        ).groupby(["month", "crime_category"], observed=False)
    ).sort_values(["month", "crime_category"])
    _write_json(output_dir / "monthly_trends.json", _to_records(monthly))

    # District-scoped annual trends (includes dc_dist)
    annual_district = _group_size_to_records_frame(
        categorized.groupby(["year", "crime_category", "dc_dist"], observed=False)
    ).sort_values(["year", "crime_category", "dc_dist"])
    _write_json(output_dir / "annual_trends_district.json", _to_records(annual_district))

    # District-scoped monthly trends (includes dc_dist)
    monthly_district = _group_size_to_records_frame(
        categorized.assign(
            month=categorized["dispatch_date"].dt.to_period("M").dt.to_timestamp()
        ).groupby(["month", "crime_category", "dc_dist"], observed=False)
    ).sort_values(["month", "crime_category", "dc_dist"])
    _write_json(output_dir / "monthly_trends_district.json", _to_records(monthly_district))

    pre = categorized[categorized["dispatch_date"] < "2020-03-01"]
    during = categorized[
        (categorized["dispatch_date"] >= "2020-03-01")
        & (categorized["dispatch_date"] < "2022-01-01")
    ]
    post = categorized[categorized["dispatch_date"] >= "2022-01-01"]

    covid = [
        {"period": "Pre", "start": "2006-01-01", "end": "2020-02-29", "count": int(len(pre))},
        {
            "period": "During",
            "start": "2020-03-01",
            "end": "2021-12-31",
            "count": int(len(during)),
        },
        {"period": "Post", "start": "2022-01-01", "end": "present", "count": int(len(post))},
    ]
    _write_json(output_dir / "covid_comparison.json", covid)


def _export_seasonality(df: Any, output_dir: Path) -> None:
    temporal = extract_temporal_features(df)
    temporal["dispatch_date"] = temporal["dispatch_date"].astype("datetime64[ns]")
    temporal["hour"] = temporal["hour"].fillna(0).astype(int)

    month_counts = _group_size_to_records_frame(temporal.groupby("month", observed=False))
    dow_counts = _group_size_to_records_frame(temporal.groupby("day_of_week", observed=False))
    hour_counts = _group_size_to_records_frame(temporal.groupby("hour", observed=False))

    seasonality = {
        "by_month": _to_records(month_counts.sort_values("month")),
        "by_day_of_week": _to_records(dow_counts.sort_values("day_of_week")),
        "by_hour": _to_records(hour_counts.sort_values("hour")),
    }
    _write_json(output_dir / "seasonality.json", seasonality)

    robbery = temporal[(temporal["ucr_general"] >= 300) & (temporal["ucr_general"] < 400)]
    robbery_matrix = _group_size_to_records_frame(
        robbery.groupby(["hour", "day_of_week"], observed=False)
    ).sort_values(["hour", "day_of_week"])
    _write_json(output_dir / "robbery_heatmap.json", _to_records(robbery_matrix))


def _export_spatial(df: Any, output_dir: Path, geo_dir: Path, repo_root: Path) -> None:
    _ensure_dir(geo_dir)
    if not HAS_GEOPANDAS:
        return

    district_path = repo_root / "data" / "boundaries" / "police_districts.geojson"
    tracts_path = repo_root / "data" / "boundaries" / "census_tracts_pop.geojson"
    hotspot_path = repo_root / "reports" / "hotspot_centroids.geojson"
    corridor_path = repo_root / "data" / "boundaries" / "corridors.geojson"

    districts = gpd.read_file(district_path)
    severity = _group_size_to_records_frame(
        df.groupby("dc_dist", observed=False),
        count_name="total_incidents",
    )
    severity["severity_score"] = (
        severity["total_incidents"] / severity["total_incidents"].max() * 100
    )
    severity["dc_dist"] = severity["dc_dist"].astype(str)

    join_key = "dist_num" if "dist_num" in districts.columns else "dist_numc"
    districts[join_key] = districts[join_key].astype(str)
    districts = districts.merge(
        severity[["dc_dist", "severity_score", "total_incidents"]],
        left_on=join_key,
        right_on="dc_dist",
        how="left",
    )
    districts["severity_score"] = districts["severity_score"].fillna(0.0)
    districts["total_incidents"] = districts["total_incidents"].fillna(0).astype(int)
    districts.to_file(geo_dir / "districts.geojson", driver="GeoJSON")

    tracts = gpd.read_file(tracts_path)
    clean = df.dropna(subset=["point_x", "point_y"]).copy()
    clean = clean[
        (clean["point_x"].between(-75.30, -74.95)) & (clean["point_y"].between(39.85, 40.15))
    ]
    if not clean.empty:
        points = gpd.GeoDataFrame(
            clean,
            geometry=gpd.points_from_xy(clean["point_x"], clean["point_y"]),
            crs="EPSG:4326",
        )
        if tracts.crs != points.crs:
            tracts = tracts.to_crs(points.crs)
        joined = gpd.sjoin(
            points, tracts[["GEOID", "total_pop", "geometry"]], how="left", predicate="within"
        )
        rate = _group_size_to_records_frame(
            joined.groupby("GEOID", observed=False),
            count_name="crime_count",
        ).merge(tracts[["GEOID", "total_pop"]].drop_duplicates(), on="GEOID", how="left")
        rate["crime_rate"] = (rate["crime_count"] / rate["total_pop"].clip(lower=1)) * 100000
        tracts = tracts.merge(rate[["GEOID", "crime_count", "crime_rate"]], on="GEOID", how="left")
    tracts["crime_count"] = tracts.get("crime_count", 0).fillna(0).astype(int)
    tracts["crime_rate"] = tracts.get("crime_rate", 0.0).fillna(0.0)
    tracts.to_file(geo_dir / "tracts.geojson", driver="GeoJSON")

    hotspots = gpd.read_file(hotspot_path)
    hotspots.to_file(geo_dir / "hotspot_centroids.geojson", driver="GeoJSON")

    corridors = gpd.read_file(corridor_path)
    corridors.to_file(geo_dir / "corridors.geojson", driver="GeoJSON")

    _write_json(
        output_dir / "spatial_summary.json",
        {
            "districts": int(len(districts)),
            "tracts": int(len(tracts)),
            "hotspots": int(len(hotspots)),
            "corridors": int(len(corridors)),
        },
    )


def _export_policy(df: Any, output_dir: Path, repo_root: Path) -> None:
    work = extract_temporal_features(df)
    work = classify_crime_category(work)
    work["dispatch_date"] = work["dispatch_date"].astype("datetime64[ns]")

    retail = work[(work["ucr_general"] >= 600) & (work["ucr_general"] < 700)]
    retail_monthly = _group_size_to_records_frame(
        retail.assign(month=retail["dispatch_date"].dt.to_period("M").dt.to_timestamp()).groupby(
            "month", observed=False
        )
    )
    _write_json(
        output_dir / "retail_theft_trend.json", _to_records(retail_monthly.sort_values("month"))
    )

    vehicle = work[(work["ucr_general"] >= 700) & (work["ucr_general"] < 800)]
    vehicle_monthly = _group_size_to_records_frame(
        vehicle.assign(month=vehicle["dispatch_date"].dt.to_period("M").dt.to_timestamp()).groupby(
            "month", observed=False
        )
    )
    _write_json(
        output_dir / "vehicle_crime_trend.json", _to_records(vehicle_monthly.sort_values("month"))
    )

    composition = _group_size_to_records_frame(
        work.groupby(["year", "crime_category"], observed=False)
    ).sort_values(["year", "crime_category"])
    _write_json(output_dir / "crime_composition.json", _to_records(composition))

    event_file = repo_root / "reports" / "event_impact_results.csv"
    if event_file.exists():
        import pandas as pd

        event_df = pd.read_csv(event_file)
        _write_json(output_dir / "event_impact.json", _to_records(event_df))
    else:
        _write_json(output_dir / "event_impact.json", [])


def _export_forecasting(df: Any, output_dir: Path) -> None:
    monthly = aggregate_by_period(df, period="ME", count_col="objectid", date_col="dispatch_date")
    monthly = monthly.rename(columns={"dispatch_date": "ds", "count": "y"})

    forecast_payload: dict[str, Any]
    if HAS_PROPHET:
        model = Prophet()
        model.fit(monthly, seed=42)
        future = model.make_future_dataframe(periods=24, freq="ME")
        pred = model.predict(future)[["ds", "yhat", "yhat_lower", "yhat_upper"]]
        pred_records = _to_records(pred)
        historical_records = _to_records(monthly)
        forecast_payload = {
            "historical": historical_records,
            "forecast": pred_records,
            "model": "Prophet",
        }
    else:
        last = monthly.tail(24).copy()
        slope = (last["y"].iloc[-1] - last["y"].iloc[0]) / max(len(last) - 1, 1)
        base_date = monthly["ds"].max()
        forecast_rows = []
        for i in range(1, 25):
            dt = (base_date + __import__("pandas").DateOffset(months=i)).to_pydatetime()
            pred = float(last["y"].iloc[-1] + slope * i)
            forecast_rows.append(
                {
                    "ds": dt.isoformat(),
                    "yhat": pred,
                    "yhat_lower": pred * 0.9,
                    "yhat_upper": pred * 1.1,
                }
            )
        forecast_payload = {
            "historical": _to_records(monthly),
            "forecast": forecast_rows,
            "model": "LinearFallback",
        }

    _write_json(output_dir / "forecast.json", forecast_payload)

    classified = classify_crime_category(extract_temporal_features(df))
    classified["is_violent"] = (classified["crime_category"] == "Violent").astype(int)
    classified["hour"] = classified["hour"].fillna(0)

    if HAS_SKLEARN:
        features = classified[["year", "month", "day_of_week", "hour"]].fillna(0)
        target = classified["is_violent"]
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(features, target)
        importances = [
            {"feature": name, "importance": float(value)}
            for name, value in zip(
                features.columns.tolist(), model.feature_importances_, strict=False
            )
        ]
    else:
        importances = [
            {"feature": "year", "importance": 0.25},
            {"feature": "month", "importance": 0.25},
            {"feature": "day_of_week", "importance": 0.25},
            {"feature": "hour", "importance": 0.25},
        ]

    _write_json(output_dir / "classification_features.json", importances)


def _export_metadata(df: Any, output_dir: Path) -> None:
    dates = df["dispatch_date"].astype("datetime64[ns]")
    latest = dates.max()
    if hasattr(latest, "to_pydatetime"):
        latest_dt = latest.to_pydatetime().replace(tzinfo=UTC)
    else:
        latest_dt = datetime.now(UTC)
    metadata = ExportMetadata(
        total_incidents=int(len(df)),
        date_start=dates.min().date().isoformat(),
        date_end=dates.max().date().isoformat(),
        last_updated=latest_dt.isoformat(),
        source="Philadelphia Police Department via OpenDataPhilly",
        colors=COLORS,
    )
    _write_json(output_dir / "metadata.json", asdict(metadata))


def export_all(output_dir: Path) -> Path:
    """Generate all API data exports and return the resolved output path."""
    repo_root = Path(__file__).resolve().parent.parent
    output_dir = output_dir if output_dir.is_absolute() else (repo_root / output_dir)
    geo_dir = output_dir / "geo"
    _ensure_dir(output_dir)
    _ensure_dir(geo_dir)

    df = load_crime_data(clean=True)
    if "dispatch_date" in df.columns:
        import pandas as pd

        df["dispatch_date"] = pd.to_datetime(df["dispatch_date"], errors="coerce")
        df = df.dropna(subset=["dispatch_date"])

    _export_trends(df, output_dir)
    _export_seasonality(df, output_dir)
    _export_spatial(df, output_dir, geo_dir, repo_root)
    _export_policy(df, output_dir, repo_root)
    _export_forecasting(df, output_dir)
    _export_metadata(df, output_dir)

    return output_dir


@app.command()
def run(
    output_dir: Path = typer.Option(Path("api/data"), help="Output directory for exports")
) -> None:
    """Generate all API data exports."""
    resolved_output = export_all(output_dir)
    typer.echo(f"Export complete: {resolved_output}")


if __name__ == "__main__":
    app()
