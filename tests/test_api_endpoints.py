"""FastAPI endpoint smoke tests for web conversion API."""

import pytest
from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from api.main import app
from api.routers import questions
from api.services.data_loader import load_all_data

client = TestClient(app)


def setup_module() -> None:
    load_all_data()


def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_trends_annual() -> None:
    response = client.get("/api/v1/trends/annual")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_metadata() -> None:
    response = client.get("/api/v1/metadata")
    assert response.status_code == 200
    payload = response.json()
    assert "last_updated" in payload
    assert "total_incidents" in payload


def _submit_question() -> str:
    response = client.post(
        "/api/v1/questions",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "question_text": "How have theft patterns changed?",
            "honeypot": "",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    return str(payload["id"])


def _reset_questions_state() -> None:
    questions._IN_MEMORY.clear()
    questions._RATE_LIMIT.clear()


def test_questions_pending_requires_admin_auth(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("ADMIN_PASSWORD", "test-password")
    monkeypatch.setenv("ADMIN_TOKEN_SECRET", "test-token-secret")
    _reset_questions_state()
    _submit_question()

    response = client.get("/api/v1/questions?status=pending")
    assert response.status_code == 401
    assert response.json()["message"] == "Missing admin token"


def test_admin_session_and_pending_listing(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("ADMIN_PASSWORD", "test-password")
    monkeypatch.setenv("ADMIN_TOKEN_SECRET", "test-token-secret")
    _reset_questions_state()
    question_id = _submit_question()

    login = client.post("/api/v1/questions/admin/session", json={"password": "test-password"})
    assert login.status_code == 200
    token = login.json()["token"]
    assert token

    pending = client.get(
        "/api/v1/questions?status=pending",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert pending.status_code == 200
    pending_ids = {item["id"] for item in pending.json()}
    assert question_id in pending_ids


def test_admin_update_requires_auth(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("ADMIN_PASSWORD", "test-password")
    monkeypatch.setenv("ADMIN_TOKEN_SECRET", "test-token-secret")
    _reset_questions_state()
    question_id = _submit_question()

    response = client.patch(
        f"/api/v1/questions/{question_id}",
        json={"answer_text": "Answer", "status": "answered"},
    )
    assert response.status_code == 401
    assert response.json()["message"] == "Missing admin token"


def test_error_payload_shape_for_http_errors() -> None:
    response = client.get("/api/v1/questions?status=invalid")
    assert response.status_code == 422
    payload = response.json()
    assert payload["error"] == "http_error"
    assert "status must be answered or pending" in payload["message"]


# Spatial endpoint tests
def test_spatial_districts() -> None:
    """Test GET /api/v1/spatial/districts returns valid GeoJSON."""
    response = client.get("/api/v1/spatial/districts")

    assert response.status_code == 200
    geojson = response.json()

    # Verify GeoJSON structure
    assert isinstance(geojson, dict)
    assert geojson.get("type") == "FeatureCollection"
    assert "features" in geojson
    assert isinstance(geojson["features"], list)

    # Verify feature structure
    if len(geojson["features"]) > 0:
        feature = geojson["features"][0]
        assert "geometry" in feature
        assert "properties" in feature
        assert feature.get("type") == "Feature"


def test_spatial_tracts() -> None:
    """Test GET /api/v1/spatial/tracts returns valid GeoJSON."""
    response = client.get("/api/v1/spatial/tracts")

    assert response.status_code == 200
    geojson = response.json()

    # Verify GeoJSON FeatureCollection structure
    assert geojson.get("type") == "FeatureCollection"
    assert isinstance(geojson.get("features"), list)

    # Verify features have Polygon or MultiPolygon geometry
    if len(geojson["features"]) > 0:
        feature = geojson["features"][0]
        geometry = feature.get("geometry", {})
        geom_type = geometry.get("type")
        assert geom_type in {"Polygon", "MultiPolygon"}


def test_spatial_hotspots() -> None:
    """Test GET /api/v1/spatial/hotspots returns valid GeoJSON."""
    response = client.get("/api/v1/spatial/hotspots")

    assert response.status_code == 200
    geojson = response.json()

    # Verify GeoJSON FeatureCollection structure
    assert geojson.get("type") == "FeatureCollection"
    assert isinstance(geojson.get("features"), list)

    # Verify features have Point geometry (hotspot centroids)
    if len(geojson["features"]) > 0:
        feature = geojson["features"][0]
        geometry = feature.get("geometry", {})
        assert geometry.get("type") == "Point"
        assert "coordinates" in geometry


def test_spatial_corridors() -> None:
    """Test GET /api/v1/spatial/corridors returns valid GeoJSON."""
    response = client.get("/api/v1/spatial/corridors")

    assert response.status_code == 200
    geojson = response.json()

    # Verify GeoJSON FeatureCollection structure
    assert geojson.get("type") == "FeatureCollection"
    assert isinstance(geojson.get("features"), list)

    # Verify features have LineString or MultiLineString geometry
    if len(geojson["features"]) > 0:
        feature = geojson["features"][0]
        geometry = feature.get("geometry", {})
        geom_type = geometry.get("type")
        assert geom_type in {"LineString", "MultiLineString"}


# Forecasting endpoint tests


def test_forecasting_time_series() -> None:
    """Test GET /api/v1/forecasting/time-series returns valid forecast data."""
    response = client.get("/api/v1/forecasting/time-series")
    assert response.status_code == 200

    payload = response.json()
    assert isinstance(payload, dict)

    # Verify expected top-level keys exist
    assert "historical" in payload
    assert "forecast" in payload
    assert "model" in payload

    # Verify forecast data is a list
    assert isinstance(payload["forecast"], list)
    assert len(payload["forecast"]) > 0

    # Verify forecast items have date/value structure with confidence intervals
    first_forecast = payload["forecast"][0]
    assert "ds" in first_forecast  # date field
    assert "yhat" in first_forecast  # prediction
    assert "yhat_lower" in first_forecast  # lower confidence bound
    assert "yhat_upper" in first_forecast  # upper confidence bound


def test_forecasting_classification() -> None:
    """Test GET /api/v1/forecasting/classification returns feature importance data."""
    response = client.get("/api/v1/forecasting/classification")
    assert response.status_code == 200

    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) > 0

    # Verify each row has feature and importance fields
    first_feature = payload[0]
    assert "feature" in first_feature
    assert "importance" in first_feature

    # Verify importance is a numeric value
    assert isinstance(first_feature["importance"], (int, float))
