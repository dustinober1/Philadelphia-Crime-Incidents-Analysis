"""Phase 4 smoke-check productization conformance checks."""

from __future__ import annotations

from pathlib import Path


CANONICAL_SMOKE_CHECK_CMD = "python scripts/validate_local_stack.py --skip-startup"


def test_canonical_smoke_check_command_is_documented_in_readme_and_runbook() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    runbook = Path("docs/local-compose.md").read_text(encoding="utf-8")

    assert CANONICAL_SMOKE_CHECK_CMD in readme
    assert CANONICAL_SMOKE_CHECK_CMD in runbook


def test_startup_docs_follow_start_then_validate_flow() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    runbook = Path("docs/local-compose.md").read_text(encoding="utf-8")

    readme_start = readme.index("docker compose up -d --build")
    readme_validate = readme.index(CANONICAL_SMOKE_CHECK_CMD)
    assert readme_start < readme_validate

    runbook_start = runbook.index("docker compose up -d --build")
    runbook_validate = runbook.index(CANONICAL_SMOKE_CHECK_CMD)
    assert runbook_start < runbook_validate


def test_docs_cover_smoke_check_pass_and_failure_interpretation() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    runbook = Path("docs/local-compose.md").read_text(encoding="utf-8")

    assert "Local compose smoke check passed" in readme
    assert "API health check failed ... ok!=true" in readme
    assert "API health missing required exports ..." in readme
    assert "Web endpoint check failed ..." in readme

    assert "Local compose smoke check passed" in runbook
    assert "API health check failed ... ok!=true" in runbook
    assert "API health missing required exports ..." in runbook
    assert "Web endpoint check failed ..." in runbook
