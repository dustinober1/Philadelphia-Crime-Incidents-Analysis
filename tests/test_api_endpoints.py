"""FastAPI endpoint smoke tests for web conversion API."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from api.main import app
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
