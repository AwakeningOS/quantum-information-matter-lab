#!/usr/bin/env python3
"""Minimal reproducibility checker for canonical raw logs.

The checker intentionally starts small. It verifies that bootstrap scripts run
and write their expected raw artifacts. Expand this file whenever a result is
promoted to RAW_LOG_BACKED.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_cmd(cmd: list[str]) -> None:
    print("$", " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def assert_json(path: Path, expected_experiment: str) -> None:
    if not path.exists():
        raise AssertionError(f"missing raw log: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    got = data.get("experiment")
    if got != expected_experiment:
        raise AssertionError(f"{path}: expected experiment={expected_experiment!r}, got {got!r}")


def main() -> None:
    py = sys.executable

    micro_json = ROOT / "data/microreactor/information_microreactor_sandbox_seed20260708.json"
    micro_csv = ROOT / "data/microreactor/information_microreactor_sandbox_seed20260708_summary.csv"
    run_cmd([
        py,
        "scripts/phenomenology/information_microreactor_sandbox.py",
        "--seed", "20260708",
        "--out", str(micro_json),
        "--csv", str(micro_csv),
    ])
    assert_json(micro_json, "information_microreactor_sandbox")
    if not micro_csv.exists():
        raise AssertionError(f"missing CSV: {micro_csv}")

    contextual_json = ROOT / "data/contextual/contextual_component_seed20260708.json"
    run_cmd([
        py,
        "scripts/contextual/contextual_component_skeleton.py",
        "--seed", "20260708",
        "--steps", "64",
        "--out", str(contextual_json),
    ])
    assert_json(contextual_json, "contextual_component_skeleton")

    print("OK: bootstrap raw-log checks passed")


if __name__ == "__main__":
    main()
