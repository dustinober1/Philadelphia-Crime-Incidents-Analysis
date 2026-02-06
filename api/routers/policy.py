"""Policy analysis endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from api.services.data_loader import get_data

router = APIRouter(prefix="/policy", tags=["policy"])


@router.get("/retail-theft")
def retail_theft() -> list[dict]:
    return get_data("retail_theft_trend.json")


@router.get("/vehicle-crimes")
def vehicle_crimes() -> list[dict]:
    return get_data("vehicle_crime_trend.json")


@router.get("/composition")
def composition() -> list[dict]:
    return get_data("crime_composition.json")


@router.get("/events")
def events() -> list[dict]:
    return get_data("event_impact.json")
