#!/usr/bin/env python3
"""Check promoted quantum observation logs."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_cmd(cmd: list[str]) -> None:
    print("$", " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def assert_json(path: Path, expected: str) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    got = data.get("experiment")
    if got != expected:
        raise AssertionError(f"{path}: expected {expected!r}, got {got!r}")


def main() -> None:
    py = sys.executable

    v0_json = ROOT / "data/quantum_observation/quantum_homeostatic_parts_observation_v0_seed20260708.json"
    v0_traj = ROOT / "data/quantum_observation/quantum_homeostatic_parts_observation_v0_seed20260708_trajectory.csv"
    v0_summary = ROOT / "data/quantum_observation/quantum_homeostatic_parts_observation_v0_seed20260708_summary.csv"
    run_cmd([py, "scripts/quantum_observation/quantum_homeostatic_parts_observation_v0.py", "--seed", "20260708", "--steps", "180", "--out", str(v0_json), "--csv", str(v0_traj), "--summary-csv", str(v0_summary)])
    assert_json(v0_json, "quantum_homeostatic_parts_observation_v0")
    if not v0_traj.exists() or not v0_summary.exists():
        raise AssertionError("missing v0 observation CSV output")

    v1_json = ROOT / "data/quantum_observation/quantum_homeostatic_parts_observation_v1_pulse_map_seed20260708.json"
    v1_summary = ROOT / "data/quantum_observation/quantum_homeostatic_parts_observation_v1_pulse_map_seed20260708_summary.csv"
    v1_trace = ROOT / "data/quantum_observation/quantum_homeostatic_parts_observation_v1_pulse_map_seed20260708_compact_trace.csv"
    run_cmd([py, "scripts/quantum_observation/quantum_homeostatic_parts_observation_v1_pulse_map.py", "--seed", "20260708", "--steps", "120", "--out", str(v1_json), "--summary-csv", str(v1_summary), "--trace-csv", str(v1_trace)])
    assert_json(v1_json, "quantum_homeostatic_parts_observation_v1_pulse_map")
    if not v1_summary.exists() or not v1_trace.exists():
        raise AssertionError("missing v1 pulse-map CSV output")

    print("OK: quantum observation logs regenerated")


if __name__ == "__main__":
    main()
