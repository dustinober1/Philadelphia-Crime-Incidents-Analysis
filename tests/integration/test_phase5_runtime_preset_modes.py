"""Phase 5 runtime preset mode conformance checks."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest


@pytest.mark.integration
def test_runtime_mode_validation_script_passes() -> None:
    if shutil.which("docker") is None:
        pytest.skip("docker is not installed")

    subprocess.run(["./scripts/validate_compose_runtime_mode.sh"], check=True)


@pytest.mark.integration
def test_default_runtime_budget_validation_script_passes() -> None:
    if shutil.which("docker") is None:
        pytest.skip("docker is not installed")

    subprocess.run(["./scripts/validate_compose_runtime_budget.sh"], check=True)


def test_runtime_preset_env_templates_define_expected_values() -> None:
    low_power = Path(".env.runtime.low-power").read_text(encoding="utf-8")
    high_performance = Path(".env.runtime.high-performance").read_text(encoding="utf-8")

    for expected in (
        "PIPELINE_CPU_LIMIT=0.50",
        "PIPELINE_MEM_LIMIT=768m",
        "API_CPU_LIMIT=0.50",
        "API_MEM_LIMIT=512m",
        "WEB_CPU_LIMIT=0.50",
        "WEB_MEM_LIMIT=512m",
    ):
        assert expected in low_power

    for expected in (
        "PIPELINE_CPU_LIMIT=2.00",
        "PIPELINE_MEM_LIMIT=3072m",
        "API_CPU_LIMIT=2.00",
        "API_MEM_LIMIT=2048m",
        "WEB_CPU_LIMIT=2.00",
        "WEB_MEM_LIMIT=2048m",
    ):
        assert expected in high_performance


def test_docs_and_scripts_document_runtime_mode_workflow() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    runbook = Path("docs/local-compose.md").read_text(encoding="utf-8")
    helper = Path("scripts/compose_with_runtime_mode.sh").read_text(encoding="utf-8")
    mode_validator = Path("scripts/validate_compose_runtime_mode.sh").read_text(encoding="utf-8")
    budget_validator = Path("scripts/validate_compose_runtime_budget.sh").read_text(encoding="utf-8")
    runtime_guardrails = Path("scripts/validate_runtime_guardrails.sh").read_text(encoding="utf-8")

    assert "docker compose up -d --build" in readme
    assert "./scripts/compose_with_runtime_mode.sh --mode low-power up -d --build" in readme
    assert "./scripts/compose_with_runtime_mode.sh --mode high-performance up -d --build" in readme
    assert "./scripts/validate_runtime_guardrails.sh" in readme

    assert "docker compose up -d --build" in runbook
    assert "./scripts/compose_with_runtime_mode.sh --mode low-power up -d --build" in runbook
    assert "./scripts/compose_with_runtime_mode.sh --mode high-performance up -d --build" in runbook
    assert "./scripts/validate_runtime_guardrails.sh" in runbook

    assert "Modes:" in helper
    assert "check_mode default" in mode_validator
    assert "check_mode low-power" in mode_validator
    assert "check_mode high-performance" in mode_validator
    assert "Default compose runtime budgets match expected baseline values" in budget_validator
    assert "validate_compose_runtime_mode.sh" in runtime_guardrails
    assert "validate_compose_runtime_budget.sh" in runtime_guardrails
