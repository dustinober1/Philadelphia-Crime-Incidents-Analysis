#!/usr/bin/env python3
"""Validate compose baseline readiness for local stack."""

from __future__ import annotations

import argparse
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
            last_error = f"health endpoint returned ok!=true; payload={payload}"
        except Exception as exc:
            last_error = str(exc)
        time.sleep(2)
    raise RuntimeError(f"API health check failed for {url}: {last_error}")


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
    raise RuntimeError(f"Web endpoint check failed for {url}: {last_error}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate local compose stack health and endpoint readiness. "
            "By default this script starts/rebuilds the stack first."
        )
    )
    parser.add_argument(
        "--skip-startup",
        action="store_true",
        help="Do not run `docker compose up -d --build`; only validate running services.",
    )
    parser.add_argument(
        "--api-health-url",
        default="http://127.0.0.1:8080/api/health",
        help="API health endpoint URL to validate.",
    )
    parser.add_argument(
        "--web-url",
        default="http://127.0.0.1:3001",
        help="Web URL to validate.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=120,
        help="Max seconds to wait for each endpoint.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run(["docker", "compose", "config"])
    if not args.skip_startup:
        run(["docker", "compose", "up", "-d", "--build"])

    health = wait_for_health(args.api_health_url, timeout_seconds=args.timeout_seconds)
    wait_for_http_ok(args.web_url, timeout_seconds=args.timeout_seconds)

    missing = health.get("missing_exports", [])
    if missing:
        missing_str = ", ".join(str(name) for name in missing)
        raise RuntimeError(f"API health missing required exports: {missing_str}")

    print("Local compose smoke check passed")
    print(f"- API health: {args.api_health_url}")
    print(f"- Web endpoint: {args.web_url}")
    print("- Required API exports: present")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - script-level guard
        print(f"Validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
