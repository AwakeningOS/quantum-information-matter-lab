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


def require(path: Path) -> None:
    if not path.exists():
        raise AssertionError(f"missing output: {path}")


def main() -> None:
    py = sys.executable

    v0_json = ROOT / "data/quantum_observation/quantum_homeostatic_parts_observation_v0_seed20260708.json"
    v0_traj = ROOT / "data/quantum_observation/quantum_homeostatic_parts_observation_v0_seed20260708_trajectory.csv"
    v0_summary = ROOT / "data/quantum_observation/quantum_homeostatic_parts_observation_v0_seed20260708_summary.csv"
    run_cmd([py, "scripts/quantum_observation/quantum_homeostatic_parts_observation_v0.py", "--seed", "20260708", "--steps", "180", "--out", str(v0_json), "--csv", str(v0_traj), "--summary-csv", str(v0_summary)])
    assert_json(v0_json, "quantum_homeostatic_parts_observation_v0")
    require(v0_traj)
    require(v0_summary)

    v1_json = ROOT / "data/quantum_observation/quantum_homeostatic_parts_observation_v1_pulse_map_seed20260708.json"
    v1_summary = ROOT / "data/quantum_observation/quantum_homeostatic_parts_observation_v1_pulse_map_seed20260708_summary.csv"
    v1_trace = ROOT / "data/quantum_observation/quantum_homeostatic_parts_observation_v1_pulse_map_seed20260708_compact_trace.csv"
    run_cmd([py, "scripts/quantum_observation/quantum_homeostatic_parts_observation_v1_pulse_map.py", "--seed", "20260708", "--steps", "120", "--out", str(v1_json), "--summary-csv", str(v1_summary), "--trace-csv", str(v1_trace)])
    assert_json(v1_json, "quantum_homeostatic_parts_observation_v1_pulse_map")
    require(v1_summary)
    require(v1_trace)

    v2_json = ROOT / "data/quantum_observation/quantum_homeostatic_parts_observation_v2_causal_touch_response_seed20260708.json"
    v2_summary = ROOT / "data/quantum_observation/quantum_homeostatic_parts_observation_v2_causal_touch_response_seed20260708_summary.csv"
    v2_trace = ROOT / "data/quantum_observation/quantum_homeostatic_parts_observation_v2_causal_touch_response_seed20260708_compact_trace.csv"
    run_cmd([py, "scripts/quantum_observation/quantum_homeostatic_parts_observation_v2_causal_touch_response.py", "--seed", "20260708", "--steps", "120", "--touch-time", "30", "--out", str(v2_json), "--summary-csv", str(v2_summary), "--trace-csv", str(v2_trace)])
    assert_json(v2_json, "quantum_homeostatic_parts_observation_v2_causal_touch_response")
    require(v2_summary)
    require(v2_trace)

    v3_json = ROOT / "data/quantum_observation/quantum_homeostatic_parts_observation_v3_recovery_cycle_seed20260708.json"
    v3_summary = ROOT / "data/quantum_observation/quantum_homeostatic_parts_observation_v3_recovery_cycle_seed20260708_summary.csv"
    v3_touch = ROOT / "data/quantum_observation/quantum_homeostatic_parts_observation_v3_recovery_cycle_seed20260708_touch_rows.csv"
    run_cmd([py, "scripts/quantum_observation/quantum_homeostatic_parts_observation_v3_recovery_cycle.py", "--seed", "20260708", "--out", str(v3_json), "--summary-csv", str(v3_summary), "--touch-csv", str(v3_touch)])
    assert_json(v3_json, "quantum_homeostatic_parts_observation_v3_recovery_cycle")
    require(v3_summary)
    require(v3_touch)

    v4_json = ROOT / "data/quantum_observation/quantum_homeostatic_parts_observation_v4_repair_vs_overdrive_seed20260708.json"
    v4_summary = ROOT / "data/quantum_observation/quantum_homeostatic_parts_observation_v4_repair_vs_overdrive_seed20260708_summary.csv"
    v4_touch = ROOT / "data/quantum_observation/quantum_homeostatic_parts_observation_v4_repair_vs_overdrive_seed20260708_selected_touch_rows.csv"
    run_cmd([py, "scripts/quantum_observation/quantum_homeostatic_parts_observation_v4_repair_vs_overdrive.py", "--seed", "20260708", "--out", str(v4_json), "--summary-csv", str(v4_summary), "--touch-csv", str(v4_touch)])
    assert_json(v4_json, "quantum_homeostatic_parts_observation_v4_repair_vs_overdrive")
    require(v4_summary)
    require(v4_touch)

    boundary_json = ROOT / "data/quantum_observation/quantum_boundary_homeostasis_v0_internal_feedback_seed20260708.json"
    boundary_summary = ROOT / "data/quantum_observation/quantum_boundary_homeostasis_v0_internal_feedback_seed20260708_summary.csv"
    boundary_trace = ROOT / "data/quantum_observation/quantum_boundary_homeostasis_v0_internal_feedback_seed20260708_selected_trace.csv"
    run_cmd([py, "scripts/quantum_observation/quantum_boundary_homeostasis_v0_internal_feedback.py", "--seed", "20260708", "--out", str(boundary_json), "--summary-csv", str(boundary_summary), "--trace-csv", str(boundary_trace)])
    assert_json(boundary_json, "quantum_boundary_homeostasis_v0_internal_feedback")
    require(boundary_summary)
    require(boundary_trace)

    print("OK: quantum observation logs regenerated")


if __name__ == "__main__":
    main()
