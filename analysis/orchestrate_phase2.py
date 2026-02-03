"""Phase 2 orchestration: Spatial & Socioeconomic Analysis.

This module provides orchestration capabilities for running all Phase 2
notebooks in sequence and validating their outputs.

Usage:
    python -m analysis.orchestrate_phase2

Or from Python:
    from analysis.orchestrate_phase2 import orchestrate_phase2
    results = orchestrate_phase2()
"""

from pathlib import Path
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Phase 2 notebooks in execution order
NOTEBOOKS = [
    "hotspot_clustering.ipynb",
    "robbery_temporal_heatmap.ipynb",
    "district_severity.ipynb",
    "census_tract_rates.ipynb",
    "phase2_summary.ipynb",  # Summary must run last
]


def run_notebook(notebook_name: str, repo_root: Path, timeout: int = 600) -> Dict:
    """Execute a notebook using jupyter nbconvert.

    Args:
        notebook_name: Name of notebook file in notebooks/ directory
        repo_root: Repository root path
        timeout: Maximum execution time in seconds

    Returns:
        Dictionary with execution results
    """
    notebook_path = repo_root / "notebooks" / notebook_name

    result = {
        "notebook": notebook_name,
        "success": False,
        "error": None,
        "duration": None,
    }

    if not notebook_path.exists():
        result["error"] = f"Notebook not found: {notebook_path}"
        print(f"  [SKIP] {notebook_name} - not found")
        return result

    print(f"  Running {notebook_name}...", end="", flush=True)
    start_time = datetime.now()

    cmd = [
        "jupyter",
        "nbconvert",
        "--to",
        "notebook",
        "--execute",
        "--inplace",
        f"--ExecutePreprocessor.timeout={timeout}",
        str(notebook_path),
    ]

    try:
        proc_result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout + 30,  # Give a bit more time than notebook timeout
        )

        duration = (datetime.now() - start_time).total_seconds()
        result["duration"] = duration

        if proc_result.returncode == 0:
            result["success"] = True
            print(f" done ({duration:.1f}s)")
        else:
            result["error"] = (
                proc_result.stderr[:500] if proc_result.stderr else "Unknown error"
            )
            print(f" FAILED")
            print(f"    Error: {result['error'][:200]}...")

    except subprocess.TimeoutExpired:
        result["error"] = f"Timeout after {timeout}s"
        print(f" TIMEOUT")
    except Exception as e:
        result["error"] = str(e)
        print(f" ERROR: {e}")

    return result


def validate_phase2(repo_root: Path) -> Dict:
    """Run validation script and return results."""
    validate_script = repo_root / "scripts" / "validate_phase2.py"

    if not validate_script.exists():
        return {"success": False, "error": "Validation script not found"}

    print("  Running validation...", end="", flush=True)

    try:
        result = subprocess.run(
            [sys.executable, str(validate_script)],
            capture_output=True,
            text=True,
            timeout=60,
        )

        success = result.returncode == 0
        print(f" {'PASSED' if success else 'FAILED'}")

        return {
            "success": success,
            "output": result.stdout,
            "error": result.stderr if not success else None,
        }
    except Exception as e:
        print(f" ERROR")
        return {"success": False, "error": str(e)}


def orchestrate_phase2(
    repo_root: Optional[Path] = None,
    notebooks: Optional[List[str]] = None,
    skip_validation: bool = False,
) -> Dict:
    """Run all Phase 2 notebooks and validate outputs.

    Args:
        repo_root: Repository root path (auto-detected if None)
        notebooks: List of notebooks to run (uses default if None)
        skip_validation: Skip validation step if True

    Returns:
        Dictionary with orchestration results
    """

    if repo_root is None:
        repo_root = Path(__file__).parent.parent

    if notebooks is None:
        notebooks = NOTEBOOKS

    results = {
        "started": datetime.now().isoformat(),
        "repo_root": str(repo_root),
        "notebooks": {},
        "validation": None,
        "success": False,
        "completed": None,
    }

    print("\n" + "=" * 60)
    print("PHASE 2 ORCHESTRATION")
    print("=" * 60)
    print(f"Repository: {repo_root}")
    print(f"Notebooks: {len(notebooks)}")

    # Run notebooks
    print("\n[1/2] Executing notebooks...")
    all_passed = True
    for notebook in notebooks:
        nb_result = run_notebook(notebook, repo_root)
        results["notebooks"][notebook] = nb_result
        if not nb_result["success"]:
            all_passed = False

    # Validate outputs
    if not skip_validation:
        print("\n[2/2] Validating outputs...")
        results["validation"] = validate_phase2(repo_root)
    else:
        print("\n[2/2] Validation skipped")
        results["validation"] = {"success": True, "skipped": True}

    # Calculate summary
    notebooks_passed = sum(1 for r in results["notebooks"].values() if r["success"])
    notebooks_total = len(results["notebooks"])
    validation_passed = results["validation"].get("success", False)

    results["success"] = all_passed and validation_passed
    results["completed"] = datetime.now().isoformat()

    # Print summary
    print("\n" + "=" * 60)
    status = "COMPLETE" if results["success"] else "FAILED"
    print(f"PHASE 2 {status}")
    print("=" * 60)
    print(f"\nNotebooks: {notebooks_passed}/{notebooks_total} passed")
    print(f"Validation: {'PASSED' if validation_passed else 'FAILED'}")

    if not results["success"]:
        print("\nFailed items:")
        for name, nb_result in results["notebooks"].items():
            if not nb_result["success"]:
                print(f"  - {name}: {nb_result.get('error', 'Unknown error')[:100]}")
        if not validation_passed:
            print(
                f"  - Validation: {results['validation'].get('error', 'Check validation output')}"
            )

    # Calculate total runtime
    started = datetime.fromisoformat(results["started"])
    completed = datetime.fromisoformat(results["completed"])
    total_seconds = (completed - started).total_seconds()
    print(f"\nTotal runtime: {total_seconds:.1f}s")

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Orchestrate Phase 2 notebooks")
    parser.add_argument(
        "--skip-validation", action="store_true", help="Skip validation step"
    )
    parser.add_argument(
        "--notebook", type=str, nargs="+", help="Run specific notebooks (default: all)"
    )
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent

    results = orchestrate_phase2(
        repo_root=repo_root,
        notebooks=args.notebook,
        skip_validation=args.skip_validation,
    )

    sys.exit(0 if results["success"] else 1)
