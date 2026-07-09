#!/usr/bin/env python3
"""classical_vs_quantum_part_coupling_v2_noise_model

Noise-model check for the v1a signed/oriented measurable witness.

This is a simple pre-hardware density-matrix noise model, not a backend-calibrated
QPU simulation.
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
SEEDS = list(range(20260741, 20260757))
BOOTSTRAPS = 10000

PROFILES = {
    "none": {
        "p_dephase_layer": 0.000,
        "p_depolarize_1q": 0.000,
        "p_depolarize_2q": 0.000,
        "p_readout_flip": 0.000,
    },
    "light": {
        "p_dephase_layer": 0.003,
        "p_depolarize_1q": 0.001,
        "p_depolarize_2q": 0.004,
        "p_readout_flip": 0.010,
    },
    "medium": {
        "p_dephase_layer": 0.008,
        "p_depolarize_1q": 0.003,
        "p_depolarize_2q": 0.012,
        "p_readout_flip": 0.025,
    },
    "heavy": {
        "p_dephase_layer": 0.018,
        "p_depolarize_1q": 0.007,
        "p_depolarize_2q": 0.030,
        "p_readout_flip": 0.050,
    },
}

I2 = v1.I2
X = v1.X
Z = v1.Z
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)

X_FULL = [v1.single_full(X, i) for i in range(4)]
Y_FULL = [v1.single_full(Y, i) for i in range(4)]
Z_FULL = v1.Z_FULL

TWO_PAULIS = {}
for q1, q2 in [(0, 1), (1, 2), (2, 3)]:
    ops = []
    for a in [I2, X, Y, Z]:
        for b in [I2, X, Y, Z]:
            if a is I2 and b is I2:
                continue
            ops.append(v1.two_full(a, q1, b, q2))
    TWO_PAULIS[(q1, q2)] = ops


def jfloat(x: Any, ndigits: int = 12) -> float:
    return round(float(x), ndigits)


def depolarize_1q(rho: np.ndarray, q: int, p: float) -> np.ndarray:
    if p <= 0:
        return rho
    return (1 - p) * rho + (p / 3) * (
        X_FULL[q] @ rho @ X_FULL[q]
        + Y_FULL[q] @ rho @ Y_FULL[q]
        + Z_FULL[q] @ rho @ Z_FULL[q]
    )


def depolarize_2q(rho: np.ndarray, q1: int, q2: int, p: float) -> np.ndarray:
    if p <= 0:
        return rho
    mixed = np.zeros_like(rho)
    for op in TWO_PAULIS[(q1, q2)]:
        mixed += op @ rho @ op
    return (1 - p) * rho + (p / 15) * mixed


def apply_1q(rho: np.ndarray, gate: np.ndarray, q: int, profile: dict) -> np.ndarray:
    rho = v1.apply_u(rho, v1.single_full(gate, q))
    return depolarize_1q(rho, q, profile["p_depolarize_1q"])


def apply_2q_link(rho: np.ndarray, gate: np.ndarray, q1: int, q2: int, profile: dict) -> np.ndarray:
    rho = v1.apply_u(rho, gate)
    return depolarize_2q(rho, q1, q2, profile["p_depolarize_2q"])


def bitflip_probs(probs: np.ndarray, p: float) -> np.ndarray:
    if p <= 0:
        return probs
    out = np.zeros_like(probs)
    for idx, prob in enumerate(probs):
        bits = [(idx >> (3 - j)) & 1 for j in range(4)]
        for mask in range(16):
            new_bits = bits[:]
            weight = prob
            for j in range(4):
                if (mask >> (3 - j)) & 1:
                    weight *= p
                    new_bits[j] ^= 1
                else:
                    weight *= 1 - p
            new_idx = sum(new_bits[j] << (3 - j) for j in range(4))
            out[new_idx] += weight
    return out / out.sum()


def p1w_from_probs(probs: np.ndarray) -> float:
    return float(sum(probs[i] for i in range(16) if format(i, "04b")[3] == "1"))


def p1w_from_counts(counts: dict[str, int]) -> float:
    total = sum(counts.values())
    return sum(count for bits, count in counts.items() if bits[3] == "1") / total


def noisy_probe(arm: str, mask: str, phase: float, profile: dict) -> np.ndarray:
    psi = np.zeros(16, dtype=complex)
    psi[0] = 1.0
    rho = np.outer(psi, psi.conj())

    for q, theta in enumerate(v1.PARAMS["prep_ry"]):
        rho = apply_1q(rho, v1.ry(theta), q, profile)

    # Same v1a lock: phase on M only.
    rho = apply_1q(rho, v1.rz(phase), 0, profile)

    if "M" in mask:
        rho = apply_1q(rho, v1.ry(v1.PARAMS["m_perturb_ry"]), 0, profile)
    if "C" in mask:
        rho = apply_1q(rho, v1.ry(v1.PARAMS["c_perturb_ry"]), 1, profile)

    layers = v1.PARAMS["layers"]

    if arm == "quantum_field_only":
        for layer in range(layers):
            for q in range(4):
                rho = apply_1q(rho, v1.ry(0.16 + 0.02 * q + 0.01 * layer), q, profile)
                rho = apply_1q(rho, v1.rz(0.03 * math.cos(layer + q)), q, profile)
            rho = v1.dephase_all_z(rho, profile["p_dephase_layer"])
        return rho

    if arm == "quantum_no_entangle":
        for layer in range(layers):
            for q in range(4):
                rho = apply_1q(rho, v1.ry(0.15 + 0.03 * q), q, profile)
                rho = apply_1q(rho, v1.rz(0.04 * math.cos(layer + q)), q, profile)
                rho = apply_1q(rho, v1.ry(0.05 * math.sin(layer + 1)), q, profile)
            rho = v1.dephase_all_z(rho, profile["p_dephase_layer"])
        return rho

    if arm in ["quantum_direct_coupled", "quantum_dephased_control"]:
        for layer in range(layers):
            for i, j in [(0, 1), (1, 2), (2, 3)]:
                theta = v1.PARAMS["link_theta_base"] + v1.PARAMS["link_theta_jitter"] * math.sin(layer + i)
                phi = v1.PARAMS["link_zz_phi"] * math.cos(layer + j)
                gate = v1.exp_pauli(v1.XX[(i, j)], theta) @ v1.exp_pauli(v1.ZZ[(i, j)], phi)
                rho = apply_2q_link(rho, gate, i, j, profile)
                rho = apply_1q(rho, v1.ry(v1.PARAMS["downstream_ry_base"] + v1.PARAMS["downstream_ry_jitter"] * layer), j, profile)
                rho = apply_1q(rho, v1.rz(v1.PARAMS["upstream_rz_jitter"] * math.sin(layer + j)), i, profile)
            if arm == "quantum_dephased_control":
                rho = v1.dephase_all_z(rho, v1.PARAMS["dephase_p_after_each_link_layer"])
            rho = v1.dephase_all_z(rho, profile["p_dephase_layer"])
        return rho

    raise ValueError(f"unknown arm: {arm}")


def exact_profile_probs(profile: dict) -> tuple[dict, dict]:
    exact = {}
    probs = {}
    for arm in ARMS:
        rho0 = noisy_probe(arm, "M", 0.0, profile)
        rhop = noisy_probe(arm, "M", math.pi / 2, profile)
        p0 = bitflip_probs(v1.probs_z(rho0), profile["p_readout_flip"])
        pp = bitflip_probs(v1.probs_z(rhop), profile["p_readout_flip"])
        exact[arm] = {
            "P1W_phase0_exact": p1w_from_probs(p0),
            "P1W_phase_pi2_exact": p1w_from_probs(pp),
            "oriented_effect_exact": p1w_from_probs(p0) - p1w_from_probs(pp),
        }
        probs[(arm, "M")] = p0
        probs[(arm, "M_phase_pi2")] = pp
    return exact, probs


def bootstrap_mean_ci(vals: list[float], seed: int) -> tuple[float, float, float]:
    rng = np.random.default_rng(seed)
    arr = np.array(vals, dtype=float)
    means = np.empty(10000)
    for i in range(10000):
        means[i] = rng.choice(arr, size=len(arr), replace=True).mean()
    lo, hi = np.quantile(means, [0.025, 0.975])
    return float(means.mean()), float(lo), float(hi)


def paired_diff_ci(a: list[float], b: list[float], seed: int) -> tuple[float, float, float]:
    rng = np.random.default_rng(seed)
    diff = np.array(a, dtype=float) - np.array(b, dtype=float)
    means = np.empty(10000)
    for i in range(10000):
        idx = rng.integers(0, len(diff), len(diff))
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


def exact_p_if_u_max(n: int, m: int, u: float) -> float | None:
    if u == n * m:
        return 1.0 / math.comb(n + m, n)
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-json", type=Path, default=Path("data/quantum_observation/classical_vs_quantum_part_coupling_v2_noise_seed20260741_20260756.json"))
    parser.add_argument("--summary-csv", type=Path, default=Path("data/quantum_observation/classical_vs_quantum_part_coupling_v2_noise_seed20260741_20260756_summary.csv"))
    args = parser.parse_args()

    rows = []
    exact_by_profile = {}

    for profile_name, profile in PROFILES.items():
        exact, probs = exact_profile_probs(profile)
        exact_by_profile[profile_name] = exact
        for seed in SEEDS:
            rng = np.random.default_rng(seed)
            for arm in ARMS:
                counts0 = v1.counts_from_probs(probs[(arm, "M")], rng)
                countsp = v1.counts_from_probs(probs[(arm, "M_phase_pi2")], rng)
                p0 = p1w_from_counts(counts0)
                pp = p1w_from_counts(countsp)
                rows.append({
                    "profile": profile_name,
                    "seed": seed,
                    "arm": arm,
                    "exact_oriented_effect": exact[arm]["oriented_effect_exact"],
                    "P1W_phase0": p0,
                    "P1W_phase_pi2": pp,
                    "oriented_effect": p0 - pp,
                })

    summary = []
    comparisons = {}
    criteria = {}
    for profile_name in PROFILES:
        by_arm = {arm: [r["oriented_effect"] for r in rows if r["profile"] == profile_name and r["arm"] == arm] for arm in ARMS}
        comparisons[profile_name] = {}
        for arm, vals in by_arm.items():
            _, lo, hi = bootstrap_mean_ci(vals, seed=7000 + len(profile_name) + len(arm))
            summary.append({
                "profile": profile_name,
                "arm": arm,
                "exact_oriented_effect": exact_by_profile[profile_name][arm]["oriented_effect_exact"],
                "mean_oriented_effect": float(np.mean(vals)),
                "std_oriented_effect": float(np.std(vals, ddof=1)),
                "min_oriented_effect": float(np.min(vals)),
                "max_oriented_effect": float(np.max(vals)),
                "positive_count": int(np.sum(np.array(vals) > 0)),
                "negative_count": int(np.sum(np.array(vals) < 0)),
                "zero_count": int(np.sum(np.array(vals) == 0)),
                "bootstrap_ci95_low": lo,
                "bootstrap_ci95_high": hi,
            })
        direct = by_arm["quantum_direct_coupled"]
        for control in ["quantum_field_only", "quantum_no_entangle", "quantum_dephased_control"]:
            ctrl = by_arm[control]
            _, lo, hi = paired_diff_ci(direct, ctrl, seed=8000 + len(profile_name) + len(control))
            u = mann_u_stat(direct, ctrl)
            comparisons[profile_name][control] = {
                "direct_minus_control_seed_mean": float(np.mean(np.array(direct) - np.array(ctrl))),
                "direct_minus_control_ci95_low": lo,
                "direct_minus_control_ci95_high": hi,
                "mann_whitney_u": u,
                "mann_whitney_u_max": len(direct) * len(ctrl),
                "one_sided_exact_p_if_u_max": exact_p_if_u_max(len(direct), len(ctrl), u),
                "direct_min_minus_control_max": float(min(direct) - max(ctrl)),
            }

        by_summary = {s["arm"]: s for s in summary if s["profile"] == profile_name}
        direct_s = by_summary["quantum_direct_coupled"]
        no_s = by_summary["quantum_no_entangle"]
        field_s = by_summary["quantum_field_only"]
        deph_s = by_summary["quantum_dephased_control"]
        floor = max(abs(field_s["mean_oriented_effect"]), abs(no_s["mean_oriented_effect"]), abs(deph_s["mean_oriented_effect"]))
        criteria[profile_name] = {
            "main_pass": direct_s["bootstrap_ci95_low"] > 0,
            "leakage_pass": no_s["bootstrap_ci95_low"] <= 0 <= no_s["bootstrap_ci95_high"] and no_s["positive_count"] > 0 and no_s["negative_count"] > 0,
            "separation_pass": comparisons[profile_name]["quantum_no_entangle"]["direct_minus_control_ci95_low"] > 0 and comparisons[profile_name]["quantum_no_entangle"]["one_sided_exact_p_if_u_max"] is not None and comparisons[profile_name]["quantum_no_entangle"]["one_sided_exact_p_if_u_max"] < 0.01,
            "field_support": field_s["bootstrap_ci95_low"] <= 0 <= field_s["bootstrap_ci95_high"],
            "dephased_support": deph_s["bootstrap_ci95_low"] <= 0 <= deph_s["bootstrap_ci95_high"] and comparisons[profile_name]["quantum_dephased_control"]["direct_minus_control_ci95_low"] > 0,
            "floor": floor,
            "floor_ok": floor < 0.05,
        }
        criteria[profile_name]["profile_survives"] = criteria[profile_name]["main_pass"] and criteria[profile_name]["leakage_pass"] and criteria[profile_name]["separation_pass"] and criteria[profile_name]["floor_ok"]

    if criteria["none"]["profile_survives"] and criteria["light"]["profile_survives"] and criteria["medium"]["profile_survives"]:
        verdict = "PASS_NOISE_MODEL_CANDIDATE"
    elif criteria["none"]["profile_survives"] and criteria["light"]["profile_survives"]:
        verdict = "PARTIAL_NOISE_MODEL_CANDIDATE"
    elif criteria["none"]["profile_survives"]:
        verdict = "NOISE_MODEL_FRAGILE"
    else:
        verdict = "NOISE_MODEL_REJECT"

    result = {
        "experiment": "classical_vs_quantum_part_coupling_v2_noise_model",
        "date": "2026-07-09",
        "status": "OBSERVATION_LOG",
        "protocol": "experiments/classical_vs_quantum_part_coupling_v2_noise_protocol_20260709.md",
        "summary_csv": str(args.summary_csv),
        "config": {
            "shots_per_seed": v1.SHOTS,
            "noise_seeds": SEEDS,
            "inference_unit": "seed",
            "profiles": PROFILES,
            "estimator": "P1_W(phaseM=0,M perturb) - P1_W(phaseM=pi/2,M perturb)",
        },
        "summary": summary,
        "comparisons": comparisons,
        "criteria": criteria,
        "overall_verdict": verdict,
        "notes": [
            "Simple pre-hardware noise model; not backend-calibrated.",
            "No QPU submission is included.",
            "Heavy profile is diagnostic only.",
        ],
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    args.summary_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.summary_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["profile", "seed", "arm", "exact_oriented_effect", "P1W_phase0", "P1W_phase_pi2", "oriented_effect"])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(json.dumps({"experiment": result["experiment"], "criteria": criteria, "overall_verdict": verdict}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
