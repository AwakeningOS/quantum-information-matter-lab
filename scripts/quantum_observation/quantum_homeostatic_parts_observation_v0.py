#!/usr/bin/env python3
"""quantum_homeostatic_parts_observation_v0

Observation model for four homeostatic parts:

    M = membrane
    C = conversion / catalyst
    R = recycler
    W = waste outlet

The model keeps a 4-qubit density matrix and a small classical whole-field
(energy, toxicity, pressure).  The field modulates local rotations and, in the
direct-entangling variant, also modulates weak two-part entangling gates.

This is an observation run, not a PASS/FAIL witness test.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np


I = np.eye(2, dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)

PARTS = ["M", "C", "R", "W"]
PAIRS = [
    ("M_C", 0, 1),
    ("C_R", 1, 2),
    ("R_W", 2, 3),
    ("M_W", 0, 3),
    ("M_R", 0, 2),
    ("C_W", 1, 3),
]
VARIANTS = ["direct_entangling_parts", "field_only_parts", "constant_entangling_parts"]


def kron_all(ops):
    out = ops[0]
    for op in ops[1:]:
        out = np.kron(out, op)
    return out


def one_qubit_gate(op, q, n=4):
    return kron_all([op if i == q else I for i in range(n)])


def ry(theta):
    c = math.cos(theta / 2)
    s = math.sin(theta / 2)
    return np.array([[c, -s], [s, c]], dtype=complex)


def rz(phi):
    return np.diag([np.exp(-1j * phi / 2), np.exp(1j * phi / 2)]).astype(complex)


def two_qubit_expand(gate4, q1, q2, n=4):
    dim = 2**n
    out = np.zeros((dim, dim), dtype=complex)
    for idx in range(dim):
        bits = [(idx >> (n - 1 - i)) & 1 for i in range(n)]
        in_sub = bits[q1] * 2 + bits[q2]
        for out_sub in range(4):
            amp = gate4[out_sub, in_sub]
            if abs(amp) <= 1e-15:
                continue
            out_bits = bits.copy()
            out_bits[q1] = out_sub // 2
            out_bits[q2] = out_sub % 2
            out_idx = 0
            for bit in out_bits:
                out_idx = (out_idx << 1) | bit
            out[out_idx, idx] += amp
    return out


def partial_iswap(theta):
    c = math.cos(theta)
    s = math.sin(theta)
    gate = np.eye(4, dtype=complex)
    gate[1, 1] = c
    gate[2, 2] = c
    gate[1, 2] = -1j * s
    gate[2, 1] = -1j * s
    return gate


def zz_phase(phi):
    return np.diag([
        np.exp(-1j * phi),
        np.exp(1j * phi),
        np.exp(1j * phi),
        np.exp(-1j * phi),
    ]).astype(complex)


def partial_trace_keep(rho, keep, n=4):
    trace = [i for i in range(n) if i not in keep]
    arr = rho.reshape([2] * (2 * n))
    perm = keep + trace + [i + n for i in keep] + [i + n for i in trace]
    arr = np.transpose(arr, perm).reshape(2 ** len(keep), 2 ** len(trace), 2 ** len(keep), 2 ** len(trace))
    return np.einsum("abcb->ac", arr)


def partial_transpose_2q(rho2, sys=1):
    arr = rho2.reshape(2, 2, 2, 2)
    if sys == 1:
        arr = arr.transpose(0, 3, 2, 1)
    else:
        arr = arr.transpose(2, 1, 0, 3)
    return arr.reshape(4, 4)


def negativity_pair(rho, q1, q2):
    reduced = partial_trace_keep(rho, [q1, q2])
    pt = partial_transpose_2q(reduced, 1)
    eigs = np.linalg.eigvalsh((pt + pt.conj().T) / 2)
    return float(np.sum(np.abs(eigs[eigs < 0])))


def dephase(rho, q, p):
    gate = one_qubit_gate(Z, q)
    return (1 - p) * rho + p * (gate @ rho @ gate)


def amplitude_damp(rho, q, gamma):
    e0 = np.array([[1, 0], [0, math.sqrt(1 - gamma)]], dtype=complex)
    e1 = np.array([[0, math.sqrt(gamma)], [0, 0]], dtype=complex)
    k0 = one_qubit_gate(e0, q)
    k1 = one_qubit_gate(e1, q)
    return k0 @ rho @ k0.conj().T + k1 @ rho @ k1.conj().T


Z_OPS = [one_qubit_gate(Z, q) for q in range(4)]
N_OPS = [(np.eye(16) - Z_OPS[q]) / 2 for q in range(4)]


def run_variant(seed, steps, variant):
    plus = np.array([1, 1], dtype=complex) / math.sqrt(2)
    psi = plus
    for _ in range(3):
        psi = np.kron(psi, plus)
    rho = np.outer(psi, psi.conj())

    energy = 0.62
    toxicity = 0.18
    pressure = 0.30
    rows = []

    entangling = variant != "field_only_parts"
    constant_coupling = variant == "constant_entangling_parts"

    for t in range(steps):
        tox_drive = (
            0.10 * np.exp(-((t - 45) / 12) ** 2)
            + 0.16 * np.exp(-((t - 112) / 16) ** 2)
            + 0.04 * np.sin(2 * np.pi * t / 37)
        )
        pressure_drive = (
            0.12 * np.exp(-((t - 70) / 15) ** 2)
            + 0.18 * np.exp(-((t - 125) / 18) ** 2)
            + 0.025 * np.sin(2 * np.pi * t / 29 + 0.4)
        )
        energy_drive = 0.04 * np.sin(2 * np.pi * t / 53 + 1.1)

        activations = [float(np.real(np.trace(rho @ N_OPS[q]))) for q in range(4)]
        membrane, converter, recycler, waste = activations

        toxicity = float(np.clip(0.90 * toxicity + tox_drive + 0.045 * converter - 0.16 * waste * (1 - membrane), 0, 1))
        pressure = float(np.clip(0.88 * pressure + pressure_drive + 0.055 * toxicity + 0.04 * converter - 0.05 * recycler, 0, 1))
        energy = float(np.clip(0.92 * energy + energy_drive + 0.10 * recycler - 0.07 * toxicity - 0.035 * pressure, 0, 1))

        local_angles = [
            -0.12 + 0.45 * toxicity + 0.22 * pressure - 0.16 * energy,
            0.06 + 0.32 * toxicity + 0.20 * pressure,
            0.04 + 0.33 * energy - 0.15 * toxicity + 0.05 * pressure,
            -0.02 + 0.48 * toxicity + 0.24 * pressure - 0.07 * energy,
        ]
        local_phases = [
            0.20 * pressure,
            0.17 * toxicity,
            0.12 * energy,
            0.15 * (toxicity + pressure),
        ]

        for q in range(4):
            gate = one_qubit_gate(rz(local_phases[q]) @ ry(local_angles[q]), q)
            rho = gate @ rho @ gate.conj().T

        if entangling:
            if constant_coupling:
                theta_mc = 0.055
                theta_cr = 0.055
                theta_rw = 0.055
                phi_mw = 0.010
            else:
                theta_mc = 0.025 + 0.095 * toxicity + 0.045 * pressure
                theta_cr = 0.020 + 0.080 * pressure + 0.040 * energy
                theta_rw = 0.018 + 0.125 * pressure + 0.085 * toxicity
                phi_mw = 0.010 + 0.040 * toxicity * pressure

            for q1, q2, theta in [(0, 1, theta_mc), (1, 2, theta_cr), (2, 3, theta_rw)]:
                gate = two_qubit_expand(partial_iswap(theta), q1, q2)
                rho = gate @ rho @ gate.conj().T
            gate = two_qubit_expand(zz_phase(phi_mw), 0, 3)
            rho = gate @ rho @ gate.conj().T
        else:
            theta_mc = theta_cr = theta_rw = phi_mw = 0.0

        dephase_rate = min(0.08, 0.006 + 0.020 * toxicity + 0.010 * pressure)
        relax_rate = min(0.04, 0.002 + 0.010 * (1 - energy) + 0.004 * toxicity)

        for q in range(4):
            rho = dephase(rho, q, dephase_rate)
            rho = amplitude_damp(rho, q, relax_rate)

        rho = (rho + rho.conj().T) / 2
        rho = rho / np.trace(rho)

        activations = [float(np.real(np.trace(rho @ N_OPS[q]))) for q in range(4)]

        row = {
            "t": t,
            "variant": variant,
            "energy": round(energy, 9),
            "toxicity": round(toxicity, 9),
            "pressure": round(pressure, 9),
            "theta_MC": round(theta_mc, 9),
            "theta_CR": round(theta_cr, 9),
            "theta_RW": round(theta_rw, 9),
        }

        for q, name in enumerate(PARTS):
            row[f"act_{name}"] = round(activations[q], 9)

        for pair_name, q1, q2 in PAIRS:
            row[f"neg_{pair_name}"] = round(negativity_pair(rho, q1, q2), 12)
            zz_cov = (
                float(np.real(np.trace(rho @ (Z_OPS[q1] @ Z_OPS[q2]))))
                - float(np.real(np.trace(rho @ Z_OPS[q1])))
                * float(np.real(np.trace(rho @ Z_OPS[q2])))
            )
            row[f"zzcov_{pair_name}"] = round(zz_cov, 12)

        row["raster"] = "".join("█" if a > 0.55 else ("▒" if a > 0.40 else "·") for a in activations)
        rows.append(row)

    return rows


def summarize(rows):
    out = []
    for variant in VARIANTS:
        sub = [r for r in rows if r["variant"] == variant]
        item = {"variant": variant, "n": len(sub)}
        fields = [
            "energy", "toxicity", "pressure",
            "act_M", "act_C", "act_R", "act_W",
            "neg_M_C", "neg_C_R", "neg_R_W", "neg_M_W",
            "zzcov_M_C", "zzcov_C_R", "zzcov_R_W",
        ]
        for field in fields:
            vals = np.array([r[field] for r in sub], dtype=float)
            item[f"{field}_mean"] = round(float(vals.mean()), 9)
            item[f"{field}_max"] = round(float(vals.max()), 9)
            item[f"{field}_sd"] = round(float(vals.std()), 9)

        for pair in ["M_C", "C_R", "R_W"]:
            vals = np.array([r[f"neg_{pair}"] for r in sub], dtype=float)
            item[f"frac_neg_{pair}_gt_0_005"] = round(float(np.mean(vals > 0.005)), 9)
            for field in ["toxicity", "pressure", "energy"]:
                a = np.array([r[field] for r in sub], dtype=float)
                if a.std() > 0 and vals.std() > 0:
                    corr = float(np.corrcoef(a, vals)[0, 1])
                else:
                    corr = 0.0
                item[f"corr_{field}_neg_{pair}"] = round(corr, 9)

        out.append(item)
    return out


def write_csv(rows, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260708)
    parser.add_argument("--steps", type=int, default=180)
    parser.add_argument("--out", type=Path, default=Path("data/quantum_observation/quantum_homeostatic_parts_observation_v0_seed20260708.json"))
    parser.add_argument("--csv", type=Path, default=Path("data/quantum_observation/quantum_homeostatic_parts_observation_v0_seed20260708_trajectory.csv"))
    parser.add_argument("--summary-csv", type=Path, default=Path("data/quantum_observation/quantum_homeostatic_parts_observation_v0_seed20260708_summary.csv"))
    args = parser.parse_args()

    rows = []
    for variant in VARIANTS:
        rows.extend(run_variant(args.seed, args.steps, variant))
    summary = summarize(rows)

    sample_rows = {}
    for variant in VARIANTS:
        sample_rows[variant] = [r for r in rows if r["variant"] == variant][:12]

    result = {
        "experiment": "quantum_homeostatic_parts_observation_v0",
        "date": "2026-07-08",
        "layer": "QUANTUM_OBSERVATION",
        "status": "OBSERVATION_LOG",
        "config": {
            "seed": args.seed,
            "steps": args.steps,
            "parts": PARTS,
            "global_fields": ["energy", "toxicity", "pressure"],
            "variants": VARIANTS,
            "direct_entangling_edges": ["M-C", "C-R", "R-W"],
            "cross_phase_edge": "M-W",
            "observation_only": True,
        },
        "summary": summary,
        "sample_rows_by_variant_first_12": sample_rows,
        "observation_notes": [
            "This is an observation run, not a PASS/FAIL witness test.",
            "The direct-entangling variant uses field-modulated partial-iSWAP gates on M-C, C-R, and R-W plus a weak M-W phase thread.",
            "The field-only variant uses the same classical field feedback but no direct entangling gates.",
            "The constant-entangling variant uses direct entangling gates with fixed strength.",
            "Pair negativity and global fields are logged on the same time axis so that correlation pulses can be inspected later.",
        ],
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(rows, args.csv)
    write_csv(summary, args.summary_csv)

    print(json.dumps({
        "experiment": result["experiment"],
        "status": result["status"],
        "summary": summary,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
