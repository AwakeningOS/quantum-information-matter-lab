#!/usr/bin/env python3
"""classical_vs_quantum_part_coupling_v1_measurable_witness

v1 replaces the v0 tomography-heavy negativity witness with measurable output
witnesses:

- phase_sens_P1W
- output_nonadditivity_P1W
- output_nonadditivity_ZZRW

Protocol lock:
- Rz phase is injected on M only.
- W is the population readout qubit.
- Dephased control inserts Z-dephasing during link propagation, not only at readout.
- link negativity is auxiliary only and not claim-bearing.

This is an ideal NumPy density-matrix simulation with 4096-shot sampling and
bootstrap. It is not a noise simulation and not a QPU result.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

SEED = 20260709
SHOTS = 4096
BOOTSTRAPS = 1000

ARMS = [
    "classical_if",
    "classical_coupled",
    "quantum_field_only",
    "quantum_no_entangle",
    "quantum_direct_coupled",
    "quantum_dephased_control",
]

CONDITIONS = [
    ("base", "", 0.0),
    ("M", "M", 0.0),
    ("C", "C", 0.0),
    ("MC", "MC", 0.0),
    ("M_phase_pi2", "M", math.pi / 2),
]

PARAMS = {
    "layers": 6,
    "prep_ry": [1.6, 0.7, 0.45, 0.2],
    "m_perturb_ry": 0.5,
    "c_perturb_ry": 0.8,
    "link_theta_base": 1.3,
    "link_theta_jitter": 0.15,
    "link_zz_phi": 0.35,
    "downstream_ry_base": 1.0,
    "downstream_ry_jitter": 0.05,
    "upstream_rz_jitter": 0.10,
    "dephase_p_after_each_link_layer": 0.20,
}

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)


def jfloat(x: Any, ndigits: int = 12) -> float:
    return round(float(x), ndigits)


def kron_all(ops: list[np.ndarray]) -> np.ndarray:
    out = np.array([[1]], dtype=complex)
    for op in ops:
        out = np.kron(out, op)
    return out


def single_full(op: np.ndarray, q: int, n: int = 4) -> np.ndarray:
    return kron_all([op if i == q else I2 for i in range(n)])


def two_full(op1: np.ndarray, q1: int, op2: np.ndarray, q2: int, n: int = 4) -> np.ndarray:
    return kron_all([op1 if i == q1 else op2 if i == q2 else I2 for i in range(n)])


def ry(theta: float) -> np.ndarray:
    return np.array(
        [[math.cos(theta / 2), -math.sin(theta / 2)], [math.sin(theta / 2), math.cos(theta / 2)]],
        dtype=complex,
    )


def rz(theta: float) -> np.ndarray:
    return np.array([[np.exp(-1j * theta / 2), 0], [0, np.exp(1j * theta / 2)]], dtype=complex)


Z_FULL = [single_full(Z, i) for i in range(4)]
XX = {(i, j): two_full(X, i, X, j) for i, j in [(0, 1), (1, 2), (2, 3)]}
ZZ = {(i, j): two_full(Z, i, Z, j) for i, j in [(0, 1), (1, 2), (2, 3)]}


def exp_pauli(pauli_op: np.ndarray, theta: float) -> np.ndarray:
    return math.cos(theta / 2) * np.eye(pauli_op.shape[0], dtype=complex) - 1j * math.sin(theta / 2) * pauli_op


def apply_u(rho: np.ndarray, u: np.ndarray) -> np.ndarray:
    return u @ rho @ u.conj().T


def dephase_all_z(rho: np.ndarray, p: float) -> np.ndarray:
    out = rho.copy()
    for z in Z_FULL:
        out = (1 - p) * out + p * (z @ out @ z)
    return out


def p1(rho: np.ndarray, q: int) -> float:
    return float(np.real((1 - np.trace(rho @ Z_FULL[q])) / 2))


def zz_expectation(rho: np.ndarray, i: int, j: int) -> float:
    return float(np.real(np.trace(rho @ (Z_FULL[i] @ Z_FULL[j]))))


def probs_z(rho: np.ndarray) -> np.ndarray:
    probs = np.real(np.diag(rho)).clip(0)
    return probs / probs.sum()


def bitstr(index: int, n: int = 4) -> str:
    return format(index, f"0{n}b")


def reduce_dm(rho: np.ndarray, keep: list[int], n: int = 4) -> np.ndarray:
    trace_over = [i for i in range(n) if i not in keep]
    red = np.zeros((2 ** len(keep), 2 ** len(keep)), dtype=complex)
    for a in range(2**n):
        ba = [(a >> (n - 1 - i)) & 1 for i in range(n)]
        ia = sum(ba[k] << (len(keep) - 1 - j) for j, k in enumerate(keep))
        for b in range(2**n):
            bb = [(b >> (n - 1 - i)) & 1 for i in range(n)]
            if all(ba[t] == bb[t] for t in trace_over):
                ib = sum(bb[k] << (len(keep) - 1 - j) for j, k in enumerate(keep))
                red[ia, ib] += rho[a, b]
    return red


def negativity_2q(rho2: np.ndarray) -> float:
    arr = rho2.reshape(2, 2, 2, 2)
    partial_transpose = arr.swapaxes(1, 3).reshape(4, 4)
    eig = np.linalg.eigvalsh(partial_transpose)
    return float(np.sum(np.abs(eig[eig < 0])))


def quantum_probe(arm: str, mask: str = "", phase: float = 0.0) -> np.ndarray:
    psi = np.zeros(16, dtype=complex)
    psi[0] = 1.0
    rho = np.outer(psi, psi.conj())

    for q, theta in enumerate(PARAMS["prep_ry"]):
        rho = apply_u(rho, single_full(ry(theta), q))

    # v1 lock: phase injection on M only. Never inject phase on C/R/W.
    rho = apply_u(rho, single_full(rz(phase), 0))

    if "M" in mask:
        rho = apply_u(rho, single_full(ry(PARAMS["m_perturb_ry"]), 0))
    if "C" in mask:
        rho = apply_u(rho, single_full(ry(PARAMS["c_perturb_ry"]), 1))

    layers = PARAMS["layers"]

    if arm == "quantum_field_only":
        for layer in range(layers):
            for q in range(4):
                rho = apply_u(rho, single_full(ry(0.16 + 0.02 * q + 0.01 * layer), q))
                rho = apply_u(rho, single_full(rz(0.03 * math.cos(layer + q)), q))
        return rho

    if arm == "quantum_no_entangle":
        for layer in range(layers):
            for q in range(4):
                rho = apply_u(rho, single_full(ry(0.15 + 0.03 * q), q))
                rho = apply_u(rho, single_full(rz(0.04 * math.cos(layer + q)), q))
                rho = apply_u(rho, single_full(ry(0.05 * math.sin(layer + 1)), q))
        return rho

    if arm in ["quantum_direct_coupled", "quantum_dephased_control"]:
        for layer in range(layers):
            for i, j in [(0, 1), (1, 2), (2, 3)]:
                theta = PARAMS["link_theta_base"] + PARAMS["link_theta_jitter"] * math.sin(layer + i)
                phi = PARAMS["link_zz_phi"] * math.cos(layer + j)
                rho = apply_u(rho, exp_pauli(XX[(i, j)], theta) @ exp_pauli(ZZ[(i, j)], phi))
                # Local basis conversion after link, not phase injection.
                rho = apply_u(rho, single_full(ry(PARAMS["downstream_ry_base"] + PARAMS["downstream_ry_jitter"] * layer), j))
                rho = apply_u(rho, single_full(rz(PARAMS["upstream_rz_jitter"] * math.sin(layer + j)), i))
            if arm == "quantum_dephased_control":
                rho = dephase_all_z(rho, PARAMS["dephase_p_after_each_link_layer"])
        return rho

    raise ValueError(f"unknown quantum arm: {arm}")


def counts_from_probs(probs: np.ndarray, rng: np.random.Generator) -> dict[str, int]:
    draws = rng.multinomial(SHOTS, probs)
    return {bitstr(i): int(c) for i, c in enumerate(draws) if int(c) > 0}


def resample_counts(counts: dict[str, int], rng: np.random.Generator) -> dict[str, int]:
    keys = list(counts.keys())
    weights = np.array([counts[k] for k in keys], dtype=float)
    probs = weights / weights.sum()
    draws = rng.multinomial(SHOTS, probs)
    return {k: int(c) for k, c in zip(keys, draws) if int(c) > 0}


def metrics_from_counts(counts: dict[str, int]) -> dict[str, float]:
    total = sum(counts.values())
    w1 = 0
    zz = 0
    for bits, count in counts.items():
        if bits[3] == "1":
            w1 += count
        zr = 1 if bits[2] == "0" else -1
        zw = 1 if bits[3] == "0" else -1
        zz += zr * zw * count
    return {"P1_W": w1 / total, "ZZ_RW": zz / total}


def witness_from_metrics(metrics: dict[str, dict[str, float]]) -> dict[str, float]:
    return {
        "phase_sens_P1W": abs(metrics["M_phase_pi2"]["P1_W"] - metrics["M"]["P1_W"]),
        "output_nonadditivity_P1W": abs(
            metrics["MC"]["P1_W"] - metrics["M"]["P1_W"] - metrics["C"]["P1_W"] + metrics["base"]["P1_W"]
        ),
        "output_nonadditivity_ZZRW": abs(
            metrics["MC"]["ZZ_RW"] - metrics["M"]["ZZ_RW"] - metrics["C"]["ZZ_RW"] + metrics["base"]["ZZ_RW"]
        ),
    }


def exact_summary_for_arm(arm: str) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    exact_metrics = {}
    probs = {}
    neg_aux = []
    for name, mask, phase in CONDITIONS:
        rho = quantum_probe(arm, mask, phase)
        exact_metrics[name] = {"P1_W": p1(rho, 3), "ZZ_RW": zz_expectation(rho, 2, 3)}
        probs[name] = probs_z(rho)
        neg_aux.append(negativity_2q(reduce_dm(rho, [2, 3])))
    witnesses = witness_from_metrics(exact_metrics)
    summary = {
        "phase_sens_P1W_exact": witnesses["phase_sens_P1W"],
        "output_nonadditivity_P1W_exact": witnesses["output_nonadditivity_P1W"],
        "output_nonadditivity_ZZRW_exact": witnesses["output_nonadditivity_ZZRW"],
        "link_negativity_aux_max": max(neg_aux),
    }
    return summary, probs


def bootstrap_witnesses(arm: str, raw_counts: dict[str, dict[str, int]], rng: np.random.Generator) -> dict[str, np.ndarray]:
    keys = ["phase_sens_P1W", "output_nonadditivity_P1W", "output_nonadditivity_ZZRW"]
    if arm.startswith("classical"):
        return {k: np.zeros(BOOTSTRAPS) for k in keys}
    out = {k: [] for k in keys}
    for _ in range(BOOTSTRAPS):
        metrics = {name: metrics_from_counts(resample_counts(raw_counts[name], rng)) for name, _, _ in CONDITIONS}
        witnesses = witness_from_metrics(metrics)
        for k in keys:
            out[k].append(witnesses[k])
    return {k: np.array(v) for k, v in out.items()}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-json", type=Path, default=Path("data/quantum_observation/classical_vs_quantum_part_coupling_v1_seed20260709.json"))
    parser.add_argument("--summary-csv", type=Path, default=Path("data/quantum_observation/classical_vs_quantum_part_coupling_v1_seed20260709_summary.csv"))
    args = parser.parse_args()

    rng = np.random.default_rng(SEED)
    summaries = []
    raw_counts: dict[str, dict[str, dict[str, int]]] = {}
    observed_metrics: dict[str, dict[str, dict[str, float]]] = {}

    for arm in ARMS:
        if arm.startswith("classical"):
            raw_counts[arm] = {}
            observed_metrics[arm] = {}
            summaries.append({
                "arm": arm,
                "phase_sens_P1W_exact": 0.0,
                "output_nonadditivity_P1W_exact": 0.0,
                "output_nonadditivity_ZZRW_exact": 0.0,
                "link_negativity_aux_max": 0.0,
                "phase_sens_P1W_shot": 0.0,
                "output_nonadditivity_P1W_shot": 0.0,
                "output_nonadditivity_ZZRW_shot": 0.0,
            })
            continue

        exact_summary, probs = exact_summary_for_arm(arm)
        raw_counts[arm] = {name: counts_from_probs(probs[name], rng) for name, _, _ in CONDITIONS}
        observed_metrics[arm] = {name: metrics_from_counts(raw_counts[arm][name]) for name, _, _ in CONDITIONS}
        shot_witnesses = witness_from_metrics(observed_metrics[arm])
        row = {"arm": arm}
        row.update({k: jfloat(v, 12) for k, v in exact_summary.items()})
        row.update({k + "_shot": jfloat(v, 12) for k, v in shot_witnesses.items()})
        summaries.append(row)

    boots = {arm: bootstrap_witnesses(arm, raw_counts.get(arm, {}), rng) for arm in ARMS}
    controls = ["classical_if", "classical_coupled", "quantum_field_only", "quantum_no_entangle", "quantum_dephased_control"]
    bootstrap_comparisons: dict[str, dict[str, Any]] = {}
    for control in controls:
        bootstrap_comparisons[control] = {}
        for witness in ["phase_sens_P1W", "output_nonadditivity_P1W", "output_nonadditivity_ZZRW"]:
            delta = boots["quantum_direct_coupled"][witness] - boots[control][witness]
            lo, hi = np.quantile(delta, [0.025, 0.975])
            bootstrap_comparisons[control][witness] = {
                "direct_minus_control_mean": jfloat(delta.mean(), 12),
                "ci95_low": jfloat(lo, 12),
                "ci95_high": jfloat(hi, 12),
                "ci_excludes_0": bool(lo > 0 or hi < 0),
            }

    direct = next(s for s in summaries if s["arm"] == "quantum_direct_coupled")
    dephased = next(s for s in summaries if s["arm"] == "quantum_dephased_control")

    def reduction(direct_value: float, control_value: float) -> float:
        return 1 - control_value / max(direct_value, 1e-12)

    main_keep = (
        bootstrap_comparisons["quantum_field_only"]["phase_sens_P1W"]["ci_excludes_0"]
        and bootstrap_comparisons["quantum_no_entangle"]["phase_sens_P1W"]["ci_excludes_0"]
        and bootstrap_comparisons["quantum_dephased_control"]["phase_sens_P1W"]["ci_excludes_0"]
    )
    secondary_keep = (
        bootstrap_comparisons["quantum_no_entangle"]["output_nonadditivity_P1W"]["ci_excludes_0"]
        and bootstrap_comparisons["quantum_dephased_control"]["output_nonadditivity_P1W"]["ci_excludes_0"]
    )
    diagnostic_keep = (
        bootstrap_comparisons["quantum_no_entangle"]["output_nonadditivity_ZZRW"]["ci_excludes_0"]
        and bootstrap_comparisons["quantum_dephased_control"]["output_nonadditivity_ZZRW"]["ci_excludes_0"]
    )
    if main_keep and (secondary_keep or diagnostic_keep):
        verdict = "PASS_MEASURABLE_WITNESS_SURVIVES"
    elif main_keep:
        verdict = "PARTIAL_WITNESS_SURVIVES"
    else:
        verdict = "WITNESS_COLLAPSED_ON_REPLACEMENT"

    result = {
        "experiment": "classical_vs_quantum_part_coupling_v1_measurable_witness",
        "date": "2026-07-09",
        "layer": "QUANTUM_OBSERVATION -> QUANTUM_AUDIT candidate",
        "status": "OBSERVATION_LOG",
        "protocol": "experiments/classical_vs_quantum_part_coupling_v1_protocol_20260709.md",
        "config": {
            "seed": SEED,
            "shots": SHOTS,
            "bootstrap_resamples": BOOTSTRAPS,
            "phase_injection": "M only",
            "readout": ["P1_W", "ZZ_RW"],
            "dephased_arm": "Z-dephase all four qubits after each full link layer",
            "params": PARAMS,
            "arms": ARMS,
            "conditions": [{"name": n, "mask": m, "phase": p} for n, m, p in CONDITIONS],
        },
        "scenario_summaries": summaries,
        "bootstrap_comparisons": bootstrap_comparisons,
        "derived": {
            "dephase_reduction_phase_sens_exact": jfloat(reduction(direct["phase_sens_P1W_exact"], dephased["phase_sens_P1W_exact"]), 12),
            "dephase_reduction_nonadd_P1W_exact": jfloat(reduction(direct["output_nonadditivity_P1W_exact"], dephased["output_nonadditivity_P1W_exact"]), 12),
            "dephase_reduction_ZZRW_exact": jfloat(reduction(direct["output_nonadditivity_ZZRW_exact"], dephased["output_nonadditivity_ZZRW_exact"]), 12),
            "shot_noise_reference_single_prob_se_4096": jfloat(math.sqrt(0.25 / SHOTS), 12),
            "shot_noise_reference_difference_two_se_4096": jfloat(math.sqrt(2) * math.sqrt(0.25 / SHOTS), 12),
            "main_phase_sens_keep": main_keep,
            "secondary_P1W_nonadd_keep": secondary_keep,
            "diagnostic_ZZRW_nonadd_keep": diagnostic_keep,
            "verdict": verdict,
        },
        "raw_counts": raw_counts,
        "notes": [
            "v0 injected phase on all qubits; v1 locks Rz phase to M only.",
            "link_negativity is auxiliary only and not claim-bearing.",
            "This is ideal density-matrix simulation with shot sampling/bootstrap, not a noise simulation or QPU result.",
        ],
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    keys: list[str] = []
    for row in summaries:
        for key in row.keys():
            if key not in keys:
                keys.append(key)
    args.summary_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.summary_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(summaries)

    print(json.dumps({"experiment": result["experiment"], "verdict": verdict, "scenario_summaries": summaries, "bootstrap_comparisons": bootstrap_comparisons, "derived": result["derived"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
