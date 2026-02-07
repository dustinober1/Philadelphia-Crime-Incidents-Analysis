"""Phase 2 footprint/runtime optimization integration checks."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest


@pytest.mark.integration
def test_compose_config_has_runtime_budgets_for_core_services() -> None:
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
    assert "cpus:" in output
    assert "mem_limit:" in output


@pytest.mark.integration
def test_runtime_budget_validation_script_passes() -> None:
    if shutil.which("docker") is None:
        pytest.skip("docker is not installed")

    subprocess.run(["./scripts/validate_compose_runtime_budget.sh"], check=True)


def test_dockerfiles_and_env_contract_include_phase2_optimizations() -> None:
    dockerignore = Path(".dockerignore").read_text(encoding="utf-8")
    api_dockerfile = Path("api/Dockerfile").read_text(encoding="utf-8")
    pipeline_dockerfile = Path("pipeline/Dockerfile").read_text(encoding="utf-8")
    web_dockerfile = Path("web/Dockerfile").read_text(encoding="utf-8")
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")
    env_example = Path(".env.example").read_text(encoding="utf-8")

    assert "web/node_modules/" in dockerignore
    assert "reports/" in dockerignore

    assert "COPY api/requirements.txt /tmp/requirements.txt" in api_dockerfile
    assert "pip install --no-cache-dir -r /tmp/requirements.txt" in api_dockerfile

    assert "COPY pyproject.toml /app/pyproject.toml" in pipeline_dockerfile
    assert "COPY data/boundaries /app/data/boundaries" in pipeline_dockerfile

    assert "npm ci --no-audit --no-fund" in web_dockerfile
    assert "npm install &&" not in compose

    for key in (
        "PIPELINE_CPU_LIMIT",
        "PIPELINE_MEM_LIMIT",
        "API_CPU_LIMIT",
        "API_MEM_LIMIT",
        "WEB_CPU_LIMIT",
        "WEB_MEM_LIMIT",
    ):
        assert f"{key}=" in env_example


def test_docs_cover_budget_tuning_and_validation_scripts() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    runbook = Path("docs/local-compose.md").read_text(encoding="utf-8")

    assert "Default Runtime Budgets" in readme
    assert "docker compose config | rg -n \"cpus|mem_limit\"" in readme

    assert "Runtime budgets" in runbook
    assert "./scripts/validate_compose_runtime_budget.sh" in runbook
    assert "./scripts/benchmark_container_builds.sh" in runbook
