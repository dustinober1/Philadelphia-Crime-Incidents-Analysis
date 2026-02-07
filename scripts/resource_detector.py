#!/usr/bin/env python3
"""Detect host CPU and memory resources across Linux, macOS, and Windows WSL."""

from __future__ import annotations

import json
import os
import platform
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ResourceSnapshot:
    platform: str
    cpu_cores: Optional[int]
    total_memory_gb: Optional[float]
    available_memory_gb: Optional[float]
    is_wsl: bool


def _run_command(cmd: list[str]) -> str:
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def detect_cpu_cores() -> Optional[int]:
    cores = os.cpu_count()
    if cores is None or cores <= 0:
        return None
    return cores


def _detect_linux_memory_gb() -> tuple[Optional[float], Optional[float]]:
    meminfo = Path("/proc/meminfo")
    if not meminfo.exists():
        return None, None

    values: dict[str, int] = {}
    for line in meminfo.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        key, raw_value = line.split(":", maxsplit=1)
        parts = raw_value.strip().split()
        if not parts:
            continue
        try:
            values[key] = int(parts[0])
        except ValueError:
            continue

    total_kb = values.get("MemTotal")
    available_kb = values.get("MemAvailable", values.get("MemFree"))
    total = round(total_kb / (1024 * 1024), 2) if total_kb else None
    available = round(available_kb / (1024 * 1024), 2) if available_kb else None
    return total, available


def _detect_macos_memory_gb() -> tuple[Optional[float], Optional[float]]:
    try:
        total_bytes = int(_run_command(["sysctl", "-n", "hw.memsize"]))
        vm_stat = _run_command(["vm_stat"])
        page_size = 4096

        for line in vm_stat.splitlines():
            if "page size of" in line:
                tail = line.split("page size of", maxsplit=1)[1].strip()
                page_size = int(tail.split()[0])
                break

        page_counts: dict[str, int] = {}
        for line in vm_stat.splitlines():
            if ":" not in line:
                continue
            key, raw_value = line.split(":", maxsplit=1)
            raw_value = raw_value.strip().rstrip(".")
            raw_value = raw_value.replace(".", "")
            try:
                page_counts[key] = int(raw_value)
            except ValueError:
                continue

        free_pages = page_counts.get("Pages free", 0)
        speculative_pages = page_counts.get("Pages speculative", 0)
        inactive_pages = page_counts.get("Pages inactive", 0)
        available_bytes = (free_pages + speculative_pages + inactive_pages) * page_size

        total = round(total_bytes / (1024**3), 2)
        available = round(available_bytes / (1024**3), 2)
        return total, available
    except (subprocess.CalledProcessError, ValueError, FileNotFoundError):
        return None, None


def detect_memory_gb() -> tuple[Optional[float], Optional[float]]:
    system = platform.system().lower()
    if system == "linux":
        return _detect_linux_memory_gb()
    if system == "darwin":
        return _detect_macos_memory_gb()
    return None, None


def detect_platform_name() -> tuple[str, bool]:
    system = platform.system()
    release = platform.release().lower()
    version = platform.version().lower()
    is_wsl = "microsoft" in release or "microsoft" in version
    if system == "Linux" and is_wsl:
        return "Windows WSL", True
    return system, is_wsl


def detect_resources() -> ResourceSnapshot:
    platform_name, is_wsl = detect_platform_name()
    total_memory_gb, available_memory_gb = detect_memory_gb()

    return ResourceSnapshot(
        platform=platform_name,
        cpu_cores=detect_cpu_cores(),
        total_memory_gb=total_memory_gb,
        available_memory_gb=available_memory_gb,
        is_wsl=is_wsl,
    )


def main() -> int:
    print(json.dumps(asdict(detect_resources()), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
