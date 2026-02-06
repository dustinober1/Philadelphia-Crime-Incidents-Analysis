"""Spatial GeoJSON endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from api.services.data_loader import get_data

router = APIRouter(prefix="/spatial", tags=["spatial"])


@router.get("/districts")
def districts() -> dict:
    return get_data("geo/districts.geojson")


@router.get("/tracts")
def tracts() -> dict:
    return get_data("geo/tracts.geojson")


@router.get("/hotspots")
def hotspots() -> dict:
    return get_data("geo/hotspot_centroids.geojson")


@router.get("/corridors")
def corridors() -> dict:
    return get_data("geo/corridors.geojson")
