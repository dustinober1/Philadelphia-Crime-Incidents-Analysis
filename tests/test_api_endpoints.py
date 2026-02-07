"""FastAPI endpoint smoke tests for web conversion API."""

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
