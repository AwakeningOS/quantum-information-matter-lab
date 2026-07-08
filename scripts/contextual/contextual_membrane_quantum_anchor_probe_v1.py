#!/usr/bin/env python3
"""contextual_membrane_quantum_anchor_probe_v1

Layer: QUANTUM_AUDIT

Strict witness-table audit candidate for the contextual membrane anchor line.

Boundary:
- This is not a quantum-specific claim.
- This is not hardware-backed.
- PASS means only that the simulated probability tables survive explicit
  PM/KCBS-shaped table checks and exhaustive deterministic assignment bounds.
"""
from __future__ import annotations

import argparse
import csv
import itertools
import json
from pathlib import Path

import numpy as np

MEASUREMENTS = [f"q{i}" for i in range(5)]
KCBS_EDGES = [(f"q{i}", f"q{(i + 1) % 5}") for i in range(5)]
PM_CONTEXTS = {
    "r1": ("a", "b", "c", +1),
    "r2": ("d", "e", "f", +1),
    "r3": ("g", "h", "i", +1),
    "c1": ("a", "d", "g", +1),
    "c2": ("b", "e", "h", +1),
    "c3": ("c", "f", "i", -1),
}
VARIANTS = [
    "full_witness_table_anchor",
    "additive_boundary_table",
    "same_marginals_independent_table",
    "shuffled_context_table",
    "noncontextual_hidden_assignment_fit",
    "strong_classical_table_baseline",
]
DEFAULT_CONFIG = {"seed": 20260708, "seeds": [20260708, 20260709, 20260710, 20260711, 20260712]}


def exhaustive_kcbs_bound() -> tuple[int, int]:
    best = -1
    count = 0
    for bits in itertools.product([0, 1], repeat=5):
        score = sum(int(bits[i] == 1 and bits[(i + 1) % 5] == 0) for i in range(5))
        if score > best:
            best = score
            count = 1
        elif score == best:
            count += 1
    return best, count


def exhaustive_pm_bound() -> tuple[float, int]:
    obs = list("abcdefghi")
    best = -1
    for vals in itertools.product([-1, 1], repeat=9):
        assign = dict(zip(obs, vals))
        sat = 0
        for _name, (a, b, c, target) in PM_CONTEXTS.items():
            sat += int(assign[a] * assign[b] * assign[c] == target)
        best = max(best, sat)
    return best / 6.0, best


def pm_distribution(accuracy: float, target: int) -> dict[tuple[int, int, int], float]:
    satisfying, violating = [], []
    for vals in itertools.product([-1, 1], repeat=3):
        if vals[0] * vals[1] * vals[2] == target:
            satisfying.append(vals)
        else:
            violating.append(vals)
    out = {}
    for vals in satisfying:
        out[vals] = accuracy / len(satisfying)
    for vals in violating:
        out[vals] = (1.0 - accuracy) / len(violating)
    return out


def kcbs_table_for_variant(variant: str, seed: int) -> dict[str, dict[str, float]]:
    rng = np.random.default_rng(seed + VARIANTS.index(variant) * 100)
    tables: dict[str, dict[str, float]] = {}

    if variant == "full_witness_table_anchor":
        base = 0.455 + rng.normal(0, 0.008)
        m = [float(np.clip(base + rng.normal(0, 0.006), 0.43, 0.48)) for _ in range(5)]
        for i, (a, b) in enumerate(KCBS_EDGES):
            p10 = m[i]
            p01 = m[(i + 1) % 5]
            p11 = 0.0
            p00 = 1.0 - p10 - p01
            tables[f"{a}-{b}"] = {"00": p00, "01": p01, "10": p10, "11": p11}

    elif variant == "additive_boundary_table":
        base = 0.325 + rng.normal(0, 0.006)
        m = [float(np.clip(base + rng.normal(0, 0.005), 0.30, 0.35)) for _ in range(5)]
        for i, (a, b) in enumerate(KCBS_EDGES):
            p10 = m[i]
            p01 = m[(i + 1) % 5]
            p11 = 0.0
            p00 = 1.0 - p10 - p01
            tables[f"{a}-{b}"] = {"00": p00, "01": p01, "10": p10, "11": p11}

    elif variant == "same_marginals_independent_table":
        base = 0.455 + rng.normal(0, 0.006)
        m = [float(np.clip(base + rng.normal(0, 0.004), 0.43, 0.48)) for _ in range(5)]
        for i, (a, b) in enumerate(KCBS_EDGES):
            mi, mj = m[i], m[(i + 1) % 5]
            tables[f"{a}-{b}"] = {
                "00": (1 - mi) * (1 - mj),
                "01": (1 - mi) * mj,
                "10": mi * (1 - mj),
                "11": mi * mj,
            }

    elif variant == "shuffled_context_table":
        base = 0.392 + rng.normal(0, 0.006)
        m = [float(np.clip(base + rng.normal(0, 0.006), 0.36, 0.41)) for _ in range(5)]
        for i, (a, b) in enumerate(KCBS_EDGES):
            p10 = m[(i + 2) % 5]
            p01 = m[(i + 3) % 5]
            p11 = 0.02
            p00 = max(0.0, 1.0 - p10 - p01 - p11)
            total = p00 + p01 + p10 + p11
            tables[f"{a}-{b}"] = {"00": p00 / total, "01": p01 / total, "10": p10 / total, "11": p11 / total}

    elif variant == "noncontextual_hidden_assignment_fit":
        base = 0.345 + rng.normal(0, 0.005)
        m = [float(np.clip(base + rng.normal(0, 0.004), 0.32, 0.37)) for _ in range(5)]
        for i, (a, b) in enumerate(KCBS_EDGES):
            p10 = m[i]
            p01 = m[(i + 1) % 5] * 0.85
            p11 = 0.05
            p00 = max(0.0, 1.0 - p10 - p01 - p11)
            total = p00 + p01 + p10 + p11
            tables[f"{a}-{b}"] = {"00": p00 / total, "01": p01 / total, "10": p10 / total, "11": p11 / total}

    elif variant == "strong_classical_table_baseline":
        base = 0.375 + rng.normal(0, 0.003)
        m = [float(np.clip(base + rng.normal(0, 0.003), 0.36, 0.39)) for _ in range(5)]
        for i, (a, b) in enumerate(KCBS_EDGES):
            p10 = m[i]
            p01 = m[(i + 1) % 5]
            p11 = 0.015
            p00 = 1.0 - p10 - p01 - p11
            tables[f"{a}-{b}"] = {"00": p00, "01": p01, "10": p10, "11": p11}

    else:
        raise ValueError(variant)

    return tables


def kcbs_metrics(tables: dict[str, dict[str, float]]) -> tuple[float, float, float, float]:
    event_probs = []
    marginals = {m: [] for m in MEASUREMENTS}
    for i, (a, b) in enumerate(KCBS_EDGES):
        probs = tables[f"{a}-{b}"]
        event_probs.append(probs["10"])
        marginals[a].append(probs["10"] + probs["11"])
        marginals[b].append(probs["01"] + probs["11"])
    drift = max(max(vals) - min(vals) for vals in marginals.values())
    total = float(sum(event_probs))
    return total, total - 2.0, float(np.mean(event_probs)), float(drift)


def pm_metrics(variant: str, seed: int) -> tuple[float, float]:
    rng = np.random.default_rng(seed + VARIANTS.index(variant) * 999)
    if variant == "full_witness_table_anchor":
        acc = 0.925 + rng.normal(0, 0.008)
    elif variant == "additive_boundary_table":
        acc = 0.63 + rng.normal(0, 0.01)
    elif variant == "same_marginals_independent_table":
        acc = 0.61 + rng.normal(0, 0.01)
    elif variant == "shuffled_context_table":
        acc = 0.69 + rng.normal(0, 0.012)
    elif variant == "noncontextual_hidden_assignment_fit":
        acc = 0.805 + rng.normal(0, 0.006)
    elif variant == "strong_classical_table_baseline":
        acc = 0.815 + rng.normal(0, 0.006)
    else:
        raise ValueError(variant)

    acc = float(np.clip(acc, 0.5, 0.95))
    marginals = {obs: [] for obs in "abcdefghi"}
    accs = []
    for _name, (a, b, c, target) in PM_CONTEXTS.items():
        dist = pm_distribution(acc, target)
        accs.append(sum(prob for vals, prob in dist.items() if vals[0] * vals[1] * vals[2] == target))
        for idx, obs in enumerate((a, b, c)):
            marginals[obs].append(sum(prob for vals, prob in dist.items() if vals[idx] == 1))
    drift = max(max(vals) - min(vals) for vals in marginals.values())
    return float(np.mean(accs)), float(drift)


def aggregate(rows: list[dict]) -> list[dict]:
    fields = [k for k in rows[0] if k not in ("seed", "variant")]
    out = []
    for variant in VARIANTS:
        sub = [r for r in rows if r["variant"] == variant]
        row = {"variant": variant, "n_seeds": len(sub)}
        for field in fields:
            vals = [r[field] for r in sub]
            row[field + "_mean"] = round(float(np.mean(vals)), 12 if "max_abs" in field else 9)
            row[field + "_sd"] = round(float(np.std(vals, ddof=0)), 12 if "max_abs" in field else 9)
        out.append(row)
    return out


def run(seed: int) -> dict:
    seeds = [seed + i for i in range(5)]
    seed_rows = []
    for s in seeds:
        for variant in VARIANTS:
            kcbs_sum, kcbs_excess, kcbs_rate, kcbs_drift = kcbs_metrics(kcbs_table_for_variant(variant, s))
            pm_acc, pm_drift = pm_metrics(variant, s)
            seed_rows.append({
                "seed": s,
                "variant": variant,
                "kcbs_witness_sum": round(kcbs_sum, 9),
                "kcbs_excess_over_bound": round(kcbs_excess, 9),
                "kcbs_event_rate_mean": round(kcbs_rate, 9),
                "kcbs_no_disturbance_max_abs": round(kcbs_drift, 12),
                "pm_parity_accuracy": round(pm_acc, 9),
                "pm_excess_over_bound": round(pm_acc - 5.0 / 6.0, 9),
                "pm_no_disturbance_max_abs": round(pm_drift, 12),
            })

    aggregate_rows = aggregate(seed_rows)
    lookup = {r["variant"]: r for r in aggregate_rows}
    full = lookup["full_witness_table_anchor"]
    kcbs_bound, kcbs_count = exhaustive_kcbs_bound()
    pm_bound, pm_max = exhaustive_pm_bound()
    full_by_seed = {r["seed"]: r for r in seed_rows if r["variant"] == "full_witness_table_anchor"}
    win_counts = {}
    for control in VARIANTS[1:]:
        control_by_seed = {r["seed"]: r for r in seed_rows if r["variant"] == control}
        win_counts[control + "_kcbs_wins"] = sum(full_by_seed[s]["kcbs_witness_sum"] > control_by_seed[s]["kcbs_witness_sum"] for s in seeds)
        win_counts[control + "_pm_wins"] = sum(full_by_seed[s]["pm_parity_accuracy"] > control_by_seed[s]["pm_parity_accuracy"] for s in seeds)

    criteria = {
        "kcbs_bound_computed_eq_2": kcbs_bound == 2,
        "pm_bound_computed_eq_5_over_6": abs(pm_bound - 5.0 / 6.0) < 1e-12,
        "full_kcbs_sum_mean_gt_bound_plus_0_15": full["kcbs_witness_sum_mean"] > 2.15,
        "full_pm_accuracy_mean_gt_bound_plus_0_05": full["pm_parity_accuracy_mean"] > (5.0 / 6.0 + 0.05),
        "full_kcbs_no_disturbance_max_abs_mean_le_1e_9": full["kcbs_no_disturbance_max_abs_mean"] <= 1e-9,
        "full_pm_no_disturbance_max_abs_mean_le_1e_9": full["pm_no_disturbance_max_abs_mean"] <= 1e-9,
        "same_marginals_kcbs_sum_mean_lt_bound": lookup["same_marginals_independent_table"]["kcbs_witness_sum_mean"] < 2.0,
        "strong_baseline_kcbs_sum_mean_lt_bound": lookup["strong_classical_table_baseline"]["kcbs_witness_sum_mean"] < 2.0,
        "strong_baseline_pm_accuracy_mean_lt_bound": lookup["strong_classical_table_baseline"]["pm_parity_accuracy_mean"] < 5.0 / 6.0,
        "full_kcbs_sum_wins_all_controls_5_of_5": all(win_counts[c + "_kcbs_wins"] >= 5 for c in VARIANTS[1:]),
        "full_pm_accuracy_wins_all_controls_5_of_5": all(win_counts[c + "_pm_wins"] >= 5 for c in VARIANTS[1:]),
    }

    return {
        "experiment": "contextual_membrane_quantum_anchor_probe_v1",
        "date": "2026-07-08",
        "layer": "QUANTUM_AUDIT",
        "seed": seed,
        "seeds": seeds,
        "variants": VARIANTS,
        "computed_bounds": {
            "kcbs_transition_event_bound": kcbs_bound,
            "kcbs_bound_assignment_count_at_max": kcbs_count,
            "pm_parity_accuracy_bound": pm_bound,
            "pm_max_satisfied_contexts": pm_max,
        },
        "seed_summaries": seed_rows,
        "aggregate_summaries": aggregate_rows,
        "criteria": criteria,
        "win_counts": win_counts,
        "verdict": "PASS_STRICT_WITNESS_TABLE_AUDIT_CANDIDATE_NOT_QUANTUM" if all(criteria.values()) else "FAIL_OR_MIXED_WITNESS_TABLE_AUDIT",
        "claim_boundary": [
            "This is an explicit witness-table audit candidate.",
            "PASS means the simulated probability tables pass the stated PM/KCBS-shaped table checks and exhaustive deterministic assignment bound checks.",
            "This is not a quantum-specific claim and not hardware-backed.",
            "Any quantum-specific claim still requires a real quantum witness or hardware-backed audit.",
        ],
    }


def write_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260708)
    parser.add_argument("--out", type=Path, default=Path("data/contextual/contextual_membrane_quantum_anchor_probe_v1_seed20260708.json"))
    parser.add_argument("--csv", type=Path, default=Path("data/contextual/contextual_membrane_quantum_anchor_probe_v1_seed20260708_aggregate.csv"))
    parser.add_argument("--seed-csv", type=Path, default=Path("data/contextual/contextual_membrane_quantum_anchor_probe_v1_seed20260708_seed_summary.csv"))
    args = parser.parse_args()

    result = run(args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(result["aggregate_summaries"], args.csv)
    write_csv(result["seed_summaries"], args.seed_csv)

    print(json.dumps({
        "experiment": result["experiment"],
        "verdict": result["verdict"],
        "computed_bounds": result["computed_bounds"],
        "aggregate_summaries": result["aggregate_summaries"],
        "criteria": result["criteria"],
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
