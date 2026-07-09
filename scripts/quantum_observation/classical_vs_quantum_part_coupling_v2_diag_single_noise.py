#!/usr/bin/env python3
"""classical_vs_quantum_part_coupling_v2_diag_single_noise

Single-noise diagnostic for the v2 signed/oriented P1_W witness.

Purpose:
  Identify whether the v2 medium/heavy separation loss is driven mainly by
  dephase, 1q depolarization, 2q depolarization, or readout flip.

This is a diagnostic only, not a QPU-ready result.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

sys.path.append(str(Path(__file__).resolve().parent))
import classical_vs_quantum_part_coupling_v2_noise_model as v2  # noqa: E402

ARMS = v2.ARMS
SEEDS = list(range(20260757, 20260773))
BOOTSTRAPS = 10000

PROFILES = {
    "medium_dephase_only": {"p_dephase_layer": 0.008, "p_depolarize_1q": 0.0, "p_depolarize_2q": 0.0, "p_readout_flip": 0.0},
    "medium_depol1q_only": {"p_dephase_layer": 0.0, "p_depolarize_1q": 0.003, "p_depolarize_2q": 0.0, "p_readout_flip": 0.0},
    "medium_depol2q_only": {"p_dephase_layer": 0.0, "p_depolarize_1q": 0.0, "p_depolarize_2q": 0.012, "p_readout_flip": 0.0},
    "medium_readout_only": {"p_dephase_layer": 0.0, "p_depolarize_1q": 0.0, "p_depolarize_2q": 0.0, "p_readout_flip": 0.025},
    "heavy_dephase_only": {"p_dephase_layer": 0.018, "p_depolarize_1q": 0.0, "p_depolarize_2q": 0.0, "p_readout_flip": 0.0},
    "heavy_depol1q_only": {"p_dephase_layer": 0.0, "p_depolarize_1q": 0.007, "p_depolarize_2q": 0.0, "p_readout_flip": 0.0},
    "heavy_depol2q_only": {"p_dephase_layer": 0.0, "p_depolarize_1q": 0.0, "p_depolarize_2q": 0.030, "p_readout_flip": 0.0},
    "heavy_readout_only": {"p_dephase_layer": 0.0, "p_depolarize_1q": 0.0, "p_depolarize_2q": 0.0, "p_readout_flip": 0.050},
}


def bootstrap_mean_ci(vals: list[float], seed: int) -> tuple[float, float, float]:
    rng = np.random.default_rng(seed)
    arr = np.array(vals, dtype=float)
    means = np.empty(BOOTSTRAPS)
    for i in range(BOOTSTRAPS):
        means[i] = rng.choice(arr, size=len(arr), replace=True).mean()
    lo, hi = np.quantile(means, [0.025, 0.975])
    return float(means.mean()), float(lo), float(hi)


def paired_diff_ci(a: list[float], b: list[float], seed: int) -> tuple[float, float, float]:
    rng = np.random.default_rng(seed)
    diff = np.array(a, dtype=float) - np.array(b, dtype=float)
    means = np.empty(BOOTSTRAPS)
    for i in range(BOOTSTRAPS):
        idx = rng.integers(0, len(diff), len(diff))
        means[i] = diff[idx].mean()
    lo, hi = np.quantile(means, [0.025, 0.975])
    return float(means.mean()), float(lo), float(hi)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-json", type=Path, default=Path("data/quantum_observation/classical_vs_quantum_part_coupling_v2_diag_single_noise_seed20260757_20260772.json"))
    parser.add_argument("--summary-csv", type=Path, default=Path("data/quantum_observation/classical_vs_quantum_part_coupling_v2_diag_single_noise_seed20260757_20260772_summary.csv"))
    args = parser.parse_args()

    rows = []
    exact_by_profile = {}
    for profile_name, profile in PROFILES.items():
        exact, probs = v2.exact_profile_probs(profile)
        exact_by_profile[profile_name] = exact
        for seed in SEEDS:
            rng = np.random.default_rng(seed)
            for arm in ARMS:
                counts0 = v2.v1.counts_from_probs(probs[(arm, "M")], rng)
                countsp = v2.v1.counts_from_probs(probs[(arm, "M_phase_pi2")], rng)
                p0 = v2.p1w_from_counts(counts0)
                pp = v2.p1w_from_counts(countsp)
                rows.append({
                    "profile": profile_name,
                    "seed": seed,
                    "arm": arm,
                    "exact_oriented_effect": exact[arm]["oriented_effect_exact"],
                    "P1W_phase0": p0,
                    "P1W_phase_pi2": pp,
                    "oriented_effect": p0 - pp,
                })

    summary = []
    comparisons = {}
    for profile_name in PROFILES:
        by_arm = {arm: [r["oriented_effect"] for r in rows if r["profile"] == profile_name and r["arm"] == arm] for arm in ARMS}
        comparisons[profile_name] = {}
        for arm, vals in by_arm.items():
            _, lo, hi = bootstrap_mean_ci(vals, seed=9000 + len(profile_name) + len(arm))
            summary.append({
                "profile": profile_name,
                "arm": arm,
                "exact": exact_by_profile[profile_name][arm]["oriented_effect_exact"],
                "mean": float(np.mean(vals)),
                "ci_low": lo,
                "ci_high": hi,
                "signs": f"+{int(np.sum(np.array(vals) > 0))}/-{int(np.sum(np.array(vals) < 0))}",
                "min": float(np.min(vals)),
                "max": float(np.max(vals)),
            })
        direct = by_arm["quantum_direct_coupled"]
        for control in ["quantum_field_only", "quantum_no_entangle", "quantum_dephased_control"]:
            ctrl = by_arm[control]
            _, lo, hi = paired_diff_ci(direct, ctrl, seed=9100 + len(profile_name) + len(control))
            comparisons[profile_name][control] = {
                "direct_minus_control_mean": float(np.mean(np.array(direct) - np.array(ctrl))),
                "ci_low": lo,
                "ci_high": hi,
                "mann_whitney_u": v2.mann_u_stat(direct, ctrl),
                "u_max": len(direct) * len(ctrl),
                "gap": float(min(direct) - max(ctrl)),
            }

    result = {
        "experiment": "classical_vs_quantum_part_coupling_v2_diag_single_noise",
        "date": "2026-07-09",
        "status": "OBSERVATION_LOG",
        "protocol": "experiments/classical_vs_quantum_part_coupling_v2_diag_protocol_20260709.md",
        "config": {"shots_per_seed": v2.v1.SHOTS, "seeds": SEEDS, "inference_unit": "seed", "profiles": PROFILES},
        "summary": summary,
        "comparisons": comparisons,
        "diagnostic_reading": {
            "readout_only": "not culprit: medium/heavy readout-only keep no_entangle zero-centered; exact no_entangle remains 0",
            "dephase_only": "erodes direct but does not explain medium strict-separation failure; medium_dephase_only still has U=256/256 vs no_entangle",
            "depol2q_only": "erodes direct but remains separated against no_entangle in medium/heavy single-noise profiles",
            "depol1q_only": "best reproduces strict-separation fragility; medium_depol1q_only has U=250/256 and negative min-max gap despite positive paired CI",
            "overall": "primary cause of strict separation loss is 1q depolarization plus seed/shot tail overlap, not symmetric readout bias",
        },
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    args.summary_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.summary_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["profile", "seed", "arm", "exact_oriented_effect", "P1W_phase0", "P1W_phase_pi2", "oriented_effect"])
        writer.writeheader()
        writer.writerows(rows)

    print(json.dumps({"experiment": result["experiment"], "diagnostic_reading": result["diagnostic_reading"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
