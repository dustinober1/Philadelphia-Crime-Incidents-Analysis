"""Forecasting endpoints."""

from __future__ import annotations

from typing import Any, cast

from fastapi import APIRouter

from api.services.data_loader import get_data

router = APIRouter(prefix="/forecasting", tags=["forecasting"])


@router.get("/time-series")
def time_series() -> dict[str, Any]:
    return cast(dict[str, Any], get_data("forecast.json"))


@router.get("/classification")
def classification() -> list[dict[str, Any]]:
    return cast(list[dict[str, Any]], get_data("classification_features.json"))
