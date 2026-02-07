"""Phase 6 preset and default-regression guardrail checks."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest


@pytest.mark.integration
def test_runtime_guardrails_script_passes() -> None:
    if shutil.which("docker") is None:
        pytest.skip("docker is not installed")

    subprocess.run(["./scripts/validate_runtime_guardrails.sh"], check=True)


def test_runtime_guardrails_script_is_canonical_path() -> None:
    wrapper = Path("scripts/validate_runtime_guardrails.sh").read_text(encoding="utf-8")
    makefile = Path("Makefile").read_text(encoding="utf-8")

    assert "./scripts/validate_compose_runtime_mode.sh" in wrapper
    assert "./scripts/validate_compose_runtime_budget.sh" in wrapper
    assert "run_stage" in wrapper
    assert "check-runtime-guardrails" in makefile
    assert "./scripts/validate_runtime_guardrails.sh" in makefile


def test_preset_04_traceability_maps_to_phase_6() -> None:
    requirements = Path(".planning/REQUIREMENTS.md").read_text(encoding="utf-8")
    roadmap = Path(".planning/ROADMAP.md").read_text(encoding="utf-8")

    assert "| PRESET-04 | Phase 6 |" in requirements
    assert "### Phase 6: Preset and Regression Guardrails" in roadmap
    assert "**Requirements:** PRESET-04" in roadmap
