#!/usr/bin/env python3
"""quantum_homeostatic_parts_observation_v3_recovery_cycle

Repeated local touch observation.

This script compares passive recovery, active recovery, and full reset while
tracking state variables that persist across touches:

- coherence residual
- population bias
- baseline negativity
- fatigue index

The response is derived from these state variables, not from touch count.
Observation only. No PASS/FAIL promotion.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

TOUCH_TIMES = [20, 60, 100, 140]
RECOVERY_MODES = ["passive_recovery", "active_recovery", "full_reset_baseline"]
TOUCH_TYPES = ["unitary_touch", "measurement_touch"]
CONDITIONS = ["high_energy", "high_toxicity"]


def run_scenario(recovery_mode: str, touch_type: str, condition: str, target: str = "C") -> tuple[list[dict], dict]:
    coherence = 0.86 if condition == "high_energy" else 0.70
    population_bias = 0.02
    baseline_negativity = 0.006
    fatigue = 0.02
    rows = []

    for idx, touch_time in enumerate(TOUCH_TIMES, start=1):
        if recovery_mode == "full_reset_baseline":
            coherence = 0.86 if condition == "high_energy" else 0.70
            population_bias = 0.02
            baseline_negativity = 0.006
            fatigue = 0.02

        env_gain = 1.10 if condition == "high_energy" else 0.82
        base_link = 0.090 * env_gain * max(0.0, coherence) * (1.0 - 0.55 * fatigue) * (1.0 - 0.45 * population_bias)
        if touch_type == "measurement_touch":
            base_link *= 0.88 - 0.20 * population_bias

        peak_mc = base_link
        peak_cr = 0.82 * base_link
        peak_rw = 0.34 * base_link

        rows.append({
            "condition": condition,
            "recovery_mode": recovery_mode,
            "touch_type": touch_type,
            "target": target,
            "touch_index": idx,
            "touch_time": touch_time,
            "pre_coherence_residual": round(coherence, 9),
            "pre_population_bias": round(population_bias, 9),
            "pre_baseline_negativity": round(baseline_negativity, 9),
            "pre_fatigue_index": round(fatigue, 9),
            "peak_time_M_C": touch_time + 5,
            "peak_neg_M_C": round(peak_mc, 12),
            "peak_time_C_R": touch_time + 5,
            "peak_neg_C_R": round(peak_cr, 12),
            "peak_time_R_W": touch_time + 18,
            "peak_neg_R_W": round(peak_rw, 12),
            "next_link_lag": 13,
            "mean_adjacent_peak": round((peak_mc + peak_cr) / 2.0, 12),
            "outer_peak": round(peak_rw, 12),
        })

        touch_coherence_cost = 0.12 if touch_type == "unitary_touch" else 0.26
        irreversible_bias = 0.03 if touch_type == "unitary_touch" else 0.18
        coherence = max(0.0, coherence - touch_coherence_cost * (1.05 if condition == "high_toxicity" else 0.75))
        population_bias = min(1.0, population_bias + irreversible_bias * (1.10 if condition == "high_toxicity" else 0.70))
        baseline_negativity = max(0.0, baseline_negativity + 0.018 * coherence - 0.015 * fatigue)
        fatigue = min(1.0, fatigue + (0.075 if touch_type == "unitary_touch" else 0.16) * (1.25 if condition == "high_toxicity" else 0.75))

        if recovery_mode == "passive_recovery":
            coherence *= 0.92 if condition == "high_energy" else 0.78
            baseline_negativity *= 0.70
            population_bias *= 0.98 if condition == "high_energy" else 1.02
            fatigue *= 0.95 if condition == "high_energy" else 1.02
        elif recovery_mode == "active_recovery":
            target_coherence = 0.84 if condition == "high_energy" else 0.62
            coherence += 0.55 * (target_coherence - coherence)
            population_bias *= 0.42 if condition == "high_energy" else 0.65
            fatigue *= 0.55 if condition == "high_energy" else 0.78
            baseline_negativity *= 0.45
        elif recovery_mode == "full_reset_baseline":
            pass

        coherence = float(max(0.0, min(1.0, coherence)))
        population_bias = float(max(0.0, min(1.0, population_bias)))
        baseline_negativity = float(max(0.0, min(1.0, baseline_negativity)))
        fatigue = float(max(0.0, min(1.0, fatigue)))

    first = rows[0]["mean_adjacent_peak"]
    last = rows[-1]["mean_adjacent_peak"]
    ratio = last / first if first else 0.0
    if recovery_mode == "full_reset_baseline":
        label = "reset_control_stable"
    elif recovery_mode == "active_recovery" and ratio > 0.75:
        label = "active_recovery_holds_response"
    elif ratio < 0.70:
        label = "habituation_like_response_decay"
    else:
        label = "partial_recovery_or_mild_decay"

    summary = {
        "condition": condition,
        "recovery_mode": recovery_mode,
        "touch_type": touch_type,
        "target": target,
        "n_touches": len(rows),
        "first_adjacent_mean_peak": round(first, 12),
        "last_adjacent_mean_peak": round(last, 12),
        "response_ratio_last_over_first": round(ratio, 9),
        "adjacent_peak_delta_last_minus_first": round(last - first, 12),
        "pre_coherence_first": rows[0]["pre_coherence_residual"],
        "pre_coherence_last": rows[-1]["pre_coherence_residual"],
        "pre_population_bias_first": rows[0]["pre_population_bias"],
        "pre_population_bias_last": rows[-1]["pre_population_bias"],
        "pre_baseline_negativity_first": rows[0]["pre_baseline_negativity"],
        "pre_baseline_negativity_last": rows[-1]["pre_baseline_negativity"],
        "pre_fatigue_first": rows[0]["pre_fatigue_index"],
        "pre_fatigue_last": rows[-1]["pre_fatigue_index"],
        "memory_trace_label": label,
    }
    return rows, summary


def write_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260708)
    parser.add_argument("--out", type=Path, default=Path("data/quantum_observation/quantum_homeostatic_parts_observation_v3_recovery_cycle_seed20260708.json"))
    parser.add_argument("--summary-csv", type=Path, default=Path("data/quantum_observation/quantum_homeostatic_parts_observation_v3_recovery_cycle_seed20260708_summary.csv"))
    parser.add_argument("--touch-csv", type=Path, default=Path("data/quantum_observation/quantum_homeostatic_parts_observation_v3_recovery_cycle_seed20260708_touch_rows.csv"))
    args = parser.parse_args()

    touch_rows = []
    summaries = []
    for condition in CONDITIONS:
        for recovery_mode in RECOVERY_MODES:
            for touch_type in TOUCH_TYPES:
                rows, summary = run_scenario(recovery_mode, touch_type, condition)
                touch_rows.extend(rows)
                summaries.append(summary)

    result = {
        "experiment": "quantum_homeostatic_parts_observation_v3_recovery_cycle",
        "date": "2026-07-08",
        "layer": "QUANTUM_OBSERVATION",
        "status": "OBSERVATION_LOG",
        "config": {
            "seed": args.seed,
            "touch_times": TOUCH_TIMES,
            "target": "C",
            "recovery_modes": RECOVERY_MODES,
            "touch_types": TOUCH_TYPES,
            "conditions": CONDITIONS,
            "state_variables_tracked": [
                "pre_coherence_residual",
                "pre_population_bias",
                "pre_baseline_negativity",
                "pre_fatigue_index",
            ],
            "observation_focus": "repeated local touch response with cross-touch memory variables",
        },
        "scenario_summaries": summaries,
        "touch_rows": touch_rows,
        "observation_notes": [
            "This is an observation log, not a PASS/FAIL test.",
            "Response changes are produced through state variables, not by an explicit touch-count response rule.",
            "Full reset baseline stays stable by removing cross-touch memory.",
            "Passive recovery shows response decay when coherence falls and bias/fatigue accumulate.",
            "Active recovery holds high-energy unitary response more strongly, but measurement touch and high-toxicity still leave bias/fatigue traces.",
        ],
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(summaries, args.summary_csv)
    write_csv(touch_rows, args.touch_csv)

    print(json.dumps({"experiment": result["experiment"], "status": result["status"], "scenario_summaries": summaries}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
