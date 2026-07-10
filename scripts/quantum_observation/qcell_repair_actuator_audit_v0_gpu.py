#!/usr/bin/env python3
"""Audit candidate repair actuators before structure-maintenance experiments."""
from __future__ import annotations

import argparse
import csv
import json
import os
import time
from pathlib import Path

import torch

import qcell_local_linked_energy_machine_full2q7_final_v0 as cpu
import qcell_local_linked_energy_machine_full2q7_final_v0_gpu as eng
import qcell_fixed_circuit_output_bottleneck_map_v0_gpu as fixedmap


EXPERIMENT = "qcell_repair_actuator_audit_v0"
GRID_ID = "QFCBM_0988"
CANDIDATES = [
    "population_fixed_offdiag_restore",
    "phase_only_alignment",
    "diagonal_phase_unitary_alignment",
]
REPAIR_FRACTION = 0.25
STRUCTURE_COST_RATE = 0.35
INITIAL_STORE = 1.0
PASS_EPS = 1e-10


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


def make_cond(grid) -> cpu.Condition:
    return cpu.Condition(
        condition_id=f"{GRID_ID}_repair_audit",
        variant="ring",
        resource="R3_pure_1",
        noise="N4_dephase_plus_amplitude_damping",
        p=0.06,
        g=grid.g_internal,
        theta=grid.theta_in_RE,
        fault="none",
        schedule="constant_on",
    )


def offdiag_l1(rho, device):
    mask = torch.as_tensor(cpu.OFFDIAG_SYS, dtype=torch.bool, device=device)
    return rho.abs()[:, mask].sum(dim=1).real


def mean_negativity(rho):
    vals = []
    for i, j, _name in cpu.PAIR_SYS:
        _mi, neg = eng.pair_metrics(rho, i, j)
        vals.append(neg)
    return torch.stack(vals, dim=0).mean(dim=0)


def phase_alignment(a, b, device):
    mask = torch.as_tensor(cpu.OFFDIAG_SYS, dtype=torch.bool, device=device)
    av = a[:, mask]
    bv = b[:, mask]
    denom = (av.abs() * bv.abs()).sum(dim=1).clamp_min(1e-15)
    return ((av.conj() * bv).real.sum(dim=1) / denom).real


def diagonal_phase_unitary(pre, post):
    eval_pre, vec_pre = torch.linalg.eigh((pre + pre.mH) * 0.5)
    eval_post, vec_post = torch.linalg.eigh((post + post.mH) * 0.5)
    vp = vec_pre[:, :, -1]
    vq = vec_post[:, :, -1]
    phi = torch.angle(vp) - torch.angle(vq)
    phase = torch.exp(1j * phi)
    return phase[:, :, None] * post * phase.conj()[:, None, :]


def repair(candidate: str, pre, post):
    if candidate == "population_fixed_offdiag_restore":
        diag = torch.diag_embed(post.diagonal(dim1=-2, dim2=-1))
        off_post = post - diag
        off_pre = pre - torch.diag_embed(pre.diagonal(dim1=-2, dim2=-1))
        return diag + (1 - REPAIR_FRACTION) * off_post + REPAIR_FRACTION * off_pre
    if candidate == "phase_only_alignment":
        diag = torch.diag_embed(post.diagonal(dim1=-2, dim2=-1))
        mag = (post - diag).abs()
        phase = torch.exp(1j * torch.angle(pre))
        return diag + mag * phase
    if candidate == "diagonal_phase_unitary_alignment":
        return diagonal_phase_unitary(pre, post)
    raise RuntimeError(candidate)


def collect_pairs(grid, seeds, n_cycles, device):
    cond = make_cond(grid)
    bits = torch.as_tensor(cpu.SYS_BITS, dtype=eng.RDTYPE, device=device)
    hamming = torch.as_tensor(cpu.HAMMING_SYS, dtype=eng.RDTYPE, device=device)
    zero = eng.t(cpu.r_state("R2_pure_0"), device)
    resource = eng.t(cpu.r_state("R3_pure_1"), device)
    rho = eng.random_products(seeds, device)
    pairs = []
    for cycle in range(n_cycles):
        full = eng.full_state(rho, resource, zero)
        full = eng.apply_two_local(full, eng.exchange(grid.theta_in_RE, device), cpu.N_FULL, 0, 1)
        rho = eng.trace_full_to_sys(full)
        rho, _flows = eng.apply_internal(rho, cond, cycle, bits, device)
        pre = rho
        post, _qnoise = eng.apply_noise(pre, cond.noise, cond.p, hamming, bits, device, strong=False)
        pairs.append((cycle, pre.detach(), post.detach()))
        rho = post
    return pairs


def audit_candidate(candidate, pairs, seeds, device):
    bits = torch.as_tensor(cpu.SYS_BITS, dtype=eng.RDTYPE, device=device)
    store_before = torch.full((len(seeds),), INITIAL_STORE, dtype=eng.RDTYPE, device=device)
    rows = []
    for cycle, pre, post in pairs:
        pre = pre.to(device)
        post = post.to(device)
        after = repair(candidate, pre, post)
        structure_repaired = (offdiag_l1(after, device) - offdiag_l1(post, device)).clamp_min(0)
        phase_delta = phase_alignment(pre, after, device) - phase_alignment(pre, post, device)
        structure_cost = STRUCTURE_COST_RATE * torch.maximum(structure_repaired, phase_delta.clamp_min(0))
        store_after = store_before - structure_cost
        diag_delta = (after.diagonal(dim1=-2, dim2=-1).real - post.diagonal(dim1=-2, dim2=-1).real).abs().sum(dim=1)
        energy_delta = eng.sys_energy(after, bits) - eng.sys_energy(post, bits)
        tr = after.diagonal(dim1=-2, dim2=-1).sum(dim=1).real
        trace_error = (tr - 1).abs()
        herm_error = (after - after.mH).abs().amax(dim=(1, 2)).real
        eig = torch.linalg.eigvalsh((after + after.mH) * 0.5).real
        min_eig = eig.min(dim=1).values
        coherence_delta = offdiag_l1(after, device) - offdiag_l1(post, device)
        negativity_delta = mean_negativity(after) - mean_negativity(post)
        store_delta = store_after - store_before
        pass_mask = (
            (trace_error <= PASS_EPS)
            & (herm_error <= PASS_EPS)
            & (min_eig >= -PASS_EPS)
            & (energy_delta.abs() <= PASS_EPS)
            & (diag_delta <= PASS_EPS)
            & ((store_delta + structure_cost).abs() <= PASS_EPS)
            & ((coherence_delta > 0) | (phase_delta > 0) | (negativity_delta > 0))
        )
        host = {k: v.detach().cpu() for k, v in {
            "trace_error": trace_error,
            "hermiticity_error": herm_error,
            "min_eigenvalue": min_eig,
            "energy_delta": energy_delta,
            "diag_l1_delta": diag_delta,
            "coherence_delta": coherence_delta,
            "negativity_delta": negativity_delta,
            "phase_alignment_delta": phase_delta,
            "store_delta": store_delta,
            "structure_cost": structure_cost,
            "pass": pass_mask.to(eng.RDTYPE),
        }.items()}
        for ix, seed in enumerate(seeds):
            rows.append({
                "candidate": candidate,
                "seed": int(seed),
                "cycle": int(cycle),
                **{k: float(v[ix]) for k, v in host.items()},
            })
    return rows


def summarize(rows):
    out = []
    for candidate in CANDIDATES:
        sub = [r for r in rows if r["candidate"] == candidate]
        out.append({
            "candidate": candidate,
            "n_rows": len(sub),
            "pass_rows": sum(1 for r in sub if r["pass"] > 0.5),
            "pass_rate": sum(1 for r in sub if r["pass"] > 0.5) / len(sub),
            "max_trace_error": max(r["trace_error"] for r in sub),
            "max_hermiticity_error": max(r["hermiticity_error"] for r in sub),
            "min_eigenvalue_min": min(r["min_eigenvalue"] for r in sub),
            "max_abs_energy_delta": max(abs(r["energy_delta"]) for r in sub),
            "max_diag_l1_delta": max(r["diag_l1_delta"] for r in sub),
            "mean_coherence_delta": sum(r["coherence_delta"] for r in sub) / len(sub),
            "mean_negativity_delta": sum(r["negativity_delta"] for r in sub) / len(sub),
            "mean_phase_alignment_delta": sum(r["phase_alignment_delta"] for r in sub) / len(sub),
            "mean_structure_cost": sum(r["structure_cost"] for r in sub) / len(sub),
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=f"{EXPERIMENT}_outputs")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--n-seeds", type=int, default=60)
    ap.add_argument("--cycles", type=int, default=40)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.smoke:
        args.n_seeds = 3
        args.cycles = 5
    if args.device.startswith("cuda") and not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable")
    t0 = time.time()
    device = torch.device(args.device)
    seeds = cpu.MAIN_SEEDS[40 : 40 + args.n_seeds]
    grid = q0988_grid()
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    pairs = collect_pairs(grid, seeds, args.cycles, device)
    rows = []
    for cand in CANDIDATES:
        print(f"candidate={cand}", flush=True)
        rows.extend(audit_candidate(cand, pairs, seeds, device))
    summary = summarize(rows)
    write_csv_atomic(out / f"{EXPERIMENT}_row_summary.csv", rows)
    write_csv_atomic(out / f"{EXPERIMENT}_candidate_summary.csv", summary)
    manifest = {
        "experiment": EXPERIMENT,
        "status": "completed",
        "grid_id": GRID_ID,
        "n_seeds": len(seeds),
        "cycles": args.cycles,
        "candidates": CANDIDATES,
        "rows": len(rows),
        "wall_seconds": time.time() - t0,
        "passed_candidates": [r["candidate"] for r in summary if r["pass_rate"] == 1.0],
        "claim_ceiling": "actuator audit only; no structure-maintenance result claim",
    }
    (out / f"{EXPERIMENT}_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# Q-cell repair actuator audit v0", "", "Date: 2026-07-10 JST", "", "## Readout", ""]
    for r in summary:
        lines.append(
            f"- {r['candidate']}: pass_rate `{r['pass_rate']:.3f}`, max |dE| `{r['max_abs_energy_delta']:.3e}`, max diag delta `{r['max_diag_l1_delta']:.3e}`, mean phase delta `{r['mean_phase_alignment_delta']:.6f}`."
        )
    lines.extend(["", "## Claim Ceiling", "", manifest["claim_ceiling"], ""])
    (out / f"{EXPERIMENT}_report_2026-07-10.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
