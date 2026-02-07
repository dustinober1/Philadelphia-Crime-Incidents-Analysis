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


# GeoJSON structure validation tests
@pytest.mark.parametrize(
    "endpoint",
    ["/api/v1/spatial/districts", "/api/v1/spatial/tracts", "/api/v1/spatial/hotspots", "/api/v1/spatial/corridors"],
)
def test_spatial_geojson_structure(endpoint: str) -> None:
    """Parametrized test validating GeoJSON FeatureCollection structure for all spatial endpoints."""
    response = client.get(endpoint)

    assert response.status_code == 200
    geojson = response.json()

    # Verify top-level GeoJSON structure
    assert geojson["type"] == "FeatureCollection"
    assert isinstance(geojson["features"], list)

    # Verify each feature has required GeoJSON fields
    for feature in geojson["features"]:
        assert feature["type"] == "Feature"
        assert "geometry" in feature
        assert isinstance(feature["geometry"], dict)
        assert "type" in feature["geometry"]
        assert "coordinates" in feature["geometry"]
        assert "properties" in feature
        assert isinstance(feature["properties"], dict)


def test_spatial_districts_properties() -> None:
    """Validate district features have dist_num property with valid values."""
    response = client.get("/api/v1/spatial/districts")

    assert response.status_code == 200
    geojson = response.json()

    # Verify all district features have dist_num property
    for feature in geojson["features"]:
        properties = feature["properties"]
        assert "dist_num" in properties

        # Verify district numbers are in valid range (1-23)
        dist_num = properties["dist_num"]
        assert isinstance(dist_num, int)
        assert 1 <= dist_num <= 23


def test_spatial_hotspots_centroids() -> None:
    """Validate hotspot features have Point geometry with Philadelphia bounds."""
    # Philadelphia bounds (approximately)
    PHILLY_LON_MIN = -75.3
    PHILLY_LON_MAX = -74.95
    PHILLY_LAT_MIN = 39.85
    PHILLY_LAT_MAX = 40.15

    response = client.get("/api/v1/spatial/hotspots")

    assert response.status_code == 200
    geojson = response.json()

    # Verify all hotspot features have Point geometry
    for feature in geojson["features"]:
        geometry = feature["geometry"]
        assert geometry["type"] == "Point"

        # Verify coordinates are within Philadelphia bounds
        lon, lat = geometry["coordinates"]
        assert PHILLY_LON_MIN <= lon <= PHILLY_LON_MAX
        assert PHILLY_LAT_MIN <= lat <= PHILLY_LAT_MAX

        # Verify intensity property exists
        properties = feature["properties"]
        assert "intensity" in properties
        assert isinstance(properties["intensity"], (int, float))


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


def test_forecasting_time_series_structure() -> None:
    """Test time series forecast has proper structure with confidence intervals."""
    response = client.get("/api/v1/forecasting/time-series")
    assert response.status_code == 200

    payload = response.json()

    # Verify historical data exists
    assert "historical" in payload
    assert isinstance(payload["historical"], list)
    assert len(payload["historical"]) > 0

    # Verify forecast data exists
    forecast = payload["forecast"]
    assert isinstance(forecast, list)
    assert len(forecast) > 0

    # Verify confidence intervals are present in forecast
    first_forecast = forecast[0]
    assert "yhat_lower" in first_forecast
    assert "yhat_upper" in first_forecast

    # Verify confidence intervals are numeric and lower < upper
    assert isinstance(first_forecast["yhat_lower"], (int, float))
    assert isinstance(first_forecast["yhat_upper"], (int, float))
    assert first_forecast["yhat_lower"] <= first_forecast["yhat_upper"]

    # Verify prediction values are numeric
    assert isinstance(first_forecast["yhat"], (int, float))

    # Verify model metadata exists
    assert "model" in payload
    assert isinstance(payload["model"], str)
    assert len(payload["model"]) > 0


def test_forecasting_classification_features() -> None:
    """Test classification features include expected feature names and importance scores."""
    response = client.get("/api/v1/forecasting/classification")
    assert response.status_code == 200

    features = response.json()
    assert isinstance(features, list)
    assert len(features) > 0

    # Verify all features have required fields
    for feature in features:
        assert "feature" in feature
        assert "importance" in feature
        assert isinstance(feature["feature"], str)
        assert isinstance(feature["importance"], (int, float))

    # Verify importance scores are non-negative
    importances = [f["importance"] for f in features]
    assert all(imp >= 0 for imp in importances)

    # Verify temporal coverage - features should include time-based fields
    feature_names = [f["feature"] for f in features]
    time_features = ["year", "month", "day_of_week", "hour"]
    assert any(tf in feature_names for tf in time_features)


# Trends endpoint tests


def test_trends_monthly() -> None:
    """Test GET /api/v1/trends/monthly returns monthly trends data."""
    response = client.get("/api/v1/trends/monthly")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # Verify structure of first row
    row = data[0]
    assert "month" in row
    assert "crime_category" in row
    assert "count" in row


def test_trends_monthly_with_start_year() -> None:
    """Test GET /api/v1/trends/monthly with start_year filter."""
    response = client.get("/api/v1/trends/monthly?start_year=2019")
    assert response.status_code == 200
    data = response.json()

    # Verify all months are from 2019 onwards
    for row in data:
        year = int(row["month"][:4])
        assert year >= 2019


def test_trends_monthly_with_end_year() -> None:
    """Test GET /api/v1/trends/monthly with end_year filter."""
    response = client.get("/api/v1/trends/monthly?end_year=2020")
    assert response.status_code == 200
    data = response.json()

    # Verify all months are through 2020
    for row in data:
        year = int(row["month"][:4])
        assert year <= 2020


def test_trends_monthly_with_year_range() -> None:
    """Test GET /api/v1/trends/monthly with both start_year and end_year."""
    response = client.get("/api/v1/trends/monthly?start_year=2018&end_year=2020")
    assert response.status_code == 200
    data = response.json()

    # Verify all months are within range
    for row in data:
        year = int(row["month"][:4])
        assert 2018 <= year <= 2020


def test_trends_covid() -> None:
    """Test GET /api/v1/trends/covid returns COVID comparison data."""
    response = client.get("/api/v1/trends/covid")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # Verify structure
    row = data[0]
    assert "period" in row
    assert "start" in row
    assert "end" in row
    assert "count" in row


def test_trends_seasonality() -> None:
    """Test GET /api/v1/trends/seasonality returns seasonality data."""
    response = client.get("/api/v1/trends/seasonality")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)

    # Verify expected keys exist
    assert "by_month" in data
    assert "by_day_of_week" in data
    assert "by_hour" in data


def test_trends_robbery_heatmap() -> None:
    """Test GET /api/v1/trends/robbery-heatmap returns robbery heatmap data."""
    response = client.get("/api/v1/trends/robbery-heatmap")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # Verify structure has hour and day_of_week
    row = data[0]
    assert "hour" in row
    assert "day_of_week" in row
    assert "count" in row
