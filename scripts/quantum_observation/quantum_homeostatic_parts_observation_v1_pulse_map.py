#!/usr/bin/env python3
"""quantum_homeostatic_parts_observation_v1_pulse_map

Observation map for part-part negativity pulse timing.

This script separates:
- spatial attenuation: which pair reaches the larger negativity
- temporal propagation: when each pair reaches onset/peak

It is an observation map, not a PASS/FAIL test.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np


PROFILES = {
    "left_to_right_wave": {"centers": (34, 54, 74), "width": 10, "tox_center": 46, "pressure_center": 58},
    "simultaneous_burst": {"centers": (55, 56, 55), "width": 10, "tox_center": 55, "pressure_center": 55},
    "right_to_left_wave": {"centers": (76, 54, 34), "width": 10, "tox_center": 46, "pressure_center": 58},
    "double_pulse_wave": {"centers": (30, 50, 70), "width": 8, "tox_center": 42, "pressure_center": 64},
}

SCALES = {"weak": 0.65, "medium": 1.0, "strong": 1.35}
PAIRS = ["M_C", "C_R", "R_W"]


def gauss(t: int, center: float, width: float) -> float:
    return math.exp(-((t - center) / width) ** 2)


def make_series(profile: str, scale: str, mode: str, steps: int) -> list[dict]:
    cfg = PROFILES[profile]
    centers = cfg["centers"]
    width = cfg["width"]
    sc = SCALES[scale]
    rows = []

    for t in range(steps):
        energy = float(np.clip(0.38 + 0.33 * gauss(t, centers[0] - 8, 18) + 0.10 * math.sin(2 * math.pi * t / 53 + 0.7), 0, 1))
        toxicity = float(np.clip(0.12 + 0.62 * gauss(t, cfg["tox_center"], 18) + 0.18 * gauss(t, centers[1], 14), 0, 1))
        pressure = float(np.clip(0.18 + 0.55 * gauss(t, cfg["pressure_center"], 20) + 0.15 * gauss(t, centers[2], 16), 0, 1))
        dephasing_load = 0.12 + 0.55 * toxicity + 0.38 * pressure

        if mode == "field_only":
            theta_mc = theta_cr = theta_rw = 0.0
            neg_mc = neg_cr = neg_rw = 0.0
        else:
            theta_mc = sc * (0.020 + 0.115 * gauss(t, centers[0], width) + 0.030 * toxicity)
            theta_cr = sc * (0.018 + 0.105 * gauss(t, centers[1], width) + 0.026 * pressure)
            theta_rw = sc * (0.016 + 0.095 * gauss(t, centers[2], width) + 0.025 * pressure)
            coherence_window = max(0.0, 0.78 * energy + 0.22 - 0.42 * dephasing_load)
            neg_mc = max(0.0, theta_mc * coherence_window * 0.96 + 0.005 * gauss(t, centers[0] + 2, width * 1.2))
            neg_cr = max(0.0, theta_cr * coherence_window * 0.78 + 0.004 * gauss(t, centers[1] + 2, width * 1.2))
            neg_rw = max(0.0, theta_rw * coherence_window * 0.55 + 0.003 * gauss(t, centers[2] + 2, width * 1.2))

        negs = [neg_mc, neg_cr, neg_rw]
        rows.append({
            "t": t,
            "mode": mode,
            "profile": profile,
            "scale": scale,
            "energy": round(energy, 9),
            "toxicity": round(toxicity, 9),
            "pressure": round(pressure, 9),
            "theta_MC": round(theta_mc, 9),
            "theta_CR": round(theta_cr, 9),
            "theta_RW": round(theta_rw, 9),
            "neg_M_C": round(neg_mc, 12),
            "neg_C_R": round(neg_cr, 12),
            "neg_R_W": round(neg_rw, 12),
            "neg_raster": "".join("█" if n > 0.04 else ("▒" if n > 0.012 else ("·" if n <= 1e-12 else "░")) for n in negs),
        })
    return rows


def pulse_metrics(rows: list[dict], threshold: float) -> dict:
    out: dict = {}
    for pair in PAIRS:
        vals = np.array([r[f"neg_{pair}"] for r in rows], dtype=float)
        times = np.array([r["t"] for r in rows], dtype=int)
        peak_idx = int(np.argmax(vals))
        above = np.where(vals > threshold)[0]
        out[pair] = {
            "peak_time": int(times[peak_idx]),
            "peak_value": round(float(vals[peak_idx]), 12),
            "onset_time": int(times[above[0]]) if len(above) else None,
            "offset_time": int(times[above[-1]]) if len(above) else None,
            "duration_gt_threshold": int(len(above)),
        }

    out["lag_peak_CR_minus_MC"] = out["C_R"]["peak_time"] - out["M_C"]["peak_time"]
    out["lag_peak_RW_minus_CR"] = out["R_W"]["peak_time"] - out["C_R"]["peak_time"]
    out["lag_onset_CR_minus_MC"] = None if out["M_C"]["onset_time"] is None or out["C_R"]["onset_time"] is None else out["C_R"]["onset_time"] - out["M_C"]["onset_time"]
    out["lag_onset_RW_minus_CR"] = None if out["C_R"]["onset_time"] is None or out["R_W"]["onset_time"] is None else out["R_W"]["onset_time"] - out["C_R"]["onset_time"]

    peak_lags = [out["lag_peak_CR_minus_MC"], out["lag_peak_RW_minus_CR"]]
    if all(lag >= 6 for lag in peak_lags):
        out["travel_label"] = "left_to_right_peak_travel"
    elif all(abs(lag) <= 4 for lag in peak_lags):
        out["travel_label"] = "near_simultaneous_peaks"
    elif all(lag <= -6 for lag in peak_lags):
        out["travel_label"] = "right_to_left_peak_travel"
    else:
        out["travel_label"] = "mixed_or_damped"

    raster = []
    for i in range(0, len(rows), 4):
        segment = rows[i:i + 4]
        chars = []
        for pair in PAIRS:
            m = max(r[f"neg_{pair}"] for r in segment)
            chars.append("█" if m > 0.04 else ("▒" if m > threshold else ("·" if m <= 1e-12 else "░")))
        raster.append("".join(chars))
    out["negativity_raster_by_4_steps"] = " ".join(raster)
    return out


def write_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260708)
    parser.add_argument("--steps", type=int, default=120)
    parser.add_argument("--threshold", type=float, default=0.012)
    parser.add_argument("--out", type=Path, default=Path("data/quantum_observation/quantum_homeostatic_parts_observation_v1_pulse_map_seed20260708.json"))
    parser.add_argument("--summary-csv", type=Path, default=Path("data/quantum_observation/quantum_homeostatic_parts_observation_v1_pulse_map_seed20260708_summary.csv"))
    parser.add_argument("--trace-csv", type=Path, default=Path("data/quantum_observation/quantum_homeostatic_parts_observation_v1_pulse_map_seed20260708_compact_trace.csv"))
    args = parser.parse_args()

    all_rows = []
    summary = []
    for profile in PROFILES:
        for scale in SCALES:
            rows = make_series(profile, scale, "direct_entangling", args.steps)
            all_rows.extend(rows)
            metrics = pulse_metrics(rows, args.threshold)
            item = {"mode": "direct_entangling", "profile": profile, "scale": scale, "n": len(rows)}
            for pair in PAIRS:
                for key, value in metrics[pair].items():
                    item[f"{pair}_{key}"] = value
            for key in ["lag_peak_CR_minus_MC", "lag_peak_RW_minus_CR", "lag_onset_CR_minus_MC", "lag_onset_RW_minus_CR", "travel_label", "negativity_raster_by_4_steps"]:
                item[key] = metrics[key]
            summary.append(item)

    for profile in PROFILES:
        rows = make_series(profile, "medium", "field_only", args.steps)
        all_rows.extend(rows)
        metrics = pulse_metrics(rows, args.threshold)
        item = {"mode": "field_only", "profile": profile, "scale": "medium", "n": len(rows)}
        for pair in PAIRS:
            for key, value in metrics[pair].items():
                item[f"{pair}_{key}"] = value
        for key in ["lag_peak_CR_minus_MC", "lag_peak_RW_minus_CR", "lag_onset_CR_minus_MC", "lag_onset_RW_minus_CR", "travel_label", "negativity_raster_by_4_steps"]:
            item[key] = metrics[key]
        summary.append(item)

    compact_rows = [
        {k: r[k] for k in ["t", "mode", "profile", "scale", "energy", "toxicity", "pressure", "theta_MC", "theta_CR", "theta_RW", "neg_M_C", "neg_C_R", "neg_R_W", "neg_raster"]}
        for r in all_rows if r["scale"] == "medium" and r["t"] % 4 == 0
    ]

    result = {
        "experiment": "quantum_homeostatic_parts_observation_v1_pulse_map",
        "date": "2026-07-08",
        "layer": "QUANTUM_OBSERVATION",
        "status": "OBSERVATION_LOG",
        "config": {
            "seed": args.seed,
            "steps": args.steps,
            "pairs_tracked": ["M-C", "C-R", "R-W"],
            "fields": ["energy", "toxicity", "pressure"],
            "profiles": list(PROFILES.keys()),
            "coupling_scales": list(SCALES.keys()),
            "threshold_negativity": args.threshold,
            "observation_focus": "separate spatial attenuation from time propagation by extracting pair peak/onset times",
        },
        "scenario_summaries": summary,
        "observation_notes": [
            "This is an observation map, not a PASS/FAIL test.",
            "Peak time and onset time are extracted separately for M-C, C-R, and R-W negativity traces.",
            "Left-to-right profiles show positive peak lags from M-C to C-R to R-W.",
            "Simultaneous profiles show near-zero peak lags.",
            "Right-to-left profiles show negative peak lags.",
            "Field-only profiles keep negativity at zero, so a shared whole-field alone does not create pair negativity.",
            "The map separates spatial attenuation from temporal propagation.",
        ],
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(summary, args.summary_csv)
    write_csv(compact_rows, args.trace_csv)

    print(json.dumps({"experiment": result["experiment"], "status": result["status"], "scenario_summaries": summary}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
