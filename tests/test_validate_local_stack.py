"""Unit tests for local compose smoke-check validator."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

import pytest


def _load_validator_module():
    module_path = Path("scripts/validate_local_stack.py")
    spec = importlib.util.spec_from_file_location("validate_local_stack", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Failed to load scripts/validate_local_stack.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validate_local_stack = _load_validator_module()


def _base_args() -> argparse.Namespace:
    return argparse.Namespace(
        skip_startup=True,
        api_health_url="http://127.0.0.1:8080/api/health",
        web_url="http://127.0.0.1:3001",
        timeout_seconds=5,
    )


def test_main_skip_startup_does_not_invoke_compose_up(monkeypatch: pytest.MonkeyPatch) -> None:
    commands: list[list[str]] = []

    monkeypatch.setattr(validate_local_stack, "parse_args", lambda: _base_args())
    monkeypatch.setattr(validate_local_stack, "run", lambda cmd: commands.append(cmd))
    monkeypatch.setattr(
        validate_local_stack,
        "wait_for_health",
        lambda *_args, **_kwargs: {"ok": True, "missing_exports": []},
    )
    monkeypatch.setattr(validate_local_stack, "wait_for_http_ok", lambda *_args, **_kwargs: None)

    assert validate_local_stack.main() == 0
    assert commands == [["docker", "compose", "config"]]


def test_wait_for_health_fails_when_ok_not_true(monkeypatch: pytest.MonkeyPatch) -> None:
    times = iter([0.0, 0.1, 2.1])

    monkeypatch.setattr(validate_local_stack.time, "time", lambda: next(times))
    monkeypatch.setattr(validate_local_stack.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(validate_local_stack, "fetch_json", lambda _url: {"ok": False})

    with pytest.raises(RuntimeError, match="ok!=true"):
        validate_local_stack.wait_for_health(
            "http://127.0.0.1:8080/api/health",
            timeout_seconds=2,
        )


def test_main_fails_when_missing_exports_present(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(validate_local_stack, "parse_args", lambda: _base_args())
    monkeypatch.setattr(validate_local_stack, "run", lambda _cmd: None)
    monkeypatch.setattr(
        validate_local_stack,
        "wait_for_health",
        lambda *_args, **_kwargs: {
            "ok": True,
            "missing_exports": ["incidents.geojson", "metadata.json"],
        },
    )
    monkeypatch.setattr(validate_local_stack, "wait_for_http_ok", lambda *_args, **_kwargs: None)

    with pytest.raises(RuntimeError, match="incidents.geojson, metadata.json"):
        validate_local_stack.main()


def test_main_fails_when_web_endpoint_unreachable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(validate_local_stack, "parse_args", lambda: _base_args())
    monkeypatch.setattr(validate_local_stack, "run", lambda _cmd: None)
    monkeypatch.setattr(
        validate_local_stack,
        "wait_for_health",
        lambda *_args, **_kwargs: {"ok": True, "missing_exports": []},
    )
    monkeypatch.setattr(
        validate_local_stack,
        "wait_for_http_ok",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            RuntimeError("Web endpoint check failed for http://127.0.0.1:3001: connection refused")
        ),
    )

    with pytest.raises(RuntimeError, match="Web endpoint check failed"):
        validate_local_stack.main()


def test_parse_args_defaults_remain_documented_contract(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["validate_local_stack.py"])
    args = validate_local_stack.parse_args()

    assert args.skip_startup is False
    assert args.api_health_url == "http://127.0.0.1:8080/api/health"
    assert args.web_url == "http://127.0.0.1:3001"
    assert args.timeout_seconds == 120
