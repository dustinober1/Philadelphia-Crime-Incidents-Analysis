"""Metadata endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from api.services.data_loader import get_data

router = APIRouter(tags=["metadata"])


@router.get("/metadata")
def metadata() -> dict:
    return get_data("metadata.json")
