#!/usr/bin/env python3
"""Calculate recommended compose runtime preset from host resources."""

from __future__ import annotations

import argparse
import json
import shlex
from dataclasses import asdict, dataclass
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from resource_detector import ResourceSnapshot, detect_resources


@dataclass
class PresetRecommendation:
    mode: str
    reason: str
    snapshot: ResourceSnapshot


def recommend_preset(snapshot: ResourceSnapshot) -> PresetRecommendation:
    cpu = snapshot.cpu_cores
    total = snapshot.total_memory_gb
    available = snapshot.available_memory_gb

    if cpu is None or total is None or available is None:
        return PresetRecommendation(
            mode="default",
            reason="resource detection incomplete; using baseline defaults",
            snapshot=snapshot,
        )

    if cpu >= 8 and total >= 16 and available >= 8:
        return PresetRecommendation(
            mode="high-performance",
            reason="host has sufficient CPU and RAM headroom",
            snapshot=snapshot,
        )

    if cpu < 4 or total < 8 or available < 4:
        return PresetRecommendation(
            mode="low-power",
            reason="host resources are constrained; using lower footprint preset",
            snapshot=snapshot,
        )

    return PresetRecommendation(
        mode="default",
        reason="host resources are moderate; baseline runtime preset is recommended",
        snapshot=snapshot,
    )


def _format_env(recommendation: PresetRecommendation) -> str:
    values = {
        "RECOMMENDED_MODE": recommendation.mode,
        "RECOMMENDATION_REASON": recommendation.reason,
        "DETECTION_PLATFORM": recommendation.snapshot.platform,
        "DETECTION_CPU_CORES": recommendation.snapshot.cpu_cores,
        "DETECTION_TOTAL_MEM_GB": recommendation.snapshot.total_memory_gb,
        "DETECTION_AVAILABLE_MEM_GB": recommendation.snapshot.available_memory_gb,
    }
    lines: list[str] = []
    for key, value in values.items():
        rendered = "unknown" if value is None else str(value)
        lines.append(f"{key}={shlex.quote(rendered)}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Recommend runtime mode based on host resources.")
    parser.add_argument("--cpu-cores", type=int, help="Override detected CPU cores")
    parser.add_argument("--total-mem-gb", type=float, help="Override detected total memory in GB")
    parser.add_argument(
        "--available-mem-gb",
        type=float,
        help="Override detected available memory in GB",
    )
    parser.add_argument("--platform", help="Override detected platform name")
    parser.add_argument("--is-wsl", action="store_true", help="Force WSL platform flag")
    parser.add_argument(
        "--format",
        choices=["human", "json", "env"],
        default="human",
        help="Output format",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    snapshot = detect_resources()
    if args.cpu_cores is not None:
        snapshot.cpu_cores = args.cpu_cores
    if args.total_mem_gb is not None:
        snapshot.total_memory_gb = args.total_mem_gb
    if args.available_mem_gb is not None:
        snapshot.available_memory_gb = args.available_mem_gb
    if args.platform is not None:
        snapshot.platform = args.platform
    if args.is_wsl:
        snapshot.is_wsl = True

    recommendation = recommend_preset(snapshot)

    if args.format == "env":
        print(_format_env(recommendation))
        return 0

    payload = {
        "recommended_mode": recommendation.mode,
        "reason": recommendation.reason,
        "snapshot": asdict(recommendation.snapshot),
    }
    if args.format == "json":
        print(json.dumps(payload, indent=2))
    else:
        print(f"Platform: {recommendation.snapshot.platform}")
        print(f"CPU cores: {recommendation.snapshot.cpu_cores}")
        print(f"Total RAM (GB): {recommendation.snapshot.total_memory_gb}")
        print(f"Available RAM (GB): {recommendation.snapshot.available_memory_gb}")
        print(f"Recommended mode: {recommendation.mode}")
        print(f"Reason: {recommendation.reason}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
