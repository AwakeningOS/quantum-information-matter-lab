#!/usr/bin/env python3
"""Minimal reproducibility checker for canonical raw logs.

The checker verifies that bootstrap scripts and promoted component scripts run
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

    membrane_json = ROOT / "data/contextual/contextual_membrane_v0_seed20260708.json"
    membrane_csv = ROOT / "data/contextual/contextual_membrane_v0_seed20260708_rows.csv"
    run_cmd([
        py,
        "scripts/contextual/contextual_membrane_v0.py",
        "--seed", "20260708",
        "--steps", "64",
        "--out", str(membrane_json),
        "--csv", str(membrane_csv),
    ])
    assert_json(membrane_json, "contextual_membrane_v0")
    if not membrane_csv.exists():
        raise AssertionError(f"missing CSV: {membrane_csv}")

    v1_json = ROOT / "data/contextual/contextual_membrane_v1_memory_ablation_seed20260708.json"
    v1_csv = ROOT / "data/contextual/contextual_membrane_v1_memory_ablation_seed20260708_summary.csv"
    run_cmd([
        py,
        "scripts/contextual/contextual_membrane_v1_memory_ablation.py",
        "--seed", "20260708",
        "--steps", "512",
        "--out", str(v1_json),
        "--csv", str(v1_csv),
    ])
    assert_json(v1_json, "contextual_membrane_v1_memory_ablation")
    if not v1_csv.exists():
        raise AssertionError(f"missing CSV: {v1_csv}")

    v2_json = ROOT / "data/contextual/contextual_membrane_v2_counterfactual_residue_seed20260708.json"
    v2_csv = ROOT / "data/contextual/contextual_membrane_v2_counterfactual_residue_seed20260708_summary.csv"
    run_cmd([
        py,
        "scripts/contextual/contextual_membrane_v2_counterfactual_residue.py",
        "--seed", "20260708",
        "--steps", "512",
        "--out", str(v2_json),
        "--csv", str(v2_csv),
    ])
    assert_json(v2_json, "contextual_membrane_v2_counterfactual_residue")
    if not v2_csv.exists():
        raise AssertionError(f"missing CSV: {v2_csv}")

    v3_json = ROOT / "data/contextual/contextual_membrane_v3_order_effect_seed20260708.json"
    v3_csv = ROOT / "data/contextual/contextual_membrane_v3_order_effect_seed20260708_summary.csv"
    run_cmd([
        py,
        "scripts/contextual/contextual_membrane_v3_order_effect.py",
        "--seed", "20260708",
        "--steps", "512",
        "--out", str(v3_json),
        "--csv", str(v3_csv),
    ])
    assert_json(v3_json, "contextual_membrane_v3_order_effect")
    if not v3_csv.exists():
        raise AssertionError(f"missing CSV: {v3_csv}")

    v4_json = ROOT / "data/contextual/contextual_membrane_v4_joint_boundary_seed20260708.json"
    v4_csv = ROOT / "data/contextual/contextual_membrane_v4_joint_boundary_seed20260708_summary.csv"
    run_cmd([
        py,
        "scripts/contextual/contextual_membrane_v4_joint_boundary.py",
        "--seed", "20260708",
        "--steps", "512",
        "--out", str(v4_json),
        "--csv", str(v4_csv),
    ])
    assert_json(v4_json, "contextual_membrane_v4_joint_boundary")
    if not v4_csv.exists():
        raise AssertionError(f"missing CSV: {v4_csv}")

    reactor_json = ROOT / "data/contextual/contextual_reactor_v0_membrane_to_flow_seed20260708.json"
    reactor_csv = ROOT / "data/contextual/contextual_reactor_v0_membrane_to_flow_seed20260708_summary.csv"
    run_cmd([
        py,
        "scripts/contextual/contextual_reactor_v0_membrane_to_flow.py",
        "--seed", "20260708",
        "--steps", "512",
        "--out", str(reactor_json),
        "--csv", str(reactor_csv),
    ])
    assert_json(reactor_json, "contextual_reactor_v0_membrane_to_flow")
    if not reactor_csv.exists():
        raise AssertionError(f"missing CSV: {reactor_csv}")

    print("OK: raw-log checks passed")


if __name__ == "__main__":
    main()
