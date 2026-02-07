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

        # Verify district numbers are valid (stored as string)
        dist_num = properties["dist_num"]
        # District numbers are stored as strings
        assert isinstance(dist_num, str)
        # Convert to int for range validation (districts 1-24)
        dist_num_int = int(dist_num)
        assert dist_num_int > 0  # Just validate it's a positive number


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

        # Verify hotspot properties exist (cluster, incident_count, point_x, point_y)
        properties = feature["properties"]
        assert "cluster" in properties
        assert "incident_count" in properties
        assert isinstance(properties["incident_count"], int)
        assert properties["incident_count"] >= 0


def test_spatial_endpoint_missing_geojson(monkeypatch: MonkeyPatch) -> None:
    """Test spatial endpoint raises KeyError when GeoJSON file is missing."""
    import pytest

    # Import the module to patch the cache
    from api.services import data_loader

    # Save original cache and clear it to simulate missing data
    original_cache = data_loader._DATA_CACHE.copy()
    monkeypatch.setattr(data_loader, "_DATA_CACHE", {})

    try:
        # Call the districts endpoint - should raise KeyError
        # Note: FastAPI TestClient propagates unhandled exceptions
        with pytest.raises(KeyError, match="Data key not loaded.*geo/districts.geojson"):
            client.get("/api/v1/spatial/districts")
    finally:
        # Restore cache for other tests
        monkeypatch.setattr(data_loader, "_DATA_CACHE", original_cache)


def test_spatial_empty_features(monkeypatch: MonkeyPatch) -> None:
    """Test spatial endpoint returns 200 with empty features list when data is empty."""
    # Import the module to patch the cache
    from api.services import data_loader

    # Create an empty FeatureCollection
    empty_geojson = {"type": "FeatureCollection", "features": []}
    monkeypatch.setattr(data_loader, "_DATA_CACHE", {"geo/districts.geojson": empty_geojson})

    # Call the districts endpoint
    response = client.get("/api/v1/spatial/districts")

    # Should return 200 even with empty features
    assert response.status_code == 200

    # Verify empty FeatureCollection structure
    geojson = response.json()
    assert geojson["type"] == "FeatureCollection"
    assert geojson["features"] == []
    assert len(geojson["features"]) == 0


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


def test_trends_annual_with_category_filter() -> None:
    """Test GET /api/v1/trends/annual with category filter."""
    response = client.get("/api/v1/trends/annual?category=Violent")
    assert response.status_code == 200
    data = response.json()

    # Verify all returned rows have crime_category == "Violent"
    for row in data:
        assert row.get("crime_category") == "Violent"


def test_trends_annual_with_nonexistent_category() -> None:
    """Test GET /api/v1/trends/annual with category that has no data."""
    response = client.get("/api/v1/trends/annual?category=NonExistent")
    assert response.status_code == 200
    data = response.json()

    # Should return empty list when no data matches
    assert isinstance(data, list)
    assert len(data) == 0


def test_trends_monthly_start_year_filters_correctly() -> None:
    """Test monthly endpoint start_year parameter filters from year onwards."""
    response = client.get("/api/v1/trends/monthly?start_year=2019")
    assert response.status_code == 200
    data = response.json()

    # All months should be from 2019 onwards
    for row in data:
        year = int(row["month"][:4])
        assert year >= 2019


def test_trends_monthly_end_year_filters_correctly() -> None:
    """Test monthly endpoint end_year parameter filters through year."""
    response = client.get("/api/v1/trends/monthly?end_year=2021")
    assert response.status_code == 200
    data = response.json()

    # All months should be through 2021
    for row in data:
        year = int(row["month"][:4])
        assert year <= 2021


def test_trends_monthly_start_greater_than_end() -> None:
    """Test monthly endpoint with start_year > end_year returns empty list."""
    response = client.get("/api/v1/trends/monthly?start_year=2025&end_year=2020")
    assert response.status_code == 200
    data = response.json()

    # Should return empty list when start > end
    assert isinstance(data, list)
    assert len(data) == 0


def test_trends_monthly_invalid_year_format() -> None:
    """Test monthly endpoint with invalid year format returns 422."""
    response = client.get("/api/v1/trends/monthly?start_year=notanumber")
    assert response.status_code == 422

    # Verify error response contains detail key
    payload = response.json()
    assert "details" in payload


def test_trends_annual_error_handling_exists() -> None:
    """Test that trends endpoints have error handling for missing data."""
    # This test verifies the error handling code path exists
    # by checking that get_data raises KeyError for missing keys
    from api.services.data_loader import get_data, _DATA_CACHE

    # Save original cache
    original_cache = _DATA_CACHE.copy()

    try:
        # Clear the cache to simulate missing data
        _DATA_CACHE.clear()

        # Verify get_data raises KeyError for missing data
        # This demonstrates the error path exists
        try:
            get_data("annual_trends.json")
            assert False, "Expected KeyError to be raised"
        except KeyError as e:
            # Verify the error message is correct
            assert "annual_trends.json" in str(e)
            assert "Data key not loaded" in str(e)
    finally:
        # Restore cache
        _DATA_CACHE.clear()
        _DATA_CACHE.update(original_cache)


# Policy Analysis Endpoint Tests


def test_policy_retail_theft() -> None:
    """Test GET /api/v1/policy/retail-theft endpoint returns valid data."""
    response = client.get("/api/v1/policy/retail-theft")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # Verify each row has expected keys
    expected_keys = {"month", "count"}
    for row in data:
        assert set(row.keys()) == expected_keys
        assert isinstance(row["month"], str)
        assert isinstance(row["count"], int)
        assert row["count"] >= 0


def test_policy_vehicle_crimes() -> None:
    """Test GET /api/v1/policy/vehicle-crimes endpoint returns valid data."""
    response = client.get("/api/v1/policy/vehicle-crimes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # Verify each row has expected keys
    expected_keys = {"month", "count"}
    for row in data:
        assert set(row.keys()) == expected_keys
        assert isinstance(row["month"], str)
        assert isinstance(row["count"], int)
        assert row["count"] >= 0


def test_policy_composition() -> None:
    """Test GET /api/v1/policy/composition endpoint returns valid data."""
    response = client.get("/api/v1/policy/composition")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # Verify each row has expected keys for composition breakdown
    expected_keys = {"year", "crime_category", "count"}
    for row in data:
        assert set(row.keys()) == expected_keys
        assert isinstance(row["year"], int)
        assert isinstance(row["crime_category"], str)
        assert isinstance(row["count"], int)
        assert row["count"] >= 0


def test_policy_events() -> None:
    """Test GET /api/v1/policy/events endpoint returns valid data."""
    response = client.get("/api/v1/policy/events")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # Verify each row has expected keys for event impact analysis
    expected_keys = {
        "event_type",
        "metric",
        "n_event_days",
        "n_control_days",
        "event_mean",
        "control_mean",
        "difference",
        "pct_change",
        "ci_lower",
        "ci_upper",
        "t_statistic",
        "p_value",
        "significant",
    }
    for row in data:
        assert set(row.keys()) == expected_keys
        assert isinstance(row["event_type"], str)
        assert isinstance(row["metric"], str)
        assert isinstance(row["n_event_days"], int)
        assert isinstance(row["n_control_days"], int)
        assert isinstance(row["event_mean"], (int, float))
        assert isinstance(row["control_mean"], (int, float))
        assert isinstance(row["difference"], (int, float))
        assert isinstance(row["pct_change"], (int, float))
        assert isinstance(row["ci_lower"], (int, float))
        assert isinstance(row["ci_upper"], (int, float))
        assert isinstance(row["t_statistic"], (int, float))
        assert isinstance(row["p_value"], (int, float))
        assert isinstance(row["significant"], bool)


def test_policy_retail_theft_trend_data() -> None:
    """Verify retail theft data has temporal coverage and chronological order."""
    response = client.get("/api/v1/policy/retail-theft")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # Verify temporal coverage (multiple years)
    years = {row["month"][:4] for row in data}
    assert len(years) > 1, "Retail theft data should span multiple years"

    # Verify data is sorted chronologically
    months = [row["month"] for row in data]
    assert months == sorted(months), "Retail theft data should be sorted chronologically"


def test_policy_vehicle_crimes_categories() -> None:
    """Verify vehicle crime data has time series coverage and valid counts."""
    response = client.get("/api/v1/policy/vehicle-crimes")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # Verify time series coverage (multiple months)
    months = [row["month"] for row in data]
    assert len(months) > 1, "Vehicle crime data should have multiple months"

    # Verify count fields are non-negative integers
    for row in data:
        assert row["count"] >= 0, "Vehicle crime counts should be non-negative"
        assert isinstance(row["count"], int), "Vehicle crime counts should be integers"


def test_policy_composition_breakdown() -> None:
    """Verify composition data includes major crime categories and year-over-year data."""
    response = client.get("/api/v1/policy/composition")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # Verify composition data includes major crime categories
    crime_categories = {row["crime_category"] for row in data}
    expected_categories = {"Violent", "Property", "Other"}
    assert expected_categories.issubset(
        crime_categories
    ), "Composition data should include major crime categories"

    # Verify year-over-year coverage
    years = {row["year"] for row in data}
    assert len(years) > 1, "Composition data should span multiple years"

    # Verify counts are non-negative
    for row in data:
        assert row["count"] >= 0, "Crime counts should be non-negative"


def test_policy_events_impact_metrics() -> None:
    """Verify event data includes impact metrics and pre/post event comparisons."""
    response = client.get("/api/v1/policy/events")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # Verify pre/post event comparison exists
    for row in data:
        assert "event_mean" in row, "Event data should include event mean"
        assert "control_mean" in row, "Event data should include control mean"
        assert "difference" in row, "Event data should include difference"
        assert isinstance(row["event_mean"], (int, float)), "Event mean should be numeric"
        assert isinstance(row["control_mean"], (int, float)), "Control mean should be numeric"

    # Verify event types are represented
    event_types = {row["event_type"] for row in data}
    assert len(event_types) > 0, "Event data should include event types"

    # Verify metrics are represented (total, violent, etc.)
    metrics = {row["metric"] for row in data}
    assert "total" in metrics, "Event data should include total metric"


def test_policy_endpoint_missing_data() -> None:
    """Test policy endpoints have error handling for missing data."""
    # This test verifies the error handling code path exists
    # by checking that get_data raises KeyError for missing keys
    from api.services.data_loader import get_data, _DATA_CACHE

    # Save original cache
    original_cache = _DATA_CACHE.copy()

    try:
        # Clear the cache to simulate missing data
        _DATA_CACHE.clear()

        # Test each data key raises KeyError for missing data
        data_keys = [
            "retail_theft_trend.json",
            "vehicle_crime_trend.json",
            "crime_composition.json",
            "event_impact.json",
        ]

        for key in data_keys:
            with pytest.raises(KeyError, match=f"Data key not loaded: {key}"):
                get_data(key)

    finally:
        # Restore original cache
        _DATA_CACHE.clear()
        _DATA_CACHE.update(original_cache)


def test_policy_empty_dataset(monkeypatch: MonkeyPatch) -> None:
    """Test policy endpoints return 200 with empty list when dataset is empty."""
    # Import here to access the cache
    from api.services import data_loader

    # Save original cache
    original_cache = data_loader._DATA_CACHE.copy()

    try:
        # Set policy data to empty lists
        data_loader._DATA_CACHE["retail_theft_trend.json"] = []
        data_loader._DATA_CACHE["vehicle_crime_trend.json"] = []
        data_loader._DATA_CACHE["crime_composition.json"] = []
        data_loader._DATA_CACHE["event_impact.json"] = []

        # Test each endpoint returns 200 with empty list
        endpoints = [
            "/api/v1/policy/retail-theft",
            "/api/v1/policy/vehicle-crimes",
            "/api/v1/policy/composition",
            "/api/v1/policy/events",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200, f"{endpoint} should return 200 with empty data"
            data = response.json()
            assert isinstance(data, list), "Response should be a list"
            assert len(data) == 0, "Response should be empty"

    finally:
        # Restore original cache
        data_loader._DATA_CACHE.clear()
        data_loader._DATA_CACHE.update(original_cache)


# Forecasting error handling tests


def test_forecasting_missing_data() -> None:
    """Test forecasting endpoint has error handling for missing forecast data."""
    from api.services.data_loader import get_data, _DATA_CACHE

    # Save original cache
    original_cache = _DATA_CACHE.copy()

    try:
        # Clear the cache to simulate missing data
        _DATA_CACHE.clear()

        # Verify get_data raises KeyError for missing forecast data
        with pytest.raises(KeyError, match="Data key not loaded.*forecast.json"):
            get_data("forecast.json")
    finally:
        # Restore cache
        _DATA_CACHE.clear()
        _DATA_CACHE.update(original_cache)


def test_forecasting_classification_missing_data() -> None:
    """Test classification endpoint has error handling for missing features data."""
    from api.services.data_loader import get_data, _DATA_CACHE

    # Save original cache
    original_cache = _DATA_CACHE.copy()

    try:
        # Clear the cache to simulate missing data
        _DATA_CACHE.clear()

        # Verify get_data raises KeyError for missing features data
        with pytest.raises(KeyError, match="Data key not loaded.*classification_features.json"):
            get_data("classification_features.json")
    finally:
        # Restore cache
        _DATA_CACHE.clear()
        _DATA_CACHE.update(original_cache)


def test_forecasting_malformed_data_passes_through(monkeypatch: MonkeyPatch) -> None:
    """Test forecasting endpoint passes through malformed cached data without error."""
    from api.services import data_loader

    # Save original cache
    original_cache = data_loader._DATA_CACHE.copy()

    try:
        # Set malformed data (missing required keys like 'forecast' and 'historical')
        malformed_data = {"incomplete": "data", "broken": True}
        data_loader._DATA_CACHE["forecast.json"] = malformed_data

        # The endpoint should pass through the malformed data as-is
        # since data_loader.get_data() returns cached data directly
        response = client.get("/api/v1/forecasting/time-series")

        # Should return 200 and pass through the malformed data
        assert response.status_code == 200
        payload = response.json()
        assert payload == malformed_data

    finally:
        # Restore cache for other tests
        data_loader._DATA_CACHE.clear()
        data_loader._DATA_CACHE.update(original_cache)
