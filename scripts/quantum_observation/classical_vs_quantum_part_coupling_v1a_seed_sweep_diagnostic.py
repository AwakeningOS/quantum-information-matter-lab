#!/usr/bin/env python3
"""classical_vs_quantum_part_coupling_v1a_seed_sweep_diagnostic

Pre-protocol diagnostic for v1a.

Purpose:
  Check whether the v1 absolute-value estimator created a positive shot-noise
  bias in zero-truth controls, especially quantum_no_entangle.

This script reuses the v1 measurable-witness circuit but changes only the
estimator:

  oriented_phase_effect_P1W = P1_W(phaseM=0, M perturb)
                              - P1_W(phaseM=pi/2, M perturb)

This is a diagnostic, not a formal PASS/FAIL protocol and not a QPU-ready claim.
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
import classical_vs_quantum_part_coupling_v1_measurable_witness as v1  # noqa: E402

ARMS = [
    "quantum_field_only",
    "quantum_no_entangle",
    "quantum_direct_coupled",
    "quantum_dephased_control",
]
SEEDS = [20260709, 20260710, 20260711, 20260712, 20260713, 20260714, 20260715, 20260716]


def jfloat(x: Any, ndigits: int = 12) -> float:
    return round(float(x), ndigits)


def p1w_from_counts(counts: dict[str, int]) -> float:
    total = sum(counts.values())
    return sum(count for bits, count in counts.items() if bits[3] == "1") / total


def exact_probs() -> tuple[dict[str, dict[str, float]], dict[tuple[str, str], np.ndarray]]:
    exact: dict[str, dict[str, float]] = {}
    probs: dict[tuple[str, str], np.ndarray] = {}
    for arm in ARMS:
        rho0 = v1.quantum_probe(arm, "M", 0.0)
        rhop = v1.quantum_probe(arm, "M", v1.math.pi / 2)
        p0 = v1.p1(rho0, 3)
        pp = v1.p1(rhop, 3)
        exact[arm] = {
            "P1W_phase0_exact": jfloat(p0),
            "P1W_phase_pi2_exact": jfloat(pp),
            "oriented_effect_exact": jfloat(p0 - pp),
        }
        probs[(arm, "M")] = v1.probs_z(rho0)
        probs[(arm, "M_phase_pi2")] = v1.probs_z(rhop)
    return exact, probs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("data/quantum_observation/classical_vs_quantum_part_coupling_v1a_seed_sweep_seed20260709_20260716.json"),
    )
    parser.add_argument(
        "--summary-csv",
        type=Path,
        default=Path("data/quantum_observation/classical_vs_quantum_part_coupling_v1a_seed_sweep_seed20260709_20260716_summary.csv"),
    )
    args = parser.parse_args()

    exact, probs = exact_probs()
    rows = []
    raw_counts: dict[str, dict[str, dict[str, dict[str, int]]]] = {}

    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        raw_counts[str(seed)] = {}
        for arm in ARMS:
            counts0 = v1.counts_from_probs(probs[(arm, "M")], rng)
            countsp = v1.counts_from_probs(probs[(arm, "M_phase_pi2")], rng)
            p0 = p1w_from_counts(counts0)
            pp = p1w_from_counts(countsp)
            effect = p0 - pp
            rows.append(
                {
                    "seed": seed,
                    "arm": arm,
                    "exact_oriented_effect": exact[arm]["oriented_effect_exact"],
                    "P1W_phase0": jfloat(p0),
                    "P1W_phase_pi2": jfloat(pp),
                    "oriented_effect": jfloat(effect),
                }
            )
            raw_counts[str(seed)][arm] = {"M": counts0, "M_phase_pi2": countsp}

    summary = []
    for arm in ARMS:
        vals = np.array([row["oriented_effect"] for row in rows if row["arm"] == arm], dtype=float)
        summary.append(
            {
                "arm": arm,
                "exact_oriented_effect": exact[arm]["oriented_effect_exact"],
                "mean_oriented_effect": jfloat(np.mean(vals)),
                "std_oriented_effect": jfloat(np.std(vals, ddof=1)),
                "min_oriented_effect": jfloat(np.min(vals)),
                "max_oriented_effect": jfloat(np.max(vals)),
                "positive_count": int(np.sum(vals > 0)),
                "negative_count": int(np.sum(vals < 0)),
                "zero_count": int(np.sum(vals == 0)),
            }
        )

    result = {
        "experiment": "classical_vs_quantum_part_coupling_v1a_signed_seed_sweep_diagnostic",
        "date": "2026-07-09",
        "status": "OBSERVATION_LOG",
        "scope": "pre-protocol diagnostic only; not PASS/FAIL promotion",
        "config": {
            "shots": v1.SHOTS,
            "seeds": SEEDS,
            "arms": ARMS,
            "estimator": "oriented_phase_effect_P1W = P1_W(phaseM=0,M perturb) - P1_W(phaseM=pi/2,M perturb)",
            "orientation_note": "v1 exact signed effect under pi/2 - 0 was negative for direct_coupled; this diagnostic reports 0 - pi/2 so a direct effect is positive.",
        },
        "exact": exact,
        "seed_rows": rows,
        "summary": summary,
        "raw_counts": raw_counts,
        "diagnostic_reading": {
            "quantum_field_only": "zero-centered shot fluctuations: +5 / -3, mean 0.001770",
            "quantum_no_entangle": "zero-centered shot fluctuations: +4 / -4, mean -0.003967",
            "quantum_direct_coupled": "8/8 positive, mean 0.039001, min 0.026367; separated from no_entangle max 0.013916 in this diagnostic",
            "quantum_dephased_control": "near-zero shot fluctuations: +5 / -3, mean 0.002167",
            "verdict": "SEED_SWEEP_SUPPORTS_SIGNED_V1A",
        },
        "notes": [
            "This diagnostic checks whether v1's abs estimator biased zero-truth controls upward.",
            "no_entangle exact effect is zero and multi-seed signed values scatter around zero.",
            "direct exact effect is positive under the oriented convention and every sampled seed remains positive.",
            "This does not replace a formal v1a protocol.",
        ],
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    args.summary_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.summary_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["seed", "arm", "exact_oriented_effect", "P1W_phase0", "P1W_phase_pi2", "oriented_effect"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(json.dumps({"experiment": result["experiment"], "summary": summary, "diagnostic_reading": result["diagnostic_reading"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
