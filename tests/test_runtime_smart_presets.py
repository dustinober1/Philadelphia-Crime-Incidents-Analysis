"""Unit tests for host resource detection and smart preset recommendation."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pytest


def _load_script_module(module_name: str, path: str):
    script_path = Path(path)
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


resource_detector = _load_script_module("resource_detector", "scripts/resource_detector.py")
preset_calculator = _load_script_module("preset_calculator", "scripts/preset_calculator.py")


def test_recommend_preset_high_performance() -> None:
    snapshot = resource_detector.ResourceSnapshot(
        platform="Linux",
        cpu_cores=12,
        total_memory_gb=32.0,
        available_memory_gb=14.0,
        is_wsl=False,
    )

    recommendation = preset_calculator.recommend_preset(snapshot)

    assert recommendation.mode == "high-performance"
    assert "sufficient CPU and RAM" in recommendation.reason


def test_recommend_preset_low_power() -> None:
    snapshot = resource_detector.ResourceSnapshot(
        platform="Linux",
        cpu_cores=2,
        total_memory_gb=6.0,
        available_memory_gb=2.0,
        is_wsl=False,
    )

    recommendation = preset_calculator.recommend_preset(snapshot)

    assert recommendation.mode == "low-power"


def test_recommend_preset_default_when_detection_incomplete() -> None:
    snapshot = resource_detector.ResourceSnapshot(
        platform="Linux",
        cpu_cores=8,
        total_memory_gb=16.0,
        available_memory_gb=None,
        is_wsl=False,
    )

    recommendation = preset_calculator.recommend_preset(snapshot)

    assert recommendation.mode == "default"
    assert "incomplete" in recommendation.reason


def test_detect_platform_name_wsl(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(resource_detector.platform, "system", lambda: "Linux")
    monkeypatch.setattr(
        resource_detector.platform, "release", lambda: "6.6.0-microsoft-standard-WSL2"
    )
    monkeypatch.setattr(resource_detector.platform, "version", lambda: "#1 SMP")

    platform_name, is_wsl = resource_detector.detect_platform_name()

    assert platform_name == "Windows WSL"
    assert is_wsl is True


def test_runtime_helper_usage_lists_auto_and_recommend() -> None:
    helper = Path("scripts/compose_with_runtime_mode.sh").read_text(encoding="utf-8")

    assert "auto              Detect host resources and choose a preset automatically" in helper
    assert "--recommend" in helper
