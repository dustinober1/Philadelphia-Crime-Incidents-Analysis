"""Phase 3 developer UX and reliability integration checks."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest


@pytest.mark.integration
def test_default_compose_config_excludes_optional_profile_services() -> None:
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
    assert "pipeline-refresh-once:" not in output


@pytest.mark.integration
def test_refresh_profile_renders_optional_service() -> None:
    if shutil.which("docker") is None:
        pytest.skip("docker is not installed")

    result = subprocess.run(
        ["docker", "compose", "--profile", "refresh", "config"],
        check=True,
        capture_output=True,
        text=True,
    )
    output = result.stdout

    assert "pipeline-refresh-once:" in output
    assert "- refresh" in output


@pytest.mark.integration
def test_profile_validation_script_passes() -> None:
    if shutil.which("docker") is None:
        pytest.skip("docker is not installed")

    subprocess.run(["./scripts/validate_compose_profiles.sh"], check=True)


def test_docs_cover_recovery_reset_and_profile_commands() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    runbook = Path("docs/local-compose.md").read_text(encoding="utf-8")

    assert "Optional Compose Profiles (Advanced)" in readme
    assert "docker compose --profile refresh config" in readme
    assert "docker compose --profile refresh run --rm pipeline-refresh-once" in readme

    assert "Recovery playbooks" in runbook
    assert "Post-recovery validation checklist" in runbook
    assert "./scripts/reset_local_stack.sh" in runbook
    assert "python scripts/validate_local_stack.py --skip-startup" in runbook
