"""Validate Phase 1 artifacts meet quality standards."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def validate_png_dpi(filepath: Path, min_dpi: int = 100) -> Tuple[bool, str]:
    """Check PNG has acceptable DPI (using PIL if available)."""
    try:
        from PIL import Image

        img = Image.open(filepath)
        dpi = img.info.get("dpi", (72, 72))
        actual_dpi = int(dpi[0])
        if actual_dpi >= min_dpi:
            return True, f"{actual_dpi} DPI"
        return False, f"{actual_dpi} DPI (< {min_dpi})"
    except ImportError:
        # PIL not available, check file exists and is non-empty
        if filepath.exists() and filepath.stat().st_size > 1000:
            return True, "exists (DPI check skipped - PIL not installed)"
        return False, "file missing or too small"


def validate_report_sections(filepath: Path) -> Tuple[bool, str]:
    """Check report has required sections."""
    if not filepath.exists():
        return False, "file missing"

    content = filepath.read_text()
    required = ["## Summary", "## Methods", "## Findings", "## Limitations"]
    missing = [s for s in required if s not in content]

    if not missing:
        return True, "all sections present"
    return False, f"missing: {', '.join(missing)}"


def validate_manifest(filepath: Path) -> Tuple[bool, str]:
    """Check manifest has required fields."""
    if not filepath.exists():
        return False, "file missing"

    try:
        manifest = json.loads(filepath.read_text())
        required_keys = ["version", "timestamp", "artifacts"]
        missing = [k for k in required_keys if k not in manifest]

        if not missing:
            return True, f"{len(manifest['artifacts'])} artifacts listed"
        return False, f"missing keys: {', '.join(missing)}"
    except json.JSONDecodeError as e:
        return False, f"invalid JSON: {e}"


def validate_hash(filepath: Path, expected_hash: str) -> Tuple[bool, str]:
    """Verify file hash matches manifest."""
    if not filepath.exists():
        return False, "file missing"

    actual = hashlib.sha256(filepath.read_bytes()).hexdigest()
    if actual == expected_hash:
        return True, "hash matches"
    return False, f"hash mismatch: {actual[:12]}... vs {expected_hash[:12]}..."


def main() -> int:
    """Run all validations and return exit code."""
    reports_dir = PROJECT_ROOT / "reports"
    errors = 0

    print("=" * 60)
    print("Phase 1 Artifact Validation")
    print("=" * 60)

    # Validate PNGs
    print("\n--- PNG Artifacts ---")
    for png in sorted(reports_dir.glob("*_v*.png")):
        success, msg = validate_png_dpi(png)
        status = "PASS" if success else "FAIL"
        print(f"  [{status}] {png.name}: {msg}")
        if not success:
            errors += 1

    # Validate reports
    print("\n--- Markdown Reports ---")
    for md in sorted(reports_dir.glob("*_report_*.md")):
        success, msg = validate_report_sections(md)
        status = "PASS" if success else "FAIL"
        print(f"  [{status}] {md.name}: {msg}")
        if not success:
            errors += 1

    # Validate manifests
    print("\n--- Manifests ---")
    for manifest_path in sorted(reports_dir.glob("*_manifest_*.json")):
        success, msg = validate_manifest(manifest_path)
        status = "PASS" if success else "FAIL"
        print(f"  [{status}] {manifest_path.name}: {msg}")
        if not success:
            errors += 1

    # Validate global phase manifest
    phase_manifest = reports_dir / "phase1_manifest_v1.0.json"
    if phase_manifest.exists():
        print("\n--- Global Manifest Hash Verification ---")
        manifest = json.loads(phase_manifest.read_text())
        for artifact in manifest.get("artifacts", []):
            artifact_path = PROJECT_ROOT / artifact["path"]
            expected_hash = artifact["sha256"]
            success, msg = validate_hash(artifact_path, expected_hash)
            status = "PASS" if success else "FAIL"
            print(f"  [{status}] {artifact_path.name}: {msg}")
            if not success:
                errors += 1

    # Summary
    print("\n" + "=" * 60)
    if errors == 0:
        print("All validations PASSED")
        return 0
    else:
        print(f"FAILED: {errors} validation(s) did not pass")
        return 1


if __name__ == "__main__":
    sys.exit(main())
