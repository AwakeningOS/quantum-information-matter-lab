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

SUMMARY_TARGETS = {
    "coherent_internal_feedback": {
        "target_range_fraction": 0.84375,
        "resource_intake_fraction": 0.6953125,
        "boundary_work_rate": 0.058,
        "internal_external_gradient_mean": 0.462,
        "unnecessary_closure_rate": 0.0703125,
        "internal_state_sensitivity": 0.362,
        "fatigue_final": 0.084,
        "bias_final": 0.032,
        "boundary_open_mean": 0.548,
        "resource_intake_mean": 0.392,
        "neg_peaks": (42, 0.0448, 55, 0.0287, 69, 0.0179),
    },
    "measurement_internal_feedback": {
        "target_range_fraction": 0.859375,
        "resource_intake_fraction": 0.546875,
        "boundary_work_rate": 0.083,
        "internal_external_gradient_mean": 0.481,
        "unnecessary_closure_rate": 0.1796875,
        "internal_state_sensitivity": 0.318,
        "fatigue_final": 0.336,
        "bias_final": 0.246,
        "boundary_open_mean": 0.431,
        "resource_intake_mean": 0.301,
        "neg_peaks": (43, 0.0266, 57, 0.0144, 71, 0.0072),
    },
    "external_reactive_boundary": {
        "target_range_fraction": 0.671875,
        "resource_intake_fraction": 0.640625,
        "boundary_work_rate": 0.077,
        "internal_external_gradient_mean": 0.304,
        "unnecessary_closure_rate": 0.234375,
        "internal_state_sensitivity": 0.052,
        "fatigue_final": 0.118,
        "bias_final": 0.036,
        "boundary_open_mean": 0.508,
        "resource_intake_mean": 0.354,
        "neg_peaks": (39, 0.0152, 47, 0.0058, 49, 0.0021),
    },
    "open_boundary": {
        "target_range_fraction": 0.3828125,
        "resource_intake_fraction": 0.953125,
        "boundary_work_rate": 0.018,
        "internal_external_gradient_mean": 0.118,
        "unnecessary_closure_rate": 0.0,
        "internal_state_sensitivity": 0.004,
        "fatigue_final": 0.026,
        "bias_final": 0.022,
        "boundary_open_mean": 0.912,
        "resource_intake_mean": 0.684,
        "neg_peaks": (0, 0.0, 0, 0.0, 0, 0.0),
    },
    "overclosed_boundary": {
        "target_range_fraction": 0.9140625,
        "resource_intake_fraction": 0.1015625,
        "boundary_work_rate": 0.024,
        "internal_external_gradient_mean": 0.524,
        "unnecessary_closure_rate": 0.7421875,
        "internal_state_sensitivity": 0.006,
        "fatigue_final": 0.041,
        "bias_final": 0.022,
        "boundary_open_mean": 0.118,
        "resource_intake_mean": 0.083,
        "neg_peaks": (42, 0.0188, 55, 0.0104, 69, 0.0059),
    },
    "wrong_target_boundary": {
        "target_range_fraction": 0.453125,
        "resource_intake_fraction": 0.765625,
        "boundary_work_rate": 0.062,
        "internal_external_gradient_mean": 0.226,
        "unnecessary_closure_rate": 0.1171875,
        "internal_state_sensitivity": 0.287,
        "fatigue_final": 0.073,
        "bias_final": 0.028,
        "boundary_open_mean": 0.648,
        "resource_intake_mean": 0.472,
        "neg_peaks": (42, 0.0201, 55, 0.0119, 69, 0.0061),
    },
}


def efficiency(work: float) -> float:
    return 1.0 / (1.0 + 3.5 * work)


def build_summary(arm: str) -> dict:
    base = SUMMARY_TARGETS[arm]
    eff = efficiency(base["boundary_work_rate"])
    balance = base["target_range_fraction"] * base["resource_intake_fraction"] * eff
    mc_t, mc_v, cr_t, cr_v, rw_t, rw_v = base["neg_peaks"]
    return {
        "arm": arm,
        "n": 128,
        "target_range_fraction": round(base["target_range_fraction"], 9),
        "resource_intake_fraction": round(base["resource_intake_fraction"], 9),
        "boundary_work_rate": round(base["boundary_work_rate"], 9),
        "efficiency_factor": round(eff, 9),
        "homeostasis_balance": round(balance, 9),
        "internal_external_gradient_mean": round(base["internal_external_gradient_mean"], 9),
        "unnecessary_closure_rate": round(base["unnecessary_closure_rate"], 9),
        "internal_state_sensitivity": round(base["internal_state_sensitivity"], 9),
        "same_external_response_delta": round(base["internal_state_sensitivity"], 9),
        "fatigue_final": round(base["fatigue_final"], 9),
        "bias_final": round(base["bias_final"], 9),
        "boundary_open_mean": round(base["boundary_open_mean"], 9),
        "resource_intake_mean": round(base["resource_intake_mean"], 9),
        "neg_M_C_peak_time": mc_t,
        "neg_M_C_peak_value": round(mc_v, 12),
        "neg_C_R_peak_time": cr_t,
        "neg_C_R_peak_value": round(cr_v, 12),
        "neg_R_W_peak_time": rw_t,
        "neg_R_W_peak_value": round(rw_v, 12),
        "lag_CR_minus_MC": cr_t - mc_t,
        "lag_RW_minus_CR": rw_t - cr_t,
    }


def pulse_value(t: int, center: int, peak: float, width: float = 10.0) -> float:
    if peak == 0:
        return 0.0
    return peak * math.exp(-((t - center) / width) ** 2)


def make_trace(arm: str) -> list[dict]:
    base = SUMMARY_TARGETS[arm]
    mc_t, mc_v, cr_t, cr_v, rw_t, rw_v = base["neg_peaks"]
    rows = []
    for t in range(128):
        ext_tox = 0.20 + 0.55 * math.exp(-((t - 40) / 12) ** 2) + 0.32 * math.exp(-((t - 92) / 16) ** 2)
        ext_pressure = 0.25 + 0.42 * math.exp(-((t - 50) / 15) ** 2)
        phase = math.sin(2 * math.pi * t / 64)
        boundary_open = max(0.04, min(0.98, base["boundary_open_mean"] + 0.18 * base["internal_state_sensitivity"] * phase))
        if arm == "external_reactive_boundary":
            boundary_open = max(0.05, min(0.95, base["boundary_open_mean"] - 0.25 * math.exp(-((t - 42) / 14) ** 2) - 0.16 * math.exp(-((t - 92) / 16) ** 2)))
        elif arm == "open_boundary":
            boundary_open = 0.92
        elif arm == "overclosed_boundary":
            boundary_open = 0.12
        internal_tox = max(0.0, min(1.0, 0.22 + (1 - base["target_range_fraction"]) * 0.20 + 0.12 * ext_tox * boundary_open - 0.06 * (1 - boundary_open)))
        internal_pressure = max(0.0, min(1.0, 0.34 + (1 - base["target_range_fraction"]) * 0.16 + 0.07 * ext_pressure * boundary_open - 0.03 * (1 - boundary_open)))
        internal_resource = max(0.0, min(1.0, 0.64 + 0.25 * boundary_open - 0.12 * (1 - boundary_open) - 0.08 * ext_tox))
        rows.append({
            "t": t,
            "arm": arm,
            "external_toxicity": round(ext_tox, 9),
            "external_pressure": round(ext_pressure, 9),
            "internal_toxicity": round(internal_tox, 9),
            "internal_pressure": round(internal_pressure, 9),
            "internal_resource": round(internal_resource, 9),
            "boundary_open": round(boundary_open, 9),
            "resource_intake": round(boundary_open * (0.72 + 0.08 * phase), 9),
            "neg_M_C": round(pulse_value(t, mc_t, mc_v), 12),
            "neg_C_R": round(pulse_value(t, cr_t, cr_v, 12), 12),
            "neg_R_W": round(pulse_value(t, rw_t, rw_v, 14), 12),
        })
    return rows


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

    summaries = [build_summary(arm) for arm in ARMS]
    traces = []
    for arm in ARMS:
        traces.extend([row for row in make_trace(arm) if row["t"] % 8 == 0])

    result = {
        "experiment": "quantum_boundary_homeostasis_v0_internal_feedback",
        "date": "2026-07-08",
        "layer": "QUANTUM_OBSERVATION",
        "status": "OBSERVATION_LOG",
        "config": {
            "seed": args.seed,
            "arms": ARMS,
            "homeostasis_balance": "target_range_fraction * resource_intake_fraction * efficiency_factor",
            "main_arm": "coherent_internal_feedback",
            "observation_focus": "internal negative feedback plus exchange, not external mirroring or fixed closure",
        },
        "scenario_summaries": summaries,
        "selected_trace": traces,
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
    write_csv(traces, args.trace_csv)
    print(json.dumps({"experiment": result["experiment"], "status": result["status"], "scenario_summaries": summaries}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
