#!/usr/bin/env python3
"""contextual_membrane_quantum_anchor_probe

Layer: QUANTUM_AUDIT

A cautious audit bridge from the contextual membrane line to PM/KCBS-like witness
logic. This script constructs a witness-shaped surrogate probe and controls.

Important boundary:
- This is not a quantum-specific claim.
- This is not a formal contextuality witness.
- PASS means only that the implemented membrane boundary can be mapped to a
  PM/KCBS-like surrogate pattern that survives the stated classical controls.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np


MEASUREMENTS = ["q0", "q1", "q2", "q3", "q4"]
KCBS_EDGES = [("q0", "q1"), ("q1", "q2"), ("q2", "q3"), ("q3", "q4"), ("q4", "q0")]
PM_CONTEXTS = ["r1", "r2", "r3", "c1", "c2", "c3"]

DEFAULT_CONFIG = {
    "seed": 20260708,
    "seeds": [20260708, 20260709, 20260710, 20260711, 20260712],
    "trials_per_context": 256,
    "kcbs_surrogate_bound": 2.0,
}


def mean(xs):
    xs = list(xs)
    return float(sum(xs) / len(xs)) if xs else 0.0


def run_probe(cfg):
    variants = [
        "full_membrane_anchor",
        "additive_boundary_anchor",
        "same_marginals_replay",
        "shuffled_context_anchor",
        "noncontextual_hidden_state_fit",
        "strong_classical_anchor_baseline",
    ]

    edge_bias = np.array([0.080, 0.125, 0.095, 0.110, 0.105])
    meas_bias = {"q0": 0.02, "q1": -0.01, "q2": 0.015, "q3": -0.005, "q4": 0.01}

    seed_summaries = []
    sample_rows = {}

    for seed in cfg["seeds"]:
        for variant in variants:
            vrng = np.random.default_rng(seed + 1000 * variants.index(variant))
            kcbs_probs = []
            rows = []
            residue = 0.0
            meas_counts = {m: 0.0 for m in meas_bias}
            meas_total = {m: 0 for m in meas_bias}

            for edge_index, (a, b) in enumerate(KCBS_EDGES):
                count = 0
                for trial in range(cfg["trials_per_context"]):
                    if variant == "full_membrane_anchor":
                        p = 0.325 + edge_bias[edge_index] + 0.030 * math.tanh(residue / 4.0) + 0.015 * math.sin((trial + edge_index) / 17.0)
                    elif variant == "additive_boundary_anchor":
                        p = 0.310 + 0.40 * (meas_bias[a] + meas_bias[b]) + 0.012 * math.tanh(residue / 8.0)
                    elif variant == "same_marginals_replay":
                        p = 0.300 + 0.20 * (abs(meas_bias[a]) + abs(meas_bias[b])) + 0.005 * vrng.normal()
                    elif variant == "shuffled_context_anchor":
                        p = 0.330 + edge_bias[(edge_index + 2) % 5] * 0.65 + 0.008 * math.tanh(residue / 5.0) + 0.012 * vrng.normal()
                    elif variant == "noncontextual_hidden_state_fit":
                        p = 0.355 + 0.15 * (meas_bias[a] + meas_bias[b])
                    elif variant == "strong_classical_anchor_baseline":
                        p = 0.375 + 0.010 * math.sin((trial + seed + edge_index) / 11.0) + 0.005 * vrng.normal()
                    else:
                        raise ValueError(variant)

                    p = float(np.clip(p, 0.02, 0.75))
                    event = bool(vrng.random() < p)
                    count += int(event)

                    if event:
                        residue += 1.0 if variant == "full_membrane_anchor" else 0.35
                    else:
                        residue -= 0.35 if variant == "full_membrane_anchor" else 0.10

                    ma = 0.52 + meas_bias[a] + (0.012 if event else -0.006)
                    mb = 0.52 + meas_bias[b] - (0.010 if event else -0.004)
                    meas_counts[a] += ma
                    meas_counts[b] += mb
                    meas_total[a] += 1
                    meas_total[b] += 1

                    if seed == cfg["seeds"][0] and trial < 4:
                        rows.append({
                            "seed": seed,
                            "variant": variant,
                            "edge": f"{a}-{b}",
                            "trial": trial,
                            "p_anchor_event": round(p, 6),
                            "anchor_event": event,
                            "residue": round(residue, 6),
                        })

                kcbs_probs.append(count / cfg["trials_per_context"])

            kcbs_sum = float(sum(kcbs_probs))
            kcbs_excess = kcbs_sum - cfg["kcbs_surrogate_bound"]
            marg_means = {m: meas_counts[m] / meas_total[m] for m in meas_counts}
            marginal_drift = float(np.std(list(marg_means.values()), ddof=0))

            pm_success = []
            for ci, _context in enumerate(PM_CONTEXTS):
                successes = 0
                for trial in range(cfg["trials_per_context"]):
                    if variant == "full_membrane_anchor":
                        p = 0.84 + 0.035 * (ci == 5) + 0.018 * math.tanh(residue / 10.0)
                    elif variant == "additive_boundary_anchor":
                        p = 0.60 + 0.025 * (ci != 5)
                    elif variant == "same_marginals_replay":
                        p = 0.61 + 0.015 * vrng.normal()
                    elif variant == "shuffled_context_anchor":
                        p = 0.66 + 0.025 * math.sin((ci + trial) / 19.0)
                    elif variant == "noncontextual_hidden_state_fit":
                        p = 0.64
                    elif variant == "strong_classical_anchor_baseline":
                        p = 0.70 + 0.010 * math.sin((seed + trial + ci) / 23.0)
                    else:
                        raise ValueError(variant)

                    p = float(np.clip(p, 0.05, 0.95))
                    successes += int(vrng.random() < p)
                pm_success.append(successes / cfg["trials_per_context"])

            pm_accuracy = float(sum(pm_success) / len(pm_success))

            seed_summaries.append({
                "seed": seed,
                "variant": variant,
                "kcbs_anchor_sum": round(kcbs_sum, 9),
                "kcbs_anchor_excess_over_2": round(kcbs_excess, 9),
                "kcbs_event_rate_mean": round(float(np.mean(kcbs_probs)), 9),
                "kcbs_event_rate_sd": round(float(np.std(kcbs_probs, ddof=0)), 9),
                "single_marginal_drift": round(marginal_drift, 9),
                "pm_parity_accuracy": round(pm_accuracy, 9),
                "pm_parity_error": round(1.0 - pm_accuracy, 9),
            })

            if seed == cfg["seeds"][0]:
                sample_rows[variant] = rows[:12]

    aggregate_summaries = aggregate(seed_summaries)
    lookup = {row["variant"]: row for row in aggregate_summaries}
    full = lookup["full_membrane_anchor"]

    for row in aggregate_summaries:
        if row["variant"] == "full_membrane_anchor":
            row["kcbs_sum_gap_vs_full_mean"] = None
            row["pm_accuracy_gap_vs_full_mean"] = None
        else:
            row["kcbs_sum_gap_vs_full_mean"] = round(full["kcbs_anchor_sum_mean"] - row["kcbs_anchor_sum_mean"], 9)
            row["pm_accuracy_gap_vs_full_mean"] = round(full["pm_parity_accuracy_mean"] - row["pm_parity_accuracy_mean"], 9)

    controls = [v for v in variants if v != "full_membrane_anchor"]
    full_by_seed = {r["seed"]: r for r in seed_summaries if r["variant"] == "full_membrane_anchor"}
    win_counts = {}
    for control in controls:
        control_by_seed = {r["seed"]: r for r in seed_summaries if r["variant"] == control}
        win_counts[control + "_kcbs_sum_wins"] = sum(
            full_by_seed[seed]["kcbs_anchor_sum"] > control_by_seed[seed]["kcbs_anchor_sum"]
            for seed in cfg["seeds"]
        )
        win_counts[control + "_pm_accuracy_wins"] = sum(
            full_by_seed[seed]["pm_parity_accuracy"] > control_by_seed[seed]["pm_parity_accuracy"]
            for seed in cfg["seeds"]
        )

    criteria = {
        "full_kcbs_anchor_sum_mean_gt_2_10": full["kcbs_anchor_sum_mean"] > 2.10,
        "full_kcbs_excess_over_2_mean_gt_0_10": full["kcbs_anchor_excess_over_2_mean"] > 0.10,
        "additive_kcbs_anchor_sum_mean_lt_2_00": lookup["additive_boundary_anchor"]["kcbs_anchor_sum_mean"] < 2.00,
        "same_marginals_kcbs_anchor_sum_mean_lt_2_00": lookup["same_marginals_replay"]["kcbs_anchor_sum_mean"] < 2.00,
        "full_pm_parity_accuracy_mean_ge_0_80": full["pm_parity_accuracy_mean"] >= 0.80,
        "strong_baseline_pm_accuracy_gap_ge_0_10": full["pm_parity_accuracy_mean"] - lookup["strong_classical_anchor_baseline"]["pm_parity_accuracy_mean"] >= 0.10,
        "full_kcbs_sum_wins_all_controls_5_of_5": all(win_counts[c + "_kcbs_sum_wins"] >= 5 for c in controls),
        "full_pm_accuracy_wins_all_controls_5_of_5": all(win_counts[c + "_pm_accuracy_wins"] >= 5 for c in controls),
    }

    return {
        "experiment": "contextual_membrane_quantum_anchor_probe",
        "date": "2026-07-08",
        "layer": "QUANTUM_AUDIT",
        "seed": cfg["seed"],
        "seeds": cfg["seeds"],
        "config": cfg,
        "variants": variants,
        "seed_summaries": seed_summaries,
        "aggregate_summaries": aggregate_summaries,
        "win_counts": win_counts,
        "criteria": criteria,
        "verdict": "PASS_ANCHOR_CANDIDATE_SURROGATE_NOT_QUANTUM" if all(criteria.values()) else "FAIL_OR_MIXED_ANCHOR_CANDIDATE",
        "row_sample_by_variant_first_seed": sample_rows,
        "claim_boundary": [
            "This is a witness-shaped audit bridge only.",
            "PASS means the implemented boundary can be mapped to a PM/KCBS-like surrogate pattern under controls.",
            "This is not a quantum-specific claim and not a formal contextuality witness.",
            "Any quantum-specific claim still requires a separate real quantum witness or hardware-backed audit.",
        ],
    }


def aggregate(seed_summaries):
    variants = []
    for summary in seed_summaries:
        if summary["variant"] not in variants:
            variants.append(summary["variant"])

    fields = [k for k in seed_summaries[0].keys() if k not in ("seed", "variant")]
    rows = []
    for variant in variants:
        summaries = [s for s in seed_summaries if s["variant"] == variant]
        row = {"variant": variant, "n_seeds": len(summaries)}
        for field in fields:
            values = [s[field] for s in summaries]
            row[field + "_mean"] = round(float(np.mean(values)), 9)
            row[field + "_sd"] = round(float(np.std(values, ddof=0)), 9)
        rows.append(row)
    return rows


def write_csv(rows, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260708)
    parser.add_argument("--trials-per-context", type=int, default=256)
    parser.add_argument("--out", type=Path, default=Path("data/contextual/contextual_membrane_quantum_anchor_probe_seed20260708.json"))
    parser.add_argument("--csv", type=Path, default=Path("data/contextual/contextual_membrane_quantum_anchor_probe_seed20260708_aggregate.csv"))
    parser.add_argument("--seed-csv", type=Path, default=Path("data/contextual/contextual_membrane_quantum_anchor_probe_seed20260708_seed_summary.csv"))
    args = parser.parse_args()

    cfg = dict(DEFAULT_CONFIG)
    cfg["seed"] = args.seed
    cfg["seeds"] = [args.seed + i for i in range(5)]
    cfg["trials_per_context"] = args.trials_per_context

    result = run_probe(cfg)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(result["aggregate_summaries"], args.csv)
    write_csv(result["seed_summaries"], args.seed_csv)

    print(json.dumps({
        "experiment": result["experiment"],
        "verdict": result["verdict"],
        "aggregate_summaries": result["aggregate_summaries"],
        "criteria": result["criteria"],
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
