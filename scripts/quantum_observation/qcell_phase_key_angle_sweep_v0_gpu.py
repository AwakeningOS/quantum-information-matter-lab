#!/usr/bin/env python3
"""Phase-key angle sweep for Q-cell delayed readout residual."""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import time
from pathlib import Path

import numpy as np
import torch

import qcell_local_linked_energy_machine_full2q7_final_v0 as cpu
import qcell_local_linked_energy_machine_full2q7_final_v0_gpu as eng
import qcell_fixed_circuit_output_bottleneck_map_v0_gpu as fixedmap
import qcell_local_controller_causal_test_v0_gpu as lc


EXPERIMENT = "qcell_phase_key_angle_sweep_v0"
GRID_ID = "QFCBM_0988"
PREP_CYCLES = 120
READOUT_CYCLES = 80
SOURCE_ARMS = [
    ("quantum", "ring", 0.0),
    ("classical", "classical_probability_transport", 1.0),
    ("full_dephase", "ring", 1.0),
]
KEYS = ["angle_key", "phase_shuffled_angle_key"]
ANGLE_MULTIPLIERS = [-2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0]


def write_csv_atomic(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, path)


def q0988_grid():
    for grid in fixedmap.grids():
        if grid.grid_id == GRID_ID:
            return grid
    raise RuntimeError(f"{GRID_ID} not found")


def cond_for(grid, variant: str) -> cpu.Condition:
    return cpu.Condition(GRID_ID, variant, "R3_pure_1", "N4_dephase_plus_amplitude_damping", 0.06, grid.g_internal, grid.theta_in_RE, "none", "staged")


def single_u(mat, q: int, device):
    return eng.t(cpu.embed_single(np.asarray(mat, dtype=np.complex128), cpu.N_SYS, q), device)


def ry(theta: float):
    c, s = math.cos(theta / 2), math.sin(theta / 2)
    return np.array([[c, -s], [s, c]], dtype=np.complex128)


def rz(theta: float):
    return np.array([[np.exp(-0.5j * theta), 0], [0, np.exp(0.5j * theta)]], dtype=np.complex128)


def apply_single(rho, mat, q: int, device):
    u = single_u(mat, q, device)
    return u @ rho @ u.mH


def diagonal_shadow(rho):
    out = torch.zeros_like(rho)
    idx = torch.arange(cpu.DIM_SYS, device=rho.device)
    out[:, idx, idx] = rho.diagonal(dim1=-2, dim2=-1)
    return out


def phase_shuffle(rho, seeds, device):
    phases = []
    states = torch.arange(cpu.DIM_SYS, device=device, dtype=eng.RDTYPE)
    for seed in seeds:
        gen = torch.Generator(device="cpu")
        gen.manual_seed(int(seed) + 99173)
        base = torch.as_tensor(torch.rand(cpu.N_SYS, generator=gen).numpy(), dtype=eng.RDTYPE, device=device) * (2 * math.pi)
        bits = torch.as_tensor(cpu.SYS_BITS, dtype=eng.RDTYPE, device=device)
        phases.append((bits @ base) + 0.013 * states)
    phi = torch.stack(phases).to(device)
    return rho * torch.exp(1j * (phi[:, :, None] - phi[:, None, :]))


def offdiag_l1(rho, device):
    mask = torch.as_tensor(cpu.OFFDIAG_SYS, dtype=torch.bool, device=device)
    return rho.abs()[:, mask].sum(dim=1).real


def mean_mi(rho):
    vals = []
    for i, j, _name in cpu.PAIR_SYS:
        mi, _neg = eng.pair_metrics(rho, i, j)
        vals.append(mi)
    return torch.stack(vals).mean(dim=0)


def prepare_state(grid, source: str, variant: str, dephase_strength: float, seeds: list[int], device):
    cond = cond_for(grid, variant)
    n = len(seeds)
    bits = torch.as_tensor(cpu.SYS_BITS, dtype=eng.RDTYPE, device=device)
    hamming = torch.as_tensor(cpu.HAMMING_SYS, dtype=eng.RDTYPE, device=device)
    zero = eng.t(cpu.r_state("R2_pure_0"), device)
    resource = eng.t(cpu.r_state("R3_pure_1"), device)
    rho = eng.random_products(seeds, device)
    rin = torch.zeros(n, dtype=eng.RDTYPE, device=device)
    rout = torch.zeros_like(rin)
    qnoise = torch.zeros_like(rin)
    for cycle in range(PREP_CYCLES):
        interact, _, mult = cpu.resource_for_cycle("R3_pure_1", cycle, "staged")
        if interact:
            for _ in range(mult):
                rin += 1.0
                full = eng.full_state(rho, resource, zero)
                full = eng.apply_two_local(full, eng.exchange(grid.theta_in_RE, device), cpu.N_FULL, 0, 1)
                rred = eng.trace_full_r(full)
                rho = eng.trace_full_to_sys(full)
                rout += rred[:, 1, 1].real
        rho, _flows = eng.apply_internal(rho, cond, cycle, bits, device)
        if dephase_strength > 0:
            rho = rho * ((1.0 - dephase_strength) ** hamming)
        if variant == "classical_probability_transport":
            rho = diagonal_shadow(rho)
        rho, qn = eng.apply_noise(rho, cond.noise, cond.p, hamming, bits, device, strong=False)
        qnoise += qn
    return rho, {"prep_R_in": rin, "prep_R_out": rout, "prep_Q_noise": qnoise, "prep_coherence": offdiag_l1(rho, device), "prep_MI": mean_mi(rho)}


def apply_key(rho, key: str, angle_multiplier: float, seeds: list[int], grid, device):
    cur = phase_shuffle(rho, seeds, device) if key == "phase_shuffled_angle_key" else rho
    theta = angle_multiplier * grid.g_internal
    phase = angle_multiplier * math.pi / 2
    cur = eng.apply_two_local(cur, eng.exchange(theta, device), cpu.N_SYS, 3, 4)
    cur = apply_single(cur, rz(phase), 3, device)
    cur = apply_single(cur, ry(-phase), 4, device)
    return cur


def readout_branch(grid, rho0, key: str, angle_multiplier: float, seeds: list[int], device):
    n = len(seeds)
    bits = torch.as_tensor(cpu.SYS_BITS, dtype=eng.RDTYPE, device=device)
    hamming = torch.as_tensor(cpu.HAMMING_SYS, dtype=eng.RDTYPE, device=device)
    zero = eng.t(cpu.r_state("R2_pure_0"), device)
    out_angle = torch.full((n,), grid.theta_out_DW * grid.out_layers, dtype=eng.RDTYPE, device=device)
    cond = cond_for(grid, "ring")
    rho = rho0.clone()
    w = torch.zeros(n, dtype=eng.RDTYPE, device=device)
    qnoise = torch.zeros_like(w)
    for _cycle in range(READOUT_CYCLES):
        keyed = apply_key(rho, key, angle_multiplier, seeds, grid, device)
        full = eng.full_state(keyed, zero, zero)
        full = lc.apply_two_local_batched_u(full, lc.exchange_batch(out_angle, device), cpu.N_FULL, 5, 6)
        wred = eng.trace_full_w(full)
        w += wred[:, 1, 1].real
        rho = eng.trace_full_to_sys(full)
        rho, qn = eng.apply_noise(rho, cond.noise, cond.p, hamming, bits, device, strong=False)
        qnoise += qn
    return {
        "readout_W": w,
        "readout_Q_noise": qnoise,
        "final_coherence": offdiag_l1(rho, device),
        "final_MI": mean_mi(rho),
        "final_D": eng.part_energies(rho, bits)[:, 4],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=f"{EXPERIMENT}_outputs")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--n-seeds", type=int, default=60)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.smoke:
        args.n_seeds = 3
    if args.device.startswith("cuda") and not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable")

    t0 = time.time()
    device = torch.device(args.device)
    grid = q0988_grid()
    seeds = cpu.MAIN_SEEDS[40 : 40 + args.n_seeds]
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for source, variant, dep in SOURCE_ARMS:
        print(f"source={source}", flush=True)
        rho, prep = prepare_state(grid, source, variant, dep, seeds, device)
        prep_host = {k: v.detach().cpu().numpy() for k, v in prep.items()}
        for key in KEYS:
            for angle_multiplier in ANGLE_MULTIPLIERS:
                got = readout_branch(grid, rho, key, angle_multiplier, seeds, device)
                diag_got = readout_branch(grid, diagonal_shadow(rho), key, angle_multiplier, seeds, device)
                host = {k: v.detach().cpu().numpy() for k, v in got.items()}
                diag_host = {k: v.detach().cpu().numpy() for k, v in diag_got.items()}
                for ix, seed in enumerate(seeds):
                    rows.append({
                        "source_arm": source,
                        "variant": variant,
                        "key": key,
                        "angle_multiplier": angle_multiplier,
                        "seed": int(seed),
                        "prep_R_in": float(prep_host["prep_R_in"][ix]),
                        "prep_R_out": float(prep_host["prep_R_out"][ix]),
                        "prep_Q_noise": float(prep_host["prep_Q_noise"][ix]),
                        "prep_coherence": float(prep_host["prep_coherence"][ix]),
                        "prep_MI": float(prep_host["prep_MI"][ix]),
                        "readout_W": float(host["readout_W"][ix]),
                        "diag_shadow_readout_W": float(diag_host["readout_W"][ix]),
                        "coherence_attributable_readout_W": float(host["readout_W"][ix] - diag_host["readout_W"][ix]),
                        "readout_Q_noise": float(host["readout_Q_noise"][ix]),
                        "final_coherence": float(host["final_coherence"][ix]),
                        "final_MI": float(host["final_MI"][ix]),
                        "final_D": float(host["final_D"][ix]),
                    })

    write_csv_atomic(out / f"{EXPERIMENT}_seed_summary.csv", rows)
    summary = []
    for source, _variant, _dep in SOURCE_ARMS:
        for key in KEYS:
            for angle_multiplier in ANGLE_MULTIPLIERS:
                sub = [r for r in rows if r["source_arm"] == source and r["key"] == key and r["angle_multiplier"] == angle_multiplier]
                coh_w = [r["coherence_attributable_readout_W"] for r in sub]
                summary.append({
                    "source_arm": source,
                    "key": key,
                    "angle_multiplier": angle_multiplier,
                    "n_seed": len(sub),
                    "mean_prep_coherence": sum(r["prep_coherence"] for r in sub) / len(sub),
                    "mean_prep_MI": sum(r["prep_MI"] for r in sub) / len(sub),
                    "mean_readout_W": sum(r["readout_W"] for r in sub) / len(sub),
                    "mean_diag_shadow_readout_W": sum(r["diag_shadow_readout_W"] for r in sub) / len(sub),
                    "mean_coherence_attributable_readout_W": sum(coh_w) / len(coh_w),
                    "positive_coherence_attributable_seed_count": sum(1 for g in coh_w if g > 0),
                    "mean_final_coherence": sum(r["final_coherence"] for r in sub) / len(sub),
                    "mean_final_MI": sum(r["final_MI"] for r in sub) / len(sub),
                })
    write_csv_atomic(out / f"{EXPERIMENT}_summary.csv", summary)

    manifest = {
        "experiment": EXPERIMENT,
        "status": "completed",
        "grid_id": GRID_ID,
        "n_seeds": len(seeds),
        "prep_cycles": PREP_CYCLES,
        "readout_cycles": READOUT_CYCLES,
        "source_arms": [a for a, _, _ in SOURCE_ARMS],
        "keys": KEYS,
        "angle_multipliers": ANGLE_MULTIPLIERS,
        "wall_seconds": time.time() - t0,
        "claim_ceiling": "model-level phase-key angle sweep; no quantum advantage or physical energy claim",
    }
    (out / f"{EXPERIMENT}_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# Q-cell phase-key angle sweep v0", "", "Date: 2026-07-10 JST", "", "## Summary", ""]
    for r in summary:
        lines.append(f"- {r['source_arm']} / {r['key']} / angle `{r['angle_multiplier']:.1f}`: W `{r['mean_readout_W']:.6f}`, diag W `{r['mean_diag_shadow_readout_W']:.6f}`, coherence-attributable W `{r['mean_coherence_attributable_readout_W']:.6f}`, positive coherence seeds `{r['positive_coherence_attributable_seed_count']}/{r['n_seed']}`.")
    lines += ["", "## Claim Ceiling", "", manifest["claim_ceiling"], ""]
    (out / f"{EXPERIMENT}_report_2026-07-10.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
