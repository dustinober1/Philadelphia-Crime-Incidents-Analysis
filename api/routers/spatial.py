"""Spatial GeoJSON endpoints."""

from __future__ import annotations

from typing import Any, cast

from fastapi import APIRouter

from api.services.data_loader import get_data

router = APIRouter(prefix="/spatial", tags=["spatial"])


@router.get("/districts")
def districts() -> dict[str, Any]:
    return cast(dict[str, Any], get_data("geo/districts.geojson"))


@router.get("/tracts")
def tracts() -> dict[str, Any]:
    return cast(dict[str, Any], get_data("geo/tracts.geojson"))


@router.get("/hotspots")
def hotspots() -> dict[str, Any]:
    return cast(dict[str, Any], get_data("geo/hotspot_centroids.geojson"))


@router.get("/corridors")
def corridors() -> dict[str, Any]:
    return cast(dict[str, Any], get_data("geo/corridors.geojson"))
