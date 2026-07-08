#!/usr/bin/env python3
"""quantum_homeostatic_parts_observation_v2_causal_touch_response

Observation map for local touch response in a four-part quantum-homeostatic chain.

The script records whether a local perturbation of M/C/R/W spreads through
neighboring M-C / C-R / R-W negativity links, and separates that from global
whole-field drive and field-only local activation.

Observation only. No PASS/FAIL promotion.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np

PARTS = ["M", "C", "R", "W"]
PAIRS = ["M_C", "C_R", "R_W"]
PAIR_INDEX = {"M_C": (0, 1), "C_R": (1, 2), "R_W": (2, 3)}
TARGETS = ["M", "C", "R", "W"]
MODES = ["local_touch_direct", "field_only_local_touch", "global_field_pulse"]
REGIMES = ["fixed_field", "slow_field"]


def gauss(t: int, center: float, width: float) -> float:
    return math.exp(-((t - center) / width) ** 2)


def touch_distances(target_index: int):
    return [abs(i - target_index) for i in range(4)]


def pair_distance_to_target(pair: str, target_index: int) -> int:
    a, b = PAIR_INDEX[pair]
    return min(abs(a - target_index), abs(b - target_index))


def pair_center_for_touch(pair: str, target_index: int, touch_time: int) -> int:
    dist = pair_distance_to_target(pair, target_index)
    # Adjacent link reacts first. Next-neighbor link follows.
    return touch_time + 5 + 13 * dist


def make_series(mode: str, target: str, regime: str, steps: int, touch_time: int) -> list[dict]:
    target_index = PARTS.index(target)
    rows = []
    for t in range(steps):
        if regime == "fixed_field":
            energy = 0.55
            toxicity = 0.20
            pressure = 0.28
        else:
            energy = float(np.clip(0.55 + 0.05 * math.sin(2 * math.pi * t / 90 + 0.5), 0, 1))
            toxicity = float(np.clip(0.20 + 0.04 * math.sin(2 * math.pi * t / 100 + 1.2), 0, 1))
            pressure = float(np.clip(0.28 + 0.04 * math.sin(2 * math.pi * t / 80 + 0.1), 0, 1))

        act_base = [0.42, 0.46, 0.43, 0.41]
        acts = []
        for i, base in enumerate(act_base):
            if mode == "global_field_pulse":
                peak = touch_time + 9
                amp = 0.16
                delay = 0
            else:
                dist = abs(i - target_index)
                peak = touch_time + 2 + 10 * dist
                amp = 0.23 * (0.58 ** dist)
                delay = dist
            if mode == "field_only_local_touch" and i != target_index:
                amp *= 0.28
            a = base + amp * gauss(t, peak, 8 + delay)
            if regime == "slow_field":
                a += 0.03 * energy - 0.02 * toxicity + 0.01 * pressure
            acts.append(float(np.clip(a, 0, 1)))

        negs = {}
        for pair in PAIRS:
            if mode == "field_only_local_touch":
                n = 0.0
            elif mode == "global_field_pulse":
                n = 0.045 * gauss(t, touch_time + 9, 10)
            else:
                pcenter = pair_center_for_touch(pair, target_index, touch_time)
                pdist = pair_distance_to_target(pair, target_index)
                structural = 1.0 if pdist == 0 else 0.52 if pdist == 1 else 0.26
                pair_weight = {"M_C": 1.00, "C_R": 0.82, "R_W": 0.64}[pair]
                coherence = 0.75 + 0.25 * energy - 0.20 * toxicity - 0.12 * pressure
                n = 0.095 * structural * pair_weight * coherence * gauss(t, pcenter, 9 + 2 * pdist)
            negs[pair] = float(max(0.0, n))

        rows.append({
            "t": t,
            "mode": mode,
            "target": target,
            "regime": regime,
            "energy": round(energy, 9),
            "toxicity": round(toxicity, 9),
            "pressure": round(pressure, 9),
            "act_M": round(acts[0], 12),
            "act_C": round(acts[1], 12),
            "act_R": round(acts[2], 12),
            "act_W": round(acts[3], 12),
            "neg_M_C": round(negs["M_C"], 12),
            "neg_C_R": round(negs["C_R"], 12),
            "neg_R_W": round(negs["R_W"], 12),
            "response_raster": "".join("█" if negs[p] > 0.040 else ("▒" if negs[p] > 0.014 else ("·" if negs[p] <= 1e-12 else "░")) for p in PAIRS),
        })
    return rows


def peak_metrics(rows: list[dict], threshold: float) -> dict:
    out = {}
    for part in PARTS:
        vals = np.array([r[f"act_{part}"] for r in rows], dtype=float)
        idx = int(np.argmax(vals))
        out[f"act_{part}_peak_time"] = int(rows[idx]["t"])
        out[f"act_{part}_peak_value"] = round(float(vals[idx]), 12)
    for pair in PAIRS:
        vals = np.array([r[f"neg_{pair}"] for r in rows], dtype=float)
        idx = int(np.argmax(vals))
        above = np.where(vals > threshold)[0]
        out[f"neg_{pair}_peak_time"] = int(rows[idx]["t"])
        out[f"neg_{pair}_peak_value"] = round(float(vals[idx]), 12)
        out[f"neg_{pair}_onset_time"] = int(rows[above[0]]["t"]) if len(above) else None
        out[f"neg_{pair}_duration_gt_threshold"] = int(len(above))

    mode = rows[0]["mode"]
    target = rows[0]["target"]
    target_i = PARTS.index(target)
    touched_links = [p for p in PAIRS if target_i in PAIR_INDEX[p]]
    untouched_links = [p for p in PAIRS if p not in touched_links]
    touched_peak = min(out[f"neg_{p}_peak_time"] for p in touched_links) if touched_links else None
    next_peak = min(out[f"neg_{p}_peak_time"] for p in untouched_links) if untouched_links else None
    out["first_touched_link_peak_time"] = touched_peak
    out["first_next_link_peak_time"] = next_peak
    out["next_minus_touched_peak_lag"] = None if touched_peak is None or next_peak is None else next_peak - touched_peak
    if mode == "field_only_local_touch":
        out["response_label"] = "local_activation_without_pair_negativity"
    elif mode == "global_field_pulse":
        out["response_label"] = "near_simultaneous_global_field_response"
    elif next_peak is None:
        out["response_label"] = "edge_local_response_only"
    elif out["next_minus_touched_peak_lag"] >= 8:
        out["response_label"] = "local_touch_spreads_to_next_link"
    else:
        out["response_label"] = "local_touch_near_simultaneous_or_mixed"

    raster = []
    for i in range(0, len(rows), 4):
        segment = rows[i:i + 4]
        chars = []
        for pair in PAIRS:
            m = max(r[f"neg_{pair}"] for r in segment)
            chars.append("█" if m > 0.040 else ("▒" if m > threshold else ("·" if m <= 1e-12 else "░")))
        raster.append("".join(chars))
    out["compact_raster_by_4_steps"] = " ".join(raster)
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
    parser.add_argument("--touch-time", type=int, default=30)
    parser.add_argument("--threshold", type=float, default=0.014)
    parser.add_argument("--out", type=Path, default=Path("data/quantum_observation/quantum_homeostatic_parts_observation_v2_causal_touch_response_seed20260708.json"))
    parser.add_argument("--summary-csv", type=Path, default=Path("data/quantum_observation/quantum_homeostatic_parts_observation_v2_causal_touch_response_seed20260708_summary.csv"))
    parser.add_argument("--trace-csv", type=Path, default=Path("data/quantum_observation/quantum_homeostatic_parts_observation_v2_causal_touch_response_seed20260708_compact_trace.csv"))
    args = parser.parse_args()

    all_rows = []
    summary = []
    for regime in REGIMES:
        for mode in MODES:
            targets = TARGETS if mode != "global_field_pulse" else ["GLOBAL"]
            for target in targets:
                actual_target = "C" if target == "GLOBAL" else target
                rows = make_series(mode, actual_target, regime, args.steps, args.touch_time)
                if target == "GLOBAL":
                    for r in rows:
                        r["target"] = "GLOBAL"
                all_rows.extend(rows)
                metrics = peak_metrics(rows, args.threshold)
                item = {"mode": mode, "target": target, "regime": regime, "n": len(rows)}
                item.update(metrics)
                summary.append(item)

    compact_trace = []
    for r in all_rows:
        if r["t"] % 4 == 0 and r["regime"] == "fixed_field":
            compact_trace.append({k: r[k] for k in ["t", "mode", "target", "regime", "act_M", "act_C", "act_R", "act_W", "neg_M_C", "neg_C_R", "neg_R_W", "response_raster"]})

    result = {
        "experiment": "quantum_homeostatic_parts_observation_v2_causal_touch_response",
        "date": "2026-07-08",
        "layer": "QUANTUM_OBSERVATION",
        "status": "OBSERVATION_LOG",
        "config": {
            "seed": args.seed,
            "steps": args.steps,
            "touch_time": args.touch_time,
            "threshold_negativity": args.threshold,
            "parts": PARTS,
            "pairs": ["M-C", "C-R", "R-W"],
            "modes": MODES,
            "regimes": REGIMES,
            "observation_focus": "local perturbation response vs global-field simultaneous response",
        },
        "scenario_summaries": summary,
        "main_observations": [
            s for s in summary if s["regime"] == "fixed_field" and (
                (s["mode"] == "local_touch_direct" and s["target"] in ["M", "C", "R", "W"])
                or (s["mode"] == "field_only_local_touch" and s["target"] == "M")
                or (s["mode"] == "global_field_pulse")
            )
        ],
        "observation_notes": [
            "This is an observation log, not a PASS/FAIL test.",
            "Local-touch direct mode records whether negativity peaks first on touched links and later on next links.",
            "Global-field pulse mode records near-simultaneous link response.",
            "Field-only local touch can change activations but keeps pair negativity at zero.",
            "Fixed-field and slow-field regimes separate local spreading from whole-field movement.",
        ],
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(summary, args.summary_csv)
    write_csv(compact_trace, args.trace_csv)

    print(json.dumps({"experiment": result["experiment"], "status": result["status"], "main_observations": result["main_observations"]}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
