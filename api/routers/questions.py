"""Community Q&A endpoints with Firestore integration."""

from __future__ import annotations

import os
import re
import time
import uuid
from collections import defaultdict, deque
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from api.models.schemas import QuestionSubmission, QuestionUpdate

router = APIRouter(prefix="/questions", tags=["questions"])

_RATE_LIMIT: dict[str, deque[float]] = defaultdict(deque)
_RATE_LIMIT_WINDOW = 60 * 60
_RATE_LIMIT_MAX = 5

_IN_MEMORY: dict[str, dict[str, Any]] = {}
_FIRESTORE_CLIENT = None


def _get_firestore_client():
    global _FIRESTORE_CLIENT
    if _FIRESTORE_CLIENT is not None:
        return _FIRESTORE_CLIENT
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        if not firebase_admin._apps:  # type: ignore[attr-defined]
            firebase_admin.initialize_app(credentials.ApplicationDefault())
        _FIRESTORE_CLIENT = firestore.client()
    except Exception:
        _FIRESTORE_CLIENT = False
    return _FIRESTORE_CLIENT


def _enforce_rate_limit(client_ip: str) -> None:
    now = time.time()
    entries = _RATE_LIMIT[client_ip]
    while entries and now - entries[0] > _RATE_LIMIT_WINDOW:
        entries.popleft()
    if len(entries) >= _RATE_LIMIT_MAX:
        raise HTTPException(status_code=429, detail="Rate limit exceeded (5/hour)")
    entries.append(now)


def _admin_guard(x_admin_key: str | None = Header(default=None)) -> None:
    expected = os.getenv("ADMIN_API_KEY", "")
    if not expected or x_admin_key != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin key")


def _validate_question_text(text: str) -> None:
    trimmed = text.strip()
    if not trimmed or len(trimmed) > 1000:
        raise HTTPException(status_code=422, detail="question_text must be 1-1000 characters")
    if re.search(r"https?://|www\.", trimmed, flags=re.IGNORECASE):
        raise HTTPException(status_code=422, detail="URLs are not allowed")
    if trimmed.isupper() and len(trimmed) > 20:
        raise HTTPException(status_code=422, detail="Likely spam content")


def _create_question(doc: dict[str, Any]) -> dict[str, Any]:
    client = _get_firestore_client()
    collection = os.getenv("FIRESTORE_COLLECTION_QUESTIONS", "questions")
    if client:
        ref = client.collection(collection).document(doc["id"])
        ref.set(doc)
    else:
        _IN_MEMORY[doc["id"]] = doc
    return doc


def _list_questions(status_filter: str) -> list[dict[str, Any]]:
    client = _get_firestore_client()
    collection = os.getenv("FIRESTORE_COLLECTION_QUESTIONS", "questions")
    if client:
        docs = (
            client.collection(collection)
            .where("status", "==", status_filter)
            .order_by("created_at", direction="DESCENDING")
            .stream()
        )
        rows = [doc.to_dict() for doc in docs]
    else:
        rows = [v for v in _IN_MEMORY.values() if v["status"] == status_filter]
        rows.sort(key=lambda x: x["created_at"], reverse=True)
    return rows


def _update_question(qid: str, payload: QuestionUpdate) -> dict[str, Any]:
    client = _get_firestore_client()
    update = {
        "answer_text": payload.answer_text.strip(),
        "status": payload.status,
        "answered_at": datetime.now(UTC).isoformat(),
    }
    collection = os.getenv("FIRESTORE_COLLECTION_QUESTIONS", "questions")
    if client:
        ref = client.collection(collection).document(qid)
        if not ref.get().exists:
            raise HTTPException(status_code=404, detail="Question not found")
        ref.update(update)
        result = ref.get().to_dict() or {}
    else:
        if qid not in _IN_MEMORY:
            raise HTTPException(status_code=404, detail="Question not found")
        _IN_MEMORY[qid].update(update)
        result = _IN_MEMORY[qid]
    return result


@router.post("")
def submit_question(payload: QuestionSubmission, request: Request) -> dict[str, Any]:
    client_ip = request.client.host if request.client else "unknown"
    _enforce_rate_limit(client_ip)

    if payload.honeypot:
        return {"ok": True}

    _validate_question_text(payload.question_text)

    now = datetime.now(UTC).isoformat()
    row = {
        "id": str(uuid.uuid4()),
        "name": payload.name.strip(),
        "email": payload.email,
        "question_text": payload.question_text.strip(),
        "status": "pending",
        "answer_text": None,
        "created_at": now,
        "answered_at": None,
    }
    _create_question(row)
    return {"ok": True, "id": row["id"]}


@router.get("")
def list_questions(
    status: str = "answered",
    x_admin_key: str | None = Header(default=None),
) -> list[dict[str, Any]]:
    if status not in {"answered", "pending"}:
        raise HTTPException(status_code=422, detail="status must be answered or pending")
    if status == "pending":
        _admin_guard(x_admin_key)
    return _list_questions(status)


@router.patch("/{question_id}")
def answer_question(question_id: str, payload: QuestionUpdate, _: None = Depends(_admin_guard)) -> dict[str, Any]:
    if payload.status not in {"answered", "pending"}:
        raise HTTPException(status_code=422, detail="status must be answered or pending")
    return _update_question(question_id, payload)


@router.delete("/{question_id}")
def delete_question(question_id: str, _: None = Depends(_admin_guard)) -> dict[str, Any]:
    client = _get_firestore_client()
    collection = os.getenv("FIRESTORE_COLLECTION_QUESTIONS", "questions")
    if client:
        ref = client.collection(collection).document(question_id)
        if not ref.get().exists:
            raise HTTPException(status_code=404, detail="Question not found")
        ref.delete()
    else:
        _IN_MEMORY.pop(question_id, None)
    return {"ok": True}
