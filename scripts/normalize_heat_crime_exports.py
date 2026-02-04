#!/usr/bin/env python3
"""Normalize heat-crime notebook exports and JSON schema.

This script attempts to make artifact filenames and JSON schema match the canonical
planning expectations without modifying notebooks. It will:

- Copy any `reports/heat_crime_*.png` to `reports/04_heat_crime_*.png` if the latter
  do not exist.
- Normalize statistical-tests JSON via `analysis.report_utils.normalize_heat_crime_json`
  and write the canonical `reports/04_heat_crime_statistical_tests.json`.

Usage:
  python scripts/normalize_heat_crime_exports.py
"""

from pathlib import Path
import json
import sys
from analysis import report_utils


REPORTS = Path("reports")


def copy_if_missing(src: Path, dst: Path):
    if not src.exists():
        return False
    if dst.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        import shutil

        shutil.copy2(src, dst)
        return True
    except Exception as e:
        print(f"Failed to copy {src} -> {dst}: {e}", file=sys.stderr)
        return False


def main():
    mappings = [
        ("heat_crime_scatterplots.png", "04_heat_crime_correlation_matrix.png"),
        ("heat_crime_by_temperature_bins.png", "04_heat_crime_temperature_bins.png"),
        ("heat_crime_hourly_patterns.png", "04_heat_crime_hourly_patterns.png"),
    ]

    made = []
    for src_name, dst_name in mappings:
        src = REPORTS / src_name
        dst = REPORTS / dst_name
        if copy_if_missing(src, dst):
            made.append((src_name, dst_name))

    # Normalize JSON
    # Try several common input filenames
    candidates = [
        REPORTS / "04_heat_crime_statistical_tests.json",
        REPORTS / "heat_crime_statistical_tests.json",
        REPORTS / "heat_crime_stat_tests.json",
    ]
    in_path = None
    for c in candidates:
        if c.exists():
            in_path = c
            break

    out_path = REPORTS / "04_heat_crime_statistical_tests.json"
    if in_path:
        # normalize and overwrite canonical file
        try:
            report_utils.normalize_heat_crime_json(str(in_path), str(out_path))
            print(f"Normalized JSON written to {out_path}")
        except Exception as e:
            print(
                f"Failed to normalize JSON {in_path} -> {out_path}: {e}",
                file=sys.stderr,
            )
    else:
        print("No statistical-tests JSON found to normalize; checked:", candidates)

    if made:
        print("Copied files:", made)
    else:
        print("No copies made; canonical files likely present already.")


if __name__ == "__main__":
    main()
