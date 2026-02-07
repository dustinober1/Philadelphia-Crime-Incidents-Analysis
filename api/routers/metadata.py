"""Metadata endpoint."""

from __future__ import annotations

from typing import Any, cast

from fastapi import APIRouter

from api.services.data_loader import get_data

router = APIRouter(tags=["metadata"])


@router.get("/metadata")
def metadata() -> dict[str, Any]:
    return cast(dict[str, Any], get_data("metadata.json"))
