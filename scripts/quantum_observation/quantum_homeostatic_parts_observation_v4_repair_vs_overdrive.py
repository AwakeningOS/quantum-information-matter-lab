#!/usr/bin/env python3
"""quantum_homeostatic_parts_observation_v4_repair_vs_overdrive

Repeated-touch recovery-strength observation.

The labels are assigned mechanically from predeclared trajectory metrics:
response ratio, overshoot, state distance, oscillation envelope, fatigue, and
population bias. Observation only. No PASS/FAIL promotion.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

TOUCHES = [1, 2, 3, 4, 5, 6]
RECOVERY_MODES = [
    "weak_recovery",
    "gentle_recovery",
    "strong_recovery",
    "oscillatory_recovery",
    "extreme_recovery",
    "full_reset_baseline",
]
TOUCH_TYPES = ["unitary_touch", "measurement_touch"]
CONDITIONS = ["high_energy", "high_toxicity"]


def run_scenario(recovery_mode: str, condition: str, touch_type: str) -> tuple[list[dict], dict]:
    high = condition == "high_energy"
    measurement = touch_type == "measurement_touch"
    set_coherence = 0.82 if high else 0.62
    set_bias = 0.02
    set_fatigue = 0.02
    set_baseline_negativity = 0.006

    coherence = set_coherence
    population_bias = set_bias
    fatigue = set_fatigue
    baseline_negativity = set_baseline_negativity
    rows: list[dict] = []

    for touch_index in TOUCHES:
        if recovery_mode == "full_reset_baseline":
            coherence = set_coherence
            population_bias = set_bias
            fatigue = set_fatigue
            baseline_negativity = set_baseline_negativity

        env_gain = 1.10 if high else 0.82
        repair_charge = (baseline_negativity - set_baseline_negativity) / 0.02
        response = (
            0.095
            * env_gain
            * max(0.0, coherence)
            * (1.0 - 0.55 * fatigue)
            * (1.0 - 0.45 * population_bias)
            * (1.0 + 0.18 * repair_charge)
        )
        if measurement:
            response *= 0.88 - 0.18 * population_bias
        response = max(0.0, response)

        state_distance = (
            abs(coherence - set_coherence)
            + 0.8 * abs(population_bias - set_bias)
            + 0.8 * abs(fatigue - set_fatigue)
            + 0.5 * abs(baseline_negativity - set_baseline_negativity)
        )

        rows.append({
            "condition": condition,
            "recovery_mode": recovery_mode,
            "touch_type": touch_type,
            "target": "C",
            "touch_index": touch_index,
            "pre_coherence_residual": round(coherence, 9),
            "pre_population_bias": round(population_bias, 9),
            "pre_baseline_negativity": round(baseline_negativity, 9),
            "pre_fatigue_index": round(fatigue, 9),
            "state_distance": round(state_distance, 12),
            "mean_adjacent_peak": round(response, 12),
            "peak_neg_M_C": round(response * 1.10, 12),
            "peak_neg_C_R": round(response * 0.90, 12),
            "peak_neg_R_W": round(response * 0.36, 12),
        })

        coherence_loss = 0.08 if not measurement else 0.20
        bias_gain = 0.025 if not measurement else 0.14
        fatigue_gain = 0.05 if not measurement else 0.12
        damage_multiplier = 0.75 if high else 1.20

        coherence -= coherence_loss * damage_multiplier
        population_bias += bias_gain * (0.70 if high else 1.25)
        fatigue += fatigue_gain * (0.75 if high else 1.20)
        baseline_negativity += 0.006 * coherence - 0.006 * fatigue

        if recovery_mode == "weak_recovery":
            coherence *= 0.94 if high else 0.80
            population_bias *= 0.96 if high else 1.03
            fatigue *= 0.96 if high else 1.04
            baseline_negativity *= 0.75
        elif recovery_mode == "gentle_recovery":
            k = 0.58 if high else 0.42
            coherence += k * (set_coherence - coherence)
            population_bias += k * (set_bias - population_bias)
            fatigue += k * (set_fatigue - fatigue)
            baseline_negativity += 0.55 * (set_baseline_negativity - baseline_negativity)
        elif recovery_mode == "strong_recovery":
            sign = -1 if touch_index % 2 == 0 else 1
            amp = (0.080 if high else 0.100) * (0.70 ** (touch_index - 1))
            coherence = set_coherence + sign * amp
            population_bias = max(0.0, set_bias + sign * 0.018 * (0.65 ** (touch_index - 1)))
            fatigue = max(0.0, set_fatigue + abs(amp) * 0.22)
            baseline_negativity = set_baseline_negativity + sign * 0.010 * (0.65 ** (touch_index - 1))
        elif recovery_mode == "oscillatory_recovery":
            damp = 0.78 if high else 1.03
            sign = -1 if touch_index % 2 == 0 else 1
            amp = (0.120 if high else 0.130) * (damp ** (touch_index - 1))
            coherence = set_coherence + sign * amp
            population_bias = max(0.0, set_bias + sign * 0.025 * (damp ** (touch_index - 1)))
            fatigue = max(0.0, set_fatigue + abs(amp) * 0.30 + (0.004 * touch_index if high else 0.015 * touch_index))
            baseline_negativity = max(0.0, set_baseline_negativity + sign * 0.015 * (damp ** (touch_index - 1)))
        elif recovery_mode == "extreme_recovery":
            growth = 1.22 if high else 1.35
            sign = -1 if touch_index % 2 == 0 else 1
            amp = (0.100 if high else 0.120) * (growth ** (touch_index - 1))
            coherence = set_coherence + sign * amp
            population_bias = population_bias * 0.75 + 0.035 * touch_index + (0.04 if measurement else 0.0)
            fatigue = fatigue * 0.82 + 0.045 * touch_index + (0.06 if measurement else 0.0)
            baseline_negativity = max(0.0, set_baseline_negativity + sign * 0.020 * (growth ** (touch_index - 1)))
        elif recovery_mode == "full_reset_baseline":
            pass

        coherence = max(0.0, min(1.4, coherence))
        population_bias = max(0.0, min(1.0, population_bias))
        fatigue = max(0.0, min(1.0, fatigue))
        baseline_negativity = max(0.0, min(0.2, baseline_negativity))

    responses = [row["mean_adjacent_peak"] for row in rows]
    distances = [row["state_distance"] for row in rows]
    first = responses[0]
    last = responses[-1]
    response_ratio = last / first if first else 0.0
    overshoot_max = max((value / first - 1.0 for value in responses), default=0.0) if first else 0.0
    if recovery_mode in {"strong_recovery", "oscillatory_recovery", "extreme_recovery"}:
        early_envelope = max(distances[1], distances[2], 1e-9)
        late_envelope = max(distances[-2], distances[-1], 1e-9)
        oscillation_envelope_ratio = late_envelope / early_envelope
    else:
        oscillation_envelope_ratio = 0.0

    coherence_last = rows[-1]["pre_coherence_residual"]
    bias_last = rows[-1]["pre_population_bias"]
    fatigue_last = rows[-1]["pre_fatigue_index"]
    state_distance_last = distances[-1]

    if response_ratio <= 0.20 and coherence_last <= 0.20 and fatigue_last >= 0.30:
        label = "collapse_or_exhausted_repair"
    elif (
        (overshoot_max >= 0.30 and oscillation_envelope_ratio >= 1.10)
        or state_distance_last >= 0.75
        or (response_ratio >= 1.25 and (fatigue_last > rows[0]["pre_fatigue_index"] or bias_last > rows[0]["pre_population_bias"]))
    ):
        label = "overdrive"
    elif overshoot_max > 0.15 and oscillation_envelope_ratio < 0.90 and state_distance_last <= 0.15 and fatigue_last <= 0.30:
        label = "damped_oscillatory_repair"
    elif 0.75 <= response_ratio <= 1.10 and overshoot_max <= 0.15 and state_distance_last <= 0.25 and oscillation_envelope_ratio <= 1.10 and fatigue_last <= 0.20 and bias_last <= 0.12:
        label = "stable_repair"
    elif response_ratio < 0.75:
        label = "partial_repair_or_fatigue"
    else:
        label = "mixed_repair"

    summary = {
        "condition": condition,
        "recovery_mode": recovery_mode,
        "touch_type": touch_type,
        "target": "C",
        "n_touches": len(rows),
        "first_adjacent_mean_peak": round(first, 12),
        "last_adjacent_mean_peak": round(last, 12),
        "response_ratio_last_over_first": round(response_ratio, 9),
        "overshoot_max": round(overshoot_max, 9),
        "state_distance_first": round(distances[0], 12),
        "state_distance_last": round(state_distance_last, 12),
        "state_distance_ratio_last_over_first": round(state_distance_last / max(distances[0], 1e-9), 9),
        "oscillation_envelope_ratio": round(oscillation_envelope_ratio, 9),
        "coherence_first": rows[0]["pre_coherence_residual"],
        "coherence_last": coherence_last,
        "bias_first": rows[0]["pre_population_bias"],
        "bias_last": bias_last,
        "fatigue_first": rows[0]["pre_fatigue_index"],
        "fatigue_last": fatigue_last,
        "mechanical_label": label,
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
    parser.add_argument("--out", type=Path, default=Path("data/quantum_observation/quantum_homeostatic_parts_observation_v4_repair_vs_overdrive_seed20260708.json"))
    parser.add_argument("--summary-csv", type=Path, default=Path("data/quantum_observation/quantum_homeostatic_parts_observation_v4_repair_vs_overdrive_seed20260708_summary.csv"))
    parser.add_argument("--touch-csv", type=Path, default=Path("data/quantum_observation/quantum_homeostatic_parts_observation_v4_repair_vs_overdrive_seed20260708_selected_touch_rows.csv"))
    args = parser.parse_args()

    all_rows = []
    summaries = []
    for condition in CONDITIONS:
        for recovery_mode in RECOVERY_MODES:
            for touch_type in TOUCH_TYPES:
                rows, summary = run_scenario(recovery_mode, condition, touch_type)
                all_rows.extend(rows)
                summaries.append(summary)

    selected_rows = [
        row for row in all_rows
        if row["touch_index"] in {1, 3, 6}
        and (
            (row["condition"] == "high_energy" and row["recovery_mode"] in {"gentle_recovery", "strong_recovery", "extreme_recovery", "full_reset_baseline"} and row["touch_type"] == "unitary_touch")
            or (row["condition"] == "high_toxicity" and row["recovery_mode"] in {"oscillatory_recovery", "extreme_recovery", "weak_recovery"} and row["touch_type"] == "measurement_touch")
        )
    ]

    result = {
        "experiment": "quantum_homeostatic_parts_observation_v4_repair_vs_overdrive",
        "date": "2026-07-08",
        "layer": "QUANTUM_OBSERVATION",
        "status": "OBSERVATION_LOG",
        "config": {
            "seed": args.seed,
            "target": "C",
            "n_touches": len(TOUCHES),
            "recovery_modes": RECOVERY_MODES,
            "touch_types": TOUCH_TYPES,
            "conditions": CONDITIONS,
            "mechanical_label_definitions": {
                "stable_repair": "0.75<=response_ratio<=1.10, overshoot<=0.15, state_distance_last<=0.25, oscillation_envelope<=1.10, fatigue<=0.20, bias<=0.12",
                "damped_oscillatory_repair": "overshoot>0.15, oscillation_envelope<0.90, state_distance_last<=0.15, fatigue<=0.30",
                "overdrive": "overshoot>=0.30 with growing oscillation, or state_distance_last>=0.75, or response_ratio>=1.25 while fatigue/bias increase",
                "collapse_or_exhausted_repair": "response_ratio<=0.20, coherence_last<=0.20, fatigue_last>=0.30",
            },
        },
        "scenario_summaries": summaries,
        "selected_touch_rows": selected_rows,
        "observation_notes": [
            "This is an observation log, not a PASS/FAIL test.",
            "Labels are assigned mechanically from predeclared response, overshoot, state-distance, oscillation-envelope, fatigue, and bias thresholds.",
            "Gentle recovery under high energy is classified as stable repair.",
            "Strong/oscillatory recovery can produce damped oscillatory repair when the oscillation envelope decays.",
            "Oscillatory or extreme recovery under high toxicity can become overdrive when the envelope and/or state distance grows.",
            "Weak recovery under high toxicity can collapse or exhaust response.",
            "Full reset stays stable and remains the reference that removes cross-touch memory.",
        ],
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(summaries, args.summary_csv)
    write_csv(selected_rows, args.touch_csv)

    print(json.dumps({"experiment": result["experiment"], "status": result["status"], "scenario_summaries": summaries}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
