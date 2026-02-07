"""Phase 1 local compose baseline integration checks."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest


@pytest.mark.integration
def test_compose_config_has_core_services_and_health_gates() -> None:
    if shutil.which("docker") is None:
        pytest.skip("docker is not installed")

    result = subprocess.run(
        ["docker", "compose", "config"],
        check=True,
        capture_output=True,
        text=True,
    )
    output = result.stdout

    assert "pipeline:" in output
    assert "api:" in output
    assert "web:" in output
    assert "condition: service_healthy" in output
    assert "shared_api_data" in output


def test_env_examples_define_local_compose_contract() -> None:
    root_env = Path(".env.example").read_text(encoding="utf-8")
    web_env = Path("web/.env.example").read_text(encoding="utf-8")

    assert "WEB_PORT=3001" in root_env
    assert "PIPELINE_REFRESH_INTERVAL_SECONDS=900" in root_env
    assert "ADMIN_PASSWORD=change-me" in root_env
    assert "NEXT_PUBLIC_API_BASE=http://localhost:8080" in web_env


def test_local_compose_docs_exist_and_reference_one_command_startup() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    runbook = Path("docs/local-compose.md").read_text(encoding="utf-8")

    assert "Local Run (Compose-First)" in readme
    assert "docker compose up -d --build" in readme
    assert "docker compose up -d --build" in runbook
    assert "python scripts/validate_local_stack.py" in runbook
