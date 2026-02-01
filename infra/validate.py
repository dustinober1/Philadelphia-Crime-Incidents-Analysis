#!/usr/bin/env python3
"""Run pandera and optionally Great Expectations validations for a named source.

Usage: python infra/validate.py --source opd_incidents --date 2026-01-31
"""
import argparse
import json
from datetime import datetime
from pathlib import Path

import pandas as pd

try:
    from infra.validation.schemas.opd_incidents_schema import validate as pandera_validate
    import pandera
except Exception:
    pandera = None
    pandera_validate = None

def find_latest_processed(source: str) -> Path:
    p = Path("data/processed") / source
    if not p.exists():
        raise FileNotFoundError(p)
    parts = sorted(p.glob("*.parquet"))
    if not parts:
        raise FileNotFoundError(p)
    return parts[-1]

def run_pandera(path: Path, outdir: Path):
    if pandera is None:
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / "pandera_missing.txt").write_text("pandera not installed")
        return 0
    df = pd.read_parquet(path)
    try:
        res = pandera_validate(df)
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / "pandera_pass.json").write_text(json.dumps({"rows": len(df)}))
        return 0
    except pandera.errors.SchemaErrors as e:
        outdir.mkdir(parents=True, exist_ok=True)
        err = e.failure_cases.to_dict(orient="records") if hasattr(e, "failure_cases") else {"error": str(e)}
        (outdir / "pandera_errors.json").write_text(json.dumps(err, default=str, indent=2))
        return 2

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--date", required=False)
    args = parser.parse_args()

    source = args.source
    date = args.date or datetime.utcnow().strftime("%Y-%m-%d")
    outdir = Path("reports/validation") / source / date

    try:
        if args.date:
            path = Path(f"data/processed/{source}/{date}.parquet")
        else:
            path = find_latest_processed(source)
    except FileNotFoundError:
        print(f"Processed artifact for source '{source}' not found")
        return 3

    code = 0
    code |= run_pandera(path, outdir)

    # Placeholder for Great Expectations integration: run GE checkpoint here if configured.

    # Summarize
    summary = {"source": source, "date": date, "validated_path": str(path), "exit_code": code}
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2))
    md = f"# Validation summary\n\n- source: {source}\n- date: {date}\n- validated_path: {path}\n- exit_code: {code}\n"
    (outdir / "summary.md").write_text(md)

    print(md)
    return code

if __name__ == '__main__':
    raise SystemExit(main())
