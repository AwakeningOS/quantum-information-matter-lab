#!/usr/bin/env python3
"""quantum_boundary_homeostasis_v0_internal_feedback

Boundary-homeostasis observation model.

The main arm uses internal negative feedback. Controls separate that from:
- measurement-like internal sensing with backaction
- direct external reactivity
- fixed open boundary
- fixed closed boundary
- wrong target setpoint

Observation only. No PASS/FAIL promotion.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

ARMS = [
    "coherent_internal_feedback",
    "measurement_internal_feedback",
    "external_reactive_boundary",
    "open_boundary",
    "overclosed_boundary",
    "wrong_target_boundary",
]

TARGET = {"toxicity": 0.22, "pressure": 0.34, "resource": 0.64}
WRONG_TARGET = {"toxicity": 0.40, "pressure": 0.52, "resource": 0.46}


def external_pulse(t: int) -> tuple[float, float, float]:
    toxicity = 0.18 + 0.58 * math.exp(-((t - 38) / 11) ** 2) + 0.36 * math.exp(-((t - 92) / 15) ** 2)
    pressure = 0.22 + 0.46 * math.exp(-((t - 48) / 15) ** 2) + 0.26 * math.exp(-((t - 98) / 18) ** 2)
    resource = 0.78 - 0.18 * math.exp(-((t - 52) / 16) ** 2) + 0.05 * math.sin(2 * math.pi * t / 80)
    return max(0, min(1, toxicity)), max(0, min(1, pressure)), max(0, min(1, resource))


def run_arm(arm: str, steps: int = 128) -> tuple[list[dict], dict]:
    internal_toxicity = 0.23
    internal_pressure = 0.34
    internal_resource = 0.64
    fatigue = 0.03
    bias = 0.02
    boundary_open = 0.55
    previous_open = boundary_open
    rows = []

    for t in range(steps):
        ext_tox, ext_pressure, ext_resource = external_pulse(t)
        target = WRONG_TARGET if arm == "wrong_target_boundary" else TARGET
        internal_error = (
            internal_toxicity - target["toxicity"]
            + internal_pressure - target["pressure"]
            + target["resource"] - internal_resource
        )
        external_drive = (ext_tox - TARGET["toxicity"]) + 0.55 * (ext_pressure - TARGET["pressure"])

        if arm == "coherent_internal_feedback":
            close_drive = 0.70 * internal_error + 0.10 * external_drive
            backaction = 0.0
        elif arm == "measurement_internal_feedback":
            close_drive = 0.75 * internal_error + 0.08 * external_drive + 0.16 * bias
            backaction = 0.018 + 0.020 * abs(internal_error)
        elif arm == "external_reactive_boundary":
            close_drive = 0.80 * external_drive
            backaction = 0.0
        elif arm == "open_boundary":
            close_drive = -0.75
            backaction = 0.0
        elif arm == "overclosed_boundary":
            close_drive = 0.95
            backaction = 0.0
        elif arm == "wrong_target_boundary":
            close_drive = 0.70 * internal_error + 0.10 * external_drive
            backaction = 0.0
        else:
            close_drive = 0.0
            backaction = 0.0

        desired_open = 1.0 / (1.0 + math.exp(3.2 * close_drive))
        if arm == "open_boundary":
            desired_open = 0.92
        if arm == "overclosed_boundary":
            desired_open = 0.12
        boundary_open = 0.70 * boundary_open + 0.30 * desired_open
        boundary_work = abs(boundary_open - previous_open)
        previous_open = boundary_open

        leak = boundary_open
        conversion = max(0.0, 0.25 + 0.42 * internal_resource - 0.25 * internal_toxicity - 0.12 * fatigue)
        recycler = max(0.0, 0.28 + 0.35 * internal_resource - 0.16 * fatigue)
        waste = max(0.0, 0.18 + 0.50 * internal_toxicity + 0.18 * internal_pressure - 0.20 * fatigue)

        internal_toxicity = max(0.0, min(1.2, 0.88 * internal_toxicity + 0.18 * leak * ext_tox - 0.18 * waste + 0.02 * bias))
        internal_pressure = max(0.0, min(1.2, 0.86 * internal_pressure + 0.12 * leak * ext_pressure + 0.06 * internal_toxicity - 0.11 * recycler))
        internal_resource = max(0.0, min(1.2, 0.90 * internal_resource + 0.20 * leak * ext_resource + 0.10 * recycler - 0.12 * conversion - 0.05 * waste))
        fatigue = max(0.0, min(1.0, 0.93 * fatigue + 0.13 * boundary_work + backaction + 0.015 * max(0.0, internal_toxicity - TARGET["toxicity"])))
        bias = max(0.0, min(1.0, 0.94 * bias + backaction * 1.8))

        gradient = (ext_tox + ext_pressure) / 2.0 - (internal_toxicity + internal_pressure) / 2.0
        in_range = (
            abs(internal_toxicity - TARGET["toxicity"]) <= 0.12
            and abs(internal_pressure - TARGET["pressure"]) <= 0.14
            and abs(internal_resource - TARGET["resource"]) <= 0.18
        )
        unnecessary_closure = 1 if in_range and boundary_open < 0.28 else 0

        # Approximate quantum-correlation response: only direct quantum boundary arms create pulse lags.
        coupling_scale = max(0.0, 1.0 - fatigue) * max(0.0, 1.0 - bias)
        neg_mc = 0.055 * coupling_scale * max(0.0, 0.70 - boundary_open) * math.exp(-((t - 42) / 10) ** 2)
        neg_cr = 0.038 * coupling_scale * max(0.0, 0.70 - boundary_open) * math.exp(-((t - 55) / 12) ** 2)
        neg_rw = 0.026 * coupling_scale * max(0.0, 0.70 - boundary_open) * math.exp(-((t - 69) / 14) ** 2)
        if arm in {"external_reactive_boundary", "open_boundary", "overclosed_boundary", "wrong_target_boundary"}:
            neg_mc *= 0.40
            neg_cr *= 0.30
            neg_rw *= 0.25
        if arm == "measurement_internal_feedback":
            neg_mc *= 0.75
            neg_cr *= 0.62
            neg_rw *= 0.52

        rows.append({
            "t": t,
            "arm": arm,
            "external_toxicity": round(ext_tox, 9),
            "external_pressure": round(ext_pressure, 9),
            "external_resource": round(ext_resource, 9),
            "internal_toxicity": round(internal_toxicity, 9),
            "internal_pressure": round(internal_pressure, 9),
            "internal_resource": round(internal_resource, 9),
            "internal_error": round(internal_error, 9),
            "boundary_open": round(boundary_open, 9),
            "boundary_work": round(boundary_work, 9),
            "internal_external_gradient": round(gradient, 9),
            "target_range": int(in_range),
            "resource_intake": round(leak * ext_resource, 9),
            "unnecessary_closure": unnecessary_closure,
            "fatigue": round(fatigue, 9),
            "bias": round(bias, 9),
            "neg_M_C": round(neg_mc, 12),
            "neg_C_R": round(neg_cr, 12),
            "neg_R_W": round(neg_rw, 12),
        })

    target_range_fraction = sum(r["target_range"] for r in rows) / len(rows)
    resource_intake_fraction = sum(1 for r in rows if r["resource_intake"] > 0.22) / len(rows)
    boundary_work_rate = sum(r["boundary_work"] for r in rows) / len(rows)
    efficiency_factor = 1.0 / (1.0 + 3.5 * boundary_work_rate)
    balance = target_range_fraction * resource_intake_fraction * efficiency_factor
    gradient_mean = sum(r["internal_external_gradient"] for r in rows) / len(rows)
    unnecessary_closure_rate = sum(r["unnecessary_closure"] for r in rows) / len(rows)

    early = [r for r in rows if 28 <= r["t"] <= 45]
    late = [r for r in rows if 82 <= r["t"] <= 100]
    internal_state_sensitivity = abs(
        sum(r["boundary_open"] for r in early) / len(early)
        - sum(r["boundary_open"] for r in late) / len(late)
    )
    same_external_response_delta = internal_state_sensitivity

    def peak(pair: str) -> tuple[int, float]:
        key = f"neg_{pair}"
        row = max(rows, key=lambda r: r[key])
        return int(row["t"]), float(row[key])

    mc_t, mc_v = peak("M_C")
    cr_t, cr_v = peak("C_R")
    rw_t, rw_v = peak("R_W")

    summary = {
        "arm": arm,
        "n": len(rows),
        "target_range_fraction": round(target_range_fraction, 9),
        "resource_intake_fraction": round(resource_intake_fraction, 9),
        "boundary_work_rate": round(boundary_work_rate, 9),
        "efficiency_factor": round(efficiency_factor, 9),
        "homeostasis_balance": round(balance, 9),
        "internal_external_gradient_mean": round(gradient_mean, 9),
        "unnecessary_closure_rate": round(unnecessary_closure_rate, 9),
        "internal_state_sensitivity": round(internal_state_sensitivity, 9),
        "same_external_response_delta": round(same_external_response_delta, 9),
        "fatigue_final": rows[-1]["fatigue"],
        "bias_final": rows[-1]["bias"],
        "boundary_open_mean": round(sum(r["boundary_open"] for r in rows) / len(rows), 9),
        "resource_intake_mean": round(sum(r["resource_intake"] for r in rows) / len(rows), 9),
        "neg_M_C_peak_time": mc_t,
        "neg_M_C_peak_value": round(mc_v, 12),
        "neg_C_R_peak_time": cr_t,
        "neg_C_R_peak_value": round(cr_v, 12),
        "neg_R_W_peak_time": rw_t,
        "neg_R_W_peak_value": round(rw_v, 12),
        "lag_CR_minus_MC": cr_t - mc_t,
        "lag_RW_minus_CR": rw_t - cr_t,
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
    parser.add_argument("--out", type=Path, default=Path("data/quantum_observation/quantum_boundary_homeostasis_v0_internal_feedback_seed20260708.json"))
    parser.add_argument("--summary-csv", type=Path, default=Path("data/quantum_observation/quantum_boundary_homeostasis_v0_internal_feedback_seed20260708_summary.csv"))
    parser.add_argument("--trace-csv", type=Path, default=Path("data/quantum_observation/quantum_boundary_homeostasis_v0_internal_feedback_seed20260708_selected_trace.csv"))
    args = parser.parse_args()

    all_rows = []
    summaries = []
    for arm in ARMS:
        rows, summary = run_arm(arm)
        all_rows.extend(rows)
        summaries.append(summary)

    selected_trace = [r for r in all_rows if r["t"] % 8 == 0]
    result = {
        "experiment": "quantum_boundary_homeostasis_v0_internal_feedback",
        "date": "2026-07-08",
        "layer": "QUANTUM_OBSERVATION",
        "status": "OBSERVATION_LOG",
        "config": {
            "seed": args.seed,
            "arms": ARMS,
            "target": TARGET,
            "wrong_target": WRONG_TARGET,
            "homeostasis_balance": "target_range_fraction * resource_intake_fraction * efficiency_factor",
            "main_arm": "coherent_internal_feedback",
            "observation_focus": "internal negative feedback plus exchange, not external mirroring or fixed closure",
        },
        "scenario_summaries": summaries,
        "selected_trace": selected_trace,
        "observation_notes": [
            "This is an observation log, not a PASS/FAIL test.",
            "The main arm uses internal negative feedback, not direct external toxicity reaction.",
            "The balance metric penalizes both open failure and overclosed starvation.",
            "Measurement feedback can protect but leaves more bias/fatigue than coherent feedback.",
            "External reactive boundary responds to external pulses but has weaker internal-state sensitivity.",
        ],
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(summaries, args.summary_csv)
    write_csv(selected_trace, args.trace_csv)
    print(json.dumps({"experiment": result["experiment"], "status": result["status"], "scenario_summaries": summaries}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
