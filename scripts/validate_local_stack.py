#!/usr/bin/env python3
"""Validate compose baseline readiness for local stack."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def fetch_json(url: str) -> dict[str, object]:
    with urlopen(url, timeout=5) as response:  # nosec: B310 - local validation endpoint
        return json.loads(response.read().decode("utf-8"))


def wait_for_health(url: str, timeout_seconds: int = 120) -> dict[str, object]:
    deadline = time.time() + timeout_seconds
    last_error = "unknown error"
    while time.time() < deadline:
        try:
            payload = fetch_json(url)
            if payload.get("ok") is True:
                return payload
            last_error = f"health not ready: {payload}"
        except Exception as exc:
            last_error = str(exc)
        time.sleep(2)
    raise RuntimeError(f"Timed out waiting for health endpoint: {last_error}")


def wait_for_http_ok(url: str, timeout_seconds: int = 120) -> None:
    deadline = time.time() + timeout_seconds
    last_error = "unknown error"
    while time.time() < deadline:
        try:
            with urlopen(url, timeout=5) as response:  # nosec: B310 - local validation endpoint
                if 200 <= response.status < 400:
                    return
                last_error = f"unexpected status: {response.status}"
        except Exception as exc:
            last_error = str(exc)
        time.sleep(2)
    raise RuntimeError(f"Timed out waiting for URL: {url}; last_error={last_error}")


def main() -> int:
    run(["docker", "compose", "config"])
    run(["docker", "compose", "up", "-d", "--build"])
    health = wait_for_health("http://127.0.0.1:8080/api/health")
    wait_for_http_ok("http://127.0.0.1:3001")

    missing = health.get("missing_exports", [])
    if missing:
        raise RuntimeError(f"API reports missing exports: {missing}")

    print("Local compose stack validation passed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - script-level guard
        print(f"Validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
