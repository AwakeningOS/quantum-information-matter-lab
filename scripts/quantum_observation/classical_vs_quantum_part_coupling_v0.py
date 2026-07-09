#!/usr/bin/env python3
"""classical_vs_quantum_part_coupling_v0

Compare classical part-coupling controls against a minimal quantum-circuit
part-coupling model.

Goal:
  Separate "parts move because explicit rules made them move" from
  "parts are coupled inside a shared quantum state and lose that coupling
   under dephasing/measurement-like disturbance."

This is an OBSERVATION_LOG, not a proof of advantage.

Parts:
  M = membrane / boundary
  C = conversion
  R = recycler / repair
  W = waste outlet

Arms:
  classical_if_controller
  classical_coupled_dynamics
  quantum_field_only
  quantum_direct_coupled
  quantum_dephased_control
  measurement_feedback
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

ARMS = [
    "classical_if_controller",
    "classical_coupled_dynamics",
    "quantum_field_only",
    "quantum_direct_coupled",
    "quantum_dephased_control",
    "measurement_feedback",
]

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(x)))


def jfloat(x: Any, ndigits: int = 12) -> float:
    return round(float(x), ndigits)


def kron_all(ops: list[np.ndarray]) -> np.ndarray:
    out = np.array([[1]], dtype=complex)
    for op in ops:
        out = np.kron(out, op)
    return out


def single_full(op: np.ndarray, q: int, n: int = 4) -> np.ndarray:
    return kron_all([op if i == q else I2 for i in range(n)])


def two_full(op: np.ndarray, q1: int, q2: int, n: int = 4) -> np.ndarray:
    return kron_all([op if i in (q1, q2) else I2 for i in range(n)])


def ry(theta: float) -> np.ndarray:
    return np.array(
        [
            [math.cos(theta / 2), -math.sin(theta / 2)],
            [math.sin(theta / 2), math.cos(theta / 2)],
        ],
        dtype=complex,
    )


def rz(theta: float) -> np.ndarray:
    return np.array(
        [[np.exp(-1j * theta / 2), 0], [0, np.exp(1j * theta / 2)]],
        dtype=complex,
    )


Z_FULL = [single_full(Z, i) for i in range(4)]
XX = {(i, j): two_full(X, i, j) for i, j in [(0, 1), (1, 2), (2, 3)]}
ZZ = {(i, j): two_full(Z, i, j) for i, j in [(0, 1), (1, 2), (2, 3)]}


def exp_pauli(pauli_op: np.ndarray, theta: float) -> np.ndarray:
    return math.cos(theta / 2) * np.eye(pauli_op.shape[0], dtype=complex) - 1j * math.sin(theta / 2) * pauli_op


def apply_u(rho: np.ndarray, u: np.ndarray) -> np.ndarray:
    return u @ rho @ u.conj().T


def dephase(rho: np.ndarray, p: float) -> np.ndarray:
    out = rho.copy()
    for zi in Z_FULL:
        out = (1 - p) * out + p * (zi @ out @ zi)
    return out


def p1(rho: np.ndarray, q: int) -> float:
    return float(np.real((1 - np.trace(rho @ Z_FULL[q])) / 2))


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


def external_drive(t: int) -> np.ndarray:
    food = 0.35 + 0.35 * math.exp(-((t - 20) / 10) ** 2) + 0.15 * math.sin(2 * math.pi * t / 48)
    toxin = 0.10 + 0.70 * math.exp(-((t - 38) / 9) ** 2) + 0.40 * math.exp(-((t - 82) / 12) ** 2)
    pressure = 0.25 + 0.50 * math.exp(-((t - 52) / 14) ** 2)
    return np.array([clamp(food), clamp(toxin), clamp(pressure)])


def in_range_score(x: float, lo: float, hi: float) -> float:
    if lo <= x <= hi:
        return 1.0
    if x < lo:
        return max(0.0, 1 - (lo - x) / max(lo, 1e-9))
    return max(0.0, 1 - (x - hi) / max(1 - hi, 1e-9))


def desired_roles(state: np.ndarray, ext: np.ndarray) -> np.ndarray:
    energy, toxicity, pressure, damage, fatigue = state
    food, external_toxicity, external_pressure = ext
    toxicity_excess = max(0.0, toxicity - 0.20) + 0.35 * external_toxicity
    pressure_excess = max(0.0, pressure - 0.60) + 0.25 * external_pressure
    energy_deficit = max(0.0, 0.62 - energy)
    m_close = clamp(0.25 + 0.62 * toxicity_excess + 0.48 * pressure_excess - 0.40 * energy_deficit)
    c_convert = clamp(0.15 + 0.75 * energy_deficit + 0.25 * food)
    r_recycle = clamp(0.12 + 0.72 * damage + 0.35 * fatigue)
    w_waste = clamp(
        0.12
        + 0.75 * max(0.0, toxicity - 0.18)
        + 0.45 * max(0.0, pressure - 0.62)
        + 0.30 * external_toxicity
    )
    return np.array([m_close, c_convert, r_recycle, w_waste])


def update_internal_state(state: np.ndarray, response: np.ndarray, ext: np.ndarray, arm: str) -> np.ndarray:
    energy, toxicity, pressure, damage, fatigue = state
    m_boundary, c_convert, r_recycle, w_waste = response
    food, external_toxicity, external_pressure = ext
    openness = clamp(1 - m_boundary)
    measurement_cost = 0.010 if arm == "measurement_feedback" else 0.0

    energy += 0.050 * food * openness + 0.030 * c_convert - 0.018 * r_recycle - 0.014 * w_waste - 0.010
    energy -= 0.020 * measurement_cost
    toxicity += 0.095 * external_toxicity * openness - 0.075 * w_waste - 0.010 * r_recycle + 0.006 * c_convert
    pressure += 0.065 * external_pressure * openness + 0.018 * food * openness + 0.012 * c_convert - 0.065 * w_waste
    damage += 0.020 * max(0.0, toxicity - 0.25) + 0.018 * max(0.0, pressure - 0.65) - 0.055 * r_recycle
    damage += 0.006 * fatigue
    fatigue += 0.006 * float(np.sum(response)) + measurement_cost + 0.010 * max(0.0, pressure - 0.70) - 0.025 * r_recycle

    return np.array([clamp(energy), clamp(toxicity), clamp(pressure), clamp(damage), clamp(fatigue)])


def corr(a: np.ndarray, b: np.ndarray) -> float:
    af = np.asarray(a).flatten()
    bf = np.asarray(b).flatten()
    if np.std(af) < 1e-9 or np.std(bf) < 1e-9:
        return 0.0
    return float(np.corrcoef(af, bf)[0, 1])


def simulate_arm(arm: str, steps: int = 96) -> tuple[list[dict], dict]:
    state = np.array([0.70, 0.06, 0.45, 0.02, 0.03])
    classical_state = np.zeros(4)

    psi = np.zeros(16, dtype=complex)
    psi[0] = 1.0
    rho = np.outer(psi, psi.conj())

    rows = []
    desired_log = []
    response_log = []
    neg_log = []
    boundary_work = []
    previous_m = None
    target_hits = 0
    resource_intake_sum = 0.0

    for t in range(steps):
        ext = external_drive(t)
        desired = desired_roles(state, ext)

        if arm == "classical_if_controller":
            response = (desired > 0.47).astype(float)
            if previous_m is not None:
                response[0] = 0.75 * response[0] + 0.25 * previous_m
            neg = (0.0, 0.0, 0.0)

        elif arm == "classical_coupled_dynamics":
            neighbor = np.array(
                [
                    classical_state[1],
                    (classical_state[0] + classical_state[2]) / 2,
                    (classical_state[1] + classical_state[3]) / 2,
                    classical_state[2],
                ]
            )
            classical_state = np.array(
                [clamp(v) for v in 0.62 * classical_state + 0.28 * desired + 0.22 * (neighbor - classical_state)]
            )
            response = classical_state.copy()
            neg = (0.0, 0.0, 0.0)

        else:
            for q in range(4):
                theta = 0.45 * (desired[q] - 0.25)
                if arm == "quantum_field_only":
                    theta += 0.20 * (float(np.mean(desired)) - 0.35)
                rho = apply_u(rho, single_full(ry(theta), q))

            phase_context = 0.35 * math.sin(2 * math.pi * t / 32) + 0.25 * (ext[1] - ext[0])
            for q in range(4):
                rho = apply_u(rho, single_full(rz(phase_context * (0.5 + 0.15 * q)), q))

            if arm in ["quantum_direct_coupled", "quantum_dephased_control", "measurement_feedback"]:
                need = float(np.mean(desired))
                for i, j in [(0, 1), (1, 2), (2, 3)]:
                    theta = 0.18 + 0.26 * need + 0.14 * abs(desired[i] - desired[j])
                    u = exp_pauli(XX[(i, j)], theta) @ exp_pauli(ZZ[(i, j)], 0.08 * math.sin(phase_context + i))
                    rho = apply_u(rho, u)

            else:
                for q in range(4):
                    rho = apply_u(rho, single_full(ry(0.04 * math.sin(phase_context)), q))

            if arm == "quantum_dephased_control":
                rho = dephase(rho, 0.045 + 0.030 * ext[1])
            elif arm == "measurement_feedback":
                rho = dephase(rho, 0.080 + 0.050 * ext[1])
                probs = np.array([p1(rho, q) for q in range(4)])
                for q in range(4):
                    rho = apply_u(rho, single_full(ry(0.18 * (desired[q] - probs[q])), q))
                rho = dephase(rho, 0.050)

            response = np.array([p1(rho, q) for q in range(4)])
            neg = (
                negativity_2q(reduce_dm(rho, [0, 1])),
                negativity_2q(reduce_dm(rho, [1, 2])),
                negativity_2q(reduce_dm(rho, [2, 3])),
            )
            neg_log.append(neg)

        state = update_internal_state(state, response, ext, arm)
        target_score = (
            in_range_score(state[0], 0.60, 0.80)
            + in_range_score(state[1], 0.00, 0.20)
            + in_range_score(state[2], 0.30, 0.60)
            + in_range_score(state[3], 0.00, 0.20)
        ) / 4

        if target_score > 0.75:
            target_hits += 1

        openness = clamp(1 - response[0])
        intake = ext[0] * openness
        resource_intake_sum += intake

        if previous_m is not None:
            boundary_work.append(abs(float(response[0] - previous_m)))
        previous_m = float(response[0])

        desired_log.append(desired)
        response_log.append(response)

        rows.append(
            {
                "t": t,
                "arm": arm,
                "energy": jfloat(state[0], 9),
                "toxicity": jfloat(state[1], 9),
                "pressure": jfloat(state[2], 9),
                "damage": jfloat(state[3], 9),
                "fatigue": jfloat(state[4], 9),
                "M_response": jfloat(response[0], 9),
                "C_response": jfloat(response[1], 9),
                "R_response": jfloat(response[2], 9),
                "W_response": jfloat(response[3], 9),
                "M_desired": jfloat(desired[0], 9),
                "C_desired": jfloat(desired[1], 9),
                "R_desired": jfloat(desired[2], 9),
                "W_desired": jfloat(desired[3], 9),
                "neg_M_C": jfloat(neg[0], 12),
                "neg_C_R": jfloat(neg[1], 12),
                "neg_R_W": jfloat(neg[2], 12),
                "target_score": jfloat(target_score, 9),
                "resource_intake": jfloat(intake, 9),
            }
        )

    desired_arr = np.array(desired_log)
    response_arr = np.array(response_log)
    neg_arr = np.array(neg_log) if neg_log else np.zeros((steps, 3))

    target_range_fraction = target_hits / steps
    resource_intake_fraction = min(1.0, resource_intake_sum / (steps * 0.45))
    boundary_work_rate = float(np.mean(boundary_work)) if boundary_work else 0.0
    efficiency_factor = 1.0 / (1.0 + 3.5 * boundary_work_rate)
    homeostasis_balance = target_range_fraction * resource_intake_fraction * efficiency_factor
    peaks = np.argmax(neg_arr, axis=0) if neg_log else np.array([0, 0, 0])

    summary = {
        "arm": arm,
        "target_range_fraction": jfloat(target_range_fraction, 9),
        "resource_intake_fraction": jfloat(resource_intake_fraction, 9),
        "boundary_work_rate": jfloat(boundary_work_rate, 9),
        "efficiency_factor": jfloat(efficiency_factor, 9),
        "homeostasis_balance": jfloat(homeostasis_balance, 9),
        "role_alignment": jfloat(corr(desired_arr, response_arr), 9),
        "part_specialization": jfloat(np.mean(np.std(response_arr, axis=1)), 9),
        "link_negativity_peak": jfloat(np.max(neg_arr) if neg_log else 0.0, 12),
        "link_negativity_integral": jfloat(np.mean(np.sum(neg_arr, axis=1)) if neg_log else 0.0, 12),
        "lag_CR_minus_MC": int(peaks[1] - peaks[0]) if neg_log else 0,
        "lag_RW_minus_CR": int(peaks[2] - peaks[1]) if neg_log else 0,
        "final_energy": jfloat(state[0], 9),
        "final_toxicity": jfloat(state[1], 9),
        "final_pressure": jfloat(state[2], 9),
        "final_damage": jfloat(state[3], 9),
        "final_fatigue": jfloat(state[4], 9),
    }
    return rows, summary


def quantum_probe(arm: str, mask: str, phase: float = 0.0) -> tuple[float, float]:
    psi = np.zeros(16, dtype=complex)
    psi[0] = 1.0
    rho = np.outer(psi, psi.conj())

    for q in range(4):
        rho = apply_u(rho, single_full(rz(phase * (0.5 + 0.15 * q)), q))

    if "M" in mask:
        rho = apply_u(rho, single_full(ry(1.10), 0))
    if "C" in mask:
        rho = apply_u(rho, single_full(ry(0.95), 1))

    for q in range(4):
        rho = apply_u(rho, single_full(ry(0.12), q))

    if arm == "quantum_field_only":
        for q in range(4):
            rho = apply_u(rho, single_full(ry(0.06 * math.sin(phase)), q))
    else:
        for layer in range(4):
            for i, j in [(0, 1), (1, 2), (2, 3)]:
                theta = 0.55 + 0.10 * math.sin(phase + layer + i)
                rho = apply_u(
                    rho,
                    exp_pauli(XX[(i, j)], theta) @ exp_pauli(ZZ[(i, j)], 0.28 * math.sin(phase + i + layer)),
                )
                if arm == "quantum_dephased_control":
                    rho = dephase(rho, 0.08)
                elif arm == "measurement_feedback":
                    rho = dephase(rho, 0.14)

    w_response = p1(rho, 3)
    rw_negativity = negativity_2q(reduce_dm(rho, [2, 3]))
    return w_response, rw_negativity


def perturbation_metrics(arm: str) -> dict:
    if arm.startswith("classical"):
        return {
            "nonadditivity_index": 0.0,
            "phase_context_sensitivity": 0.0,
            "probe_observable": "classical_W_response",
        }

    if arm == "quantum_field_only":
        base_w, base_neg = quantum_probe("quantum_field_only", "", 0.0)
        m_w, m_neg = quantum_probe("quantum_field_only", "M", 0.0)
        c_w, c_neg = quantum_probe("quantum_field_only", "C", 0.0)
        mc_w, mc_neg = quantum_probe("quantum_field_only", "MC", 0.0)
        ctx = abs(quantum_probe("quantum_field_only", "M", 0.0)[0] - quantum_probe("quantum_field_only", "M", math.pi / 2)[0])
        return {
            "nonadditivity_index": jfloat(abs(mc_neg - m_neg - c_neg + base_neg), 12),
            "phase_context_sensitivity": jfloat(ctx, 12),
            "probe_observable": "R-W negativity / W response",
        }

    base_w, base_neg = quantum_probe(arm, "", 0.0)
    m_w, m_neg = quantum_probe(arm, "M", 0.0)
    c_w, c_neg = quantum_probe(arm, "C", 0.0)
    mc_w, mc_neg = quantum_probe(arm, "MC", 0.0)
    ctx = abs(quantum_probe(arm, "M", 0.0)[0] - quantum_probe(arm, "M", math.pi / 2)[0])
    return {
        "nonadditivity_index": jfloat(abs(mc_neg - m_neg - c_neg + base_neg), 12),
        "phase_context_sensitivity": jfloat(ctx, 12),
        "probe_observable": "R-W negativity / W response",
    }


def write_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260709)
    parser.add_argument("--out-json", type=Path, default=Path("data/quantum_observation/classical_vs_quantum_part_coupling_v0_seed20260709.json"))
    parser.add_argument("--summary-csv", type=Path, default=Path("data/quantum_observation/classical_vs_quantum_part_coupling_v0_seed20260709_summary.csv"))
    parser.add_argument("--trace-csv", type=Path, default=Path("data/quantum_observation/classical_vs_quantum_part_coupling_v0_seed20260709_selected_trace.csv"))
    args = parser.parse_args()

    # No stochastic sampling is used yet; seed is recorded to keep future variants stable.
    np.random.seed(args.seed)

    all_rows = []
    summaries = []
    for arm in ARMS:
        rows, summary = simulate_arm(arm)
        summary.update(perturbation_metrics(arm))
        summaries.append(summary)
        all_rows.extend(row for row in rows if row["t"] % 8 == 0)

    direct = next(s for s in summaries if s["arm"] == "quantum_direct_coupled")
    dephased = next(s for s in summaries if s["arm"] == "quantum_dephased_control")
    measurement = next(s for s in summaries if s["arm"] == "measurement_feedback")

    result = {
        "experiment": "classical_vs_quantum_part_coupling_v0",
        "date": "2026-07-09",
        "layer": "QUANTUM_OBSERVATION",
        "status": "OBSERVATION_LOG",
        "config": {
            "seed": args.seed,
            "parts": ["M_boundary", "C_conversion", "R_recycler", "W_waste"],
            "arms": ARMS,
            "steps": 96,
            "homeostasis_balance": "target_range_fraction * resource_intake_fraction * efficiency_factor",
            "quantum_model": "4-qubit density matrix with single-part drives, optional M-C/C-R/R-W entangling links, dephasing, and measurement-like feedback",
            "classical_controls": "explicit if controller and smooth nearest-neighbor coupled dynamics",
        },
        "scenario_summaries": summaries,
        "selected_trace": all_rows,
        "derived_comparisons": {
            "direct_vs_dephased_negativity_integral_ratio": jfloat(
                direct["link_negativity_integral"] / max(dephased["link_negativity_integral"], 1e-12), 6
            ),
            "direct_vs_measurement_negativity_integral_ratio": jfloat(
                direct["link_negativity_integral"] / max(measurement["link_negativity_integral"], 1e-12), 6
            ),
            "measurement_minus_direct_homeostasis_balance": jfloat(
                measurement["homeostasis_balance"] - direct["homeostasis_balance"], 9
            ),
            "measurement_minus_direct_final_fatigue": jfloat(
                measurement["final_fatigue"] - direct["final_fatigue"], 9
            ),
        },
        "observation_notes": [
            "Classical controls can create role-like behavior, but they do it by explicit rules or smooth numeric coupling and have no link negativity or phase-context response.",
            "Quantum field-only drives parts together but produces no meaningful pair negativity because no direct entangling links are applied.",
            "Quantum direct-coupled produces the strongest M-C/C-R/R-W link negativity and the strongest nonadditive link probe, but it is not the best homeostasis controller in this first parameterization.",
            "Dephasing reduces the link-negativity integral by more than an order of magnitude relative to direct coupling.",
            "Measurement feedback gives the highest homeostasis balance in this toy run, but it leaves very high final fatigue, matching the earlier measurement-cost pattern.",
            "This is an observation log. It does not establish a quantum advantage or a biological claim.",
        ],
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(summaries, args.summary_csv)
    write_csv(all_rows, args.trace_csv)
    print(json.dumps({"experiment": result["experiment"], "status": result["status"], "scenario_summaries": summaries, "derived_comparisons": result["derived_comparisons"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
