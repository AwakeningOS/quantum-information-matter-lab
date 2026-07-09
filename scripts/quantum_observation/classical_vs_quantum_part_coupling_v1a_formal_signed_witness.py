#!/usr/bin/env python3
"""classical_vs_quantum_part_coupling_v1a_formal_signed_witness

Formal v1a run.

This run follows the v1a protocol:
- signed/oriented estimator
- fresh formal seed block 20260725-20260740
- seed-level inference, not pooled-shot inference
- Mann-Whitney separation against no_entangle

It reuses the v1 circuit implementation.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
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
FORMAL_SEEDS = list(range(20260725, 20260741))
BOOTSTRAPS = 10000


def jfloat(x: Any, ndigits: int = 12) -> float:
    return round(float(x), ndigits)


def p1w_from_counts(counts: dict[str, int]) -> float:
    total = sum(counts.values())
    return sum(count for bits, count in counts.items() if bits[3] == "1") / total


def bootstrap_mean_ci(vals: list[float], seed: int = 4242) -> tuple[float, float, float]:
    rng = np.random.default_rng(seed)
    arr = np.array(vals, dtype=float)
    means = np.empty(BOOTSTRAPS)
    for i in range(BOOTSTRAPS):
        means[i] = rng.choice(arr, size=len(arr), replace=True).mean()
    lo, hi = np.quantile(means, [0.025, 0.975])
    return float(means.mean()), float(lo), float(hi)


def paired_diff_ci(a: list[float], b: list[float], seed: int = 4243) -> tuple[float, float, float]:
    rng = np.random.default_rng(seed)
    diff = np.array(a, dtype=float) - np.array(b, dtype=float)
    means = np.empty(BOOTSTRAPS)
    for i in range(BOOTSTRAPS):
        idx = rng.integers(0, len(diff), size=len(diff))
        means[i] = diff[idx].mean()
    lo, hi = np.quantile(means, [0.025, 0.975])
    return float(means.mean()), float(lo), float(hi)


def mann_u_stat(x: list[float], y: list[float]) -> float:
    u = 0.0
    for xi in x:
        for yj in y:
            if xi > yj:
                u += 1.0
            elif xi == yj:
                u += 0.5
    return u


def exact_mann_p_if_u_max(n: int, m: int, u: float) -> float | None:
    if u == n * m:
        return 1.0 / math.comb(n + m, n)
    return None


def exact_probs() -> tuple[dict[str, dict[str, float]], dict[tuple[str, str], np.ndarray]]:
    exact: dict[str, dict[str, float]] = {}
    probs: dict[tuple[str, str], np.ndarray] = {}
    for arm in ARMS:
        rho0 = v1.quantum_probe(arm, "M", 0.0)
        rhop = v1.quantum_probe(arm, "M", math.pi / 2)
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
        default=Path("data/quantum_observation/classical_vs_quantum_part_coupling_v1a_formal_seed20260725_20260740.json"),
    )
    parser.add_argument(
        "--summary-csv",
        type=Path,
        default=Path("data/quantum_observation/classical_vs_quantum_part_coupling_v1a_formal_seed20260725_20260740_summary.csv"),
    )
    args = parser.parse_args()

    exact, probs = exact_probs()
    rows = []
    raw_counts: dict[str, dict[str, dict[str, dict[str, int]]]] = {}

    for seed in FORMAL_SEEDS:
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

    by_arm = {
        arm: [float(r["oriented_effect"]) for r in rows if r["arm"] == arm]
        for arm in ARMS
    }

    summary = []
    for arm, vals in by_arm.items():
        bmean, blo, bhi = bootstrap_mean_ci(vals)
        summary.append(
            {
                "arm": arm,
                "exact_oriented_effect": exact[arm]["oriented_effect_exact"],
                "mean_oriented_effect": jfloat(np.mean(vals)),
                "std_oriented_effect": jfloat(np.std(vals, ddof=1)),
                "min_oriented_effect": jfloat(np.min(vals)),
                "max_oriented_effect": jfloat(np.max(vals)),
                "positive_count": int(np.sum(np.array(vals) > 0)),
                "negative_count": int(np.sum(np.array(vals) < 0)),
                "zero_count": int(np.sum(np.array(vals) == 0)),
                "bootstrap_mean": jfloat(bmean),
                "bootstrap_ci95_low": jfloat(blo),
                "bootstrap_ci95_high": jfloat(bhi),
            }
        )

    comparisons = {}
    direct = by_arm["quantum_direct_coupled"]
    for control in ["quantum_field_only", "quantum_no_entangle", "quantum_dephased_control"]:
        ctrl = by_arm[control]
        dmean, dlo, dhi = paired_diff_ci(direct, ctrl)
        u = mann_u_stat(direct, ctrl)
        comparisons[control] = {
            "direct_minus_control_seed_mean": jfloat(dmean),
            "direct_minus_control_ci95_low": jfloat(dlo),
            "direct_minus_control_ci95_high": jfloat(dhi),
            "mann_whitney_u": jfloat(u),
            "mann_whitney_u_max": len(direct) * len(ctrl),
            "one_sided_exact_p_if_u_max": exact_mann_p_if_u_max(len(direct), len(ctrl), u),
            "direct_min_minus_control_max": jfloat(min(direct) - max(ctrl)),
        }

    direct_summary = next(s for s in summary if s["arm"] == "quantum_direct_coupled")
    no_summary = next(s for s in summary if s["arm"] == "quantum_no_entangle")
    field_summary = next(s for s in summary if s["arm"] == "quantum_field_only")
    deph_summary = next(s for s in summary if s["arm"] == "quantum_dephased_control")

    main_pass = direct_summary["bootstrap_ci95_low"] > 0
    leakage_pass = (
        no_summary["bootstrap_ci95_low"] <= 0 <= no_summary["bootstrap_ci95_high"]
        and no_summary["positive_count"] > 0
        and no_summary["negative_count"] > 0
    )
    separation_pass = (
        comparisons["quantum_no_entangle"]["one_sided_exact_p_if_u_max"] is not None
        and comparisons["quantum_no_entangle"]["one_sided_exact_p_if_u_max"] < 0.01
    )
    field_support = field_summary["bootstrap_ci95_low"] <= 0 <= field_summary["bootstrap_ci95_high"]
    deph_support = (
        deph_summary["bootstrap_ci95_low"] <= 0 <= deph_summary["bootstrap_ci95_high"]
        and comparisons["quantum_dephased_control"]["direct_minus_control_ci95_low"] > 0
    )

    if main_pass and leakage_pass and separation_pass:
        verdict = "PASS_SIGNED_MULTI_SEED_WITNESS_SURVIVES"
    elif main_pass:
        verdict = "PARTIAL_SIGNED_WITNESS_SURVIVES"
    elif not leakage_pass:
        verdict = "SIGNED_WITNESS_LEAKAGE_SUSPECTED"
    else:
        verdict = "SIGNED_WITNESS_NOT_SEPARATED"

    result = {
        "experiment": "classical_vs_quantum_part_coupling_v1a_formal_signed_witness",
        "date": "2026-07-09",
        "status": "OBSERVATION_LOG",
        "protocol": "experiments/classical_vs_quantum_part_coupling_v1a_protocol_20260709.md",
        "config": {
            "shots_per_seed": v1.SHOTS,
            "formal_seeds": FORMAL_SEEDS,
            "bootstrap_resamples": BOOTSTRAPS,
            "estimator": "oriented_phase_effect_P1W = P1_W(phaseM=0,M perturb) - P1_W(phaseM=pi/2,M perturb)",
            "inference_unit": "seed",
            "orientation_note": "v1 exact signed effect under pi/2 - 0 was negative for direct_coupled; v1a reports 0 - pi/2 so a true direct effect is positive.",
            "diagnostic_seeds_not_reused": True,
            "arms": ARMS,
        },
        "exact": exact,
        "seed_rows": rows,
        "summary": summary,
        "comparisons": comparisons,
        "criteria": {
            "main_pass": bool(main_pass),
            "leakage_pass": bool(leakage_pass),
            "separation_pass": bool(separation_pass),
            "field_support": bool(field_support),
            "dephased_support": bool(deph_support),
            "verdict": verdict,
        },
        "raw_counts": raw_counts,
        "notes": [
            "This formal v1a run uses fresh seeds not used in the v1a diagnostic.",
            "Primary inference treats seed as the independent unit.",
            "No noise model and no QPU submission are included.",
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

    print(json.dumps({"experiment": result["experiment"], "summary": summary, "comparisons": comparisons, "criteria": result["criteria"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
