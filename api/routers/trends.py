"""Trend and seasonality endpoints."""

from __future__ import annotations

from typing import Any, cast

from fastapi import APIRouter, Query

from api.services.data_loader import get_data

router = APIRouter(prefix="/trends", tags=["trends"])


@router.get("/annual")
def annual(
    category: str | None = Query(default=None),
    district: int | None = Query(default=None, ge=1, le=23, description="PPD district number (1-23)"),
) -> list[dict[str, Any]]:
    # If district is specified, use district-scoped data
    if district is not None:
        data = cast(list[dict[str, Any]], get_data("annual_trends_district.json"))
        data = [row for row in data if row.get("dc_dist") == district]
    else:
        data = cast(list[dict[str, Any]], get_data("annual_trends.json"))

    if category:
        data = [row for row in data if row.get("crime_category") == category]
    return data


@router.get("/monthly")
def monthly(
    start_year: int | None = None,
    end_year: int | None = None,
    district: int | None = Query(default=None, ge=1, le=23, description="PPD district number (1-23)"),
) -> list[dict[str, Any]]:
    # If district is specified, use district-scoped data
    if district is not None:
        data = cast(list[dict[str, Any]], get_data("monthly_trends_district.json"))
        data = [row for row in data if row.get("dc_dist") == district]
    else:
        data = cast(list[dict[str, Any]], get_data("monthly_trends.json"))

    def _year(value: str) -> int:
        return int(value[:4])

    if start_year is not None:
        data = [row for row in data if _year(row["month"]) >= start_year]
    if end_year is not None:
        data = [row for row in data if _year(row["month"]) <= end_year]
    return data


@router.get("/covid")
def covid() -> list[dict[str, Any]]:
    return cast(list[dict[str, Any]], get_data("covid_comparison.json"))


@router.get("/seasonality")
def seasonality() -> dict[str, Any]:
    return cast(dict[str, Any], get_data("seasonality.json"))


@router.get("/robbery-heatmap")
def robbery_heatmap() -> list[dict[str, Any]]:
    return cast(list[dict[str, Any]], get_data("robbery_heatmap.json"))
