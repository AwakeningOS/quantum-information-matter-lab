#!/usr/bin/env python3
"""Batched CUDA runner for qcell_local_linked_energy_machine_full2q7_final_v0.

One condition is evaluated as a batch of initial states.  Each completed
condition is written atomically, so --resume can safely continue an
interrupted run.  The simulated cycle still materializes the full
R,E,A,B,C,D,W density matrix; only the implementation is batched.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import torch

import qcell_local_linked_energy_machine_full2q7_final_v0 as cpu


DTYPE = torch.complex128
RDTYPE = torch.float64
N_SYS = cpu.N_SYS
N_FULL = cpu.N_FULL
DIM_SYS = cpu.DIM_SYS
CHECKPOINTS = set(cpu.CHECKPOINTS)
BASE = "qcell_local_linked_energy_machine_full2q7_final_v0"


def t(x, device):
    return torch.as_tensor(x, dtype=DTYPE, device=device)


def apply_two_local(rho, u2, n, q1, q2):
    """Batched two-qubit unitary without a dense 2^n gate."""
    keep = [q1, q2]
    rest = [q for q in range(n) if q not in keep]
    axes = [0] + [1 + q for q in keep + rest]
    axes += [1 + n + q for q in keep + rest]
    inverse = np.argsort(axes)
    batch = rho.shape[0]
    drest = 2 ** (n - 2)
    x = rho.reshape([batch] + [2] * (2 * n)).permute(axes)
    x = x.reshape(batch, 4, drest, 4, drest)
    y = torch.einsum("ai,nirjs,bj->narbs", u2, x, u2.conj())
    y = y.reshape([batch] + [2] * (2 * n)).permute(tuple(inverse))
    return y.reshape(batch, 2**n, 2**n)


def full_state(rsys, rr, rw):
    return torch.einsum("ab,nij,cd->naicbjd", rr, rsys, rw).reshape(
        rsys.shape[0], 2**N_FULL, 2**N_FULL
    )


def trace_full_to_sys(rfull):
    x = rfull.reshape(rfull.shape[0], 2, DIM_SYS, 2, 2, DIM_SYS, 2)
    return torch.einsum("naicajc->nij", x)


def trace_full_r(rfull):
    x = rfull.reshape(rfull.shape[0], 2, DIM_SYS, 2, 2, DIM_SYS, 2)
    return torch.einsum("naicbic->nab", x)


def trace_full_w(rfull):
    x = rfull.reshape(rfull.shape[0], 2, DIM_SYS, 2, 2, DIM_SYS, 2)
    return torch.einsum("naicaid->ncd", x)


def reduced_pair(rho, i, j):
    keep = [i, j]
    rest = [q for q in range(N_SYS) if q not in keep]
    axes = [0] + [1 + q for q in keep + rest]
    axes += [1 + N_SYS + q for q in keep + rest]
    x = rho.reshape([rho.shape[0]] + [2] * (2 * N_SYS)).permute(axes)
    x = x.reshape(rho.shape[0], 4, 8, 4, 8)
    return torch.einsum("narbr->nab", x)


def entropy_batch(rho, base2=True):
    vals = torch.linalg.eigvalsh((rho + rho.mH) * 0.5).real.clamp_min(0)
    logs = torch.where(vals > 1e-14, torch.log2(vals) if base2 else torch.log(vals), 0)
    return -(vals * logs).sum(dim=-1)


def trace_distance_batch(a, b):
    vals = torch.linalg.eigvalsh((a - b + (a - b).mH) * 0.5).real
    return 0.5 * vals.abs().sum(dim=-1)


def pair_metrics(rho, i, j):
    red = reduced_pair(rho, i, j)
    x = red.reshape(rho.shape[0], 2, 2, 2, 2)
    ri = torch.einsum("naib i->nab", x)
    rj = torch.einsum("naia j->nij", x)
    mi = entropy_batch(ri) + entropy_batch(rj) - entropy_batch(red)
    pt = x.permute(0, 1, 4, 3, 2).reshape(rho.shape[0], 4, 4)
    ev = torch.linalg.eigvalsh((pt + pt.mH) * 0.5).real
    neg = (-ev.clamp_max(0)).sum(dim=-1)
    return mi, neg


def random_products(seeds, device):
    return t(np.stack([cpu.random_product(s) for s in seeds]), device)


def exchange(theta, device):
    return t(cpu.exchange2(theta), device)


def sys_energy(rho, bits):
    return rho.diagonal(dim1=-2, dim2=-1).real @ bits.sum(dim=1)


def part_energies(rho, bits):
    return rho.diagonal(dim1=-2, dim2=-1).real @ bits


def apply_kraus_local(rho, kraus, q, device):
    out = torch.zeros_like(rho)
    for k in kraus:
        km = t(cpu.embed_single(k, N_SYS, q), device)
        out += km @ rho @ km.mH
    return out


def apply_noise(rho, noise, p, hamming, bits, device, strong=False):
    before = sys_energy(rho, bits)
    out = rho
    if noise in ("N1_dephase", "N4_dephase_plus_amplitude_damping"):
        out = out * ((1 - p) ** hamming)
    if noise in ("N3_amplitude_damping", "N4_dephase_plus_amplitude_damping"):
        k0 = np.array([[1, 0], [0, math.sqrt(1-p)]], np.complex128)
        k1 = np.array([[0, math.sqrt(p)], [0, 0]], np.complex128)
        for q in range(N_SYS):
            out = apply_kraus_local(out, (k0, k1), q, device)
    if strong:
        out = out * (0.0 ** hamming)
    return out, before - sys_energy(out, bits)


def classical_transport(rho, cond, cycle, bits):
    diag = rho.diagonal(dim1=-2, dim2=-1).real.clone()
    alpha = min(0.49, 4 * cond.g * cond.g)
    for a, b, _, _ in cpu.links(cond, cycle):
        swapped = torch.arange(DIM_SYS, device=rho.device)
        ba = bits[:, a].long()
        bb = bits[:, b].long()
        swapped = swapped ^ ((ba ^ bb) << (N_SYS - 1 - a))
        swapped = swapped ^ ((ba ^ bb) << (N_SYS - 1 - b))
        diag = (1 - alpha) * diag + alpha * diag[:, swapped]
    out = torch.zeros_like(rho)
    idx = torch.arange(DIM_SYS, device=rho.device)
    out[:, idx, idx] = diag.to(rho.dtype)
    return out


def apply_internal(rho, cond, cycle, bits, device):
    flows = {}
    if cond.variant == "classical_probability_transport":
        return classical_transport(rho, cond, cycle, bits), flows
    cur = rho
    for a, b, angle, name in cpu.links(cond, cycle):
        before = part_energies(cur, bits)
        cur = apply_two_local(cur, exchange(angle, device), N_SYS, a, b)
        after = part_energies(cur, bits)
        flows[f"flow_{name}"] = flows.get(f"flow_{name}", 0) + after[:, b] - before[:, b]
    if cond.variant == "central_control":
        before = part_energies(cur, bits)
        cur = apply_two_local(cur, exchange(cond.g * 2, device), N_SYS, 0, 4)
        after = part_energies(cur, bits)
        flows["flow_ED_direct_upper_bound"] = after[:, 4] - before[:, 4]
    return cur, flows


def apply_fault(rho, fault, bits, device):
    if fault in ("none", "cut_BC", "weaken_AB", "close_DW"):
        return rho, torch.zeros(rho.shape[0], dtype=RDTYPE, device=device)
    before = sys_energy(rho, bits)
    if fault in ("remove_A_excitation", "empty_E"):
        q = 1 if fault == "remove_A_excitation" else 0
        ks = (
            np.array([[1, 0], [0, 0]], np.complex128),
            np.array([[0, 1], [0, 0]], np.complex128),
        )
    elif fault == "overexcite_C":
        q = 3
        ks = (
            np.array([[0, 0], [0, 1]], np.complex128),
            np.array([[0, 0], [1, 0]], np.complex128),
        )
    else:
        raise ValueError(fault)
    out = apply_kraus_local(rho, ks, q, device)
    return out, sys_energy(out, bits) - before


def batch_metrics(rho, cond, seeds, cycle, prev, bits, maxmix):
    n = rho.shape[0]
    diag = rho.diagonal(dim1=-2, dim2=-1).real
    parts = diag @ bits
    vals = {
        "E_internal": diag @ bits.sum(dim=1),
        "purity": torch.einsum("nij,nji->n", rho, rho).real,
        "entropy": entropy_batch(rho),
        "l1_coherence": rho.abs().sum(dim=(1,2)) - diag.abs().sum(dim=1),
        "trace_distance_to_maxmixed": trace_distance_batch(rho, maxmix),
    }
    vals["prev_cycle_trace_distance"] = (
        trace_distance_batch(rho, prev) if prev is not None else None
    )
    for k, name in enumerate(cpu.SYS_NAMES):
        vals[f"E_{name}"] = parts[:, k]
    for k in range(DIM_SYS):
        vals[f"pop_{k:05b}"] = diag[:, k]
    for i, j, name in cpu.PAIR_SYS:
        z = (1 - 2*bits[:, i]) * (1 - 2*bits[:, j])
        vals[f"ZZ_{name}"] = diag @ z
        mi, neg = pair_metrics(rho, i, j)
        vals[f"MI_{name}"] = mi
        vals[f"negativity_{name}"] = neg
    host = {k: (None if v is None else v.detach().cpu().numpy()) for k, v in vals.items()}
    rows = []
    fixed = dict(
        condition_id=cond.condition_id, variant=cond.variant, resource=cond.resource,
        noise=cond.noise, p=cond.p, g=cond.g, theta=cond.theta, fault=cond.fault,
    )
    for ix, seed in enumerate(seeds):
        row = dict(fixed, seed=seed, cycle=cycle)
        for key, arr in host.items():
            row[key] = "" if arr is None else float(arr[ix])
        rows.append(row)
    return rows


def write_csv(path, rows):
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, path)


def run_condition(cond, seeds, device, part_dir, save_states):
    bits = torch.as_tensor(cpu.SYS_BITS, dtype=RDTYPE, device=device)
    hamming = torch.as_tensor(cpu.HAMMING_SYS, dtype=RDTYPE, device=device)
    maxmix = torch.eye(DIM_SYS, dtype=DTYPE, device=device) / DIM_SYS
    zero = t(cpu.r_state("R2_pure_0"), device)
    rho = random_products(seeds, device)
    metrics, ledger, flows, states = [], [], [], {}
    metrics += batch_metrics(rho, cond, seeds, 0, None, bits, maxmix)
    if save_states:
        states["cycle000"] = rho.detach().cpu().numpy().astype(np.complex64)

    for cycle in range(200):
        prev = rho.clone()
        estart = sys_energy(rho, bits)
        wext = torch.zeros(len(seeds), dtype=RDTYPE, device=device)
        if cycle == 100:
            rho, wext = apply_fault(rho, cond.fault, bits, device)
        interact, rs_np, mult = cpu.resource_for_cycle(cond.resource, cycle, cond.schedule)
        if cond.variant == "converter_off":
            interact = False
        rin = torch.zeros_like(wext)
        rout = torch.zeros_like(wext)
        fcons = torch.zeros_like(wext)
        sent = torch.zeros_like(wext)
        if interact:
            rs = t(rs_np, device)
            fin = cpu.free_energy_beta1(rs_np)
            for _ in range(mult):
                rin += cpu.single_energy(rs_np)
                full = full_state(rho, rs, zero)
                full = apply_two_local(full, exchange(cond.theta, device), N_FULL, 0, 1)
                rred = trace_full_r(full)
                rho = trace_full_to_sys(full)
                rout += rred[:, 1, 1].real
                fcons += fin - (rred[:,1,1].real - entropy_batch(rred, base2=False))
                sent += entropy_batch(rred)

        rho, linkflow = apply_internal(rho, cond, cycle, bits, device)
        wout = torch.zeros_like(wext)
        open_output = cond.variant != "output_off"
        if cond.fault == "close_DW" and 100 <= cycle < 120:
            open_output = False
        if open_output:
            full = full_state(rho, zero, zero)
            full = apply_two_local(full, exchange(cond.theta, device), N_FULL, 5, 6)
            wred = trace_full_w(full)
            wout = wred[:, 1, 1].real
            rho = trace_full_to_sys(full)

        rho, qnoise = apply_noise(
            rho, cond.noise, cond.p, hamming, bits, device,
            strong=cond.variant in ("strong_dephase", "classical_probability_transport"),
        )
        dend = sys_energy(rho, bits)
        de = dend - estart
        residual = rin + wext - (de + rout + wout + qnoise)
        host = {
            "E_R_in": rin, "E_R_out": rout, "Delta_E_Qcell": de,
            "E_W_out": wout, "Q_noise": qnoise, "W_external": wext,
            "energy_balance_residual": residual,
            "resource_free_energy_consumed": fcons,
            "entropy_exported_to_R": sent, "E_internal_start": estart,
            "E_internal_end": dend,
        }
        host = {k: v.detach().cpu().numpy() for k, v in host.items()}
        flow_host = {k: v.detach().cpu().numpy() for k, v in linkflow.items()}
        fixed = dict(
            condition_id=cond.condition_id, variant=cond.variant, resource=cond.resource,
            noise=cond.noise, p=cond.p, g=cond.g, theta=cond.theta, fault=cond.fault,
        )
        for ix, seed in enumerate(seeds):
            ledger.append(dict(fixed, seed=seed, cycle=cycle+1,
                               **{k: float(v[ix]) for k,v in host.items()}))
            fr = dict(fixed, seed=seed, cycle=cycle+1,
                      R_in_energy=float(host["E_R_in"][ix]),
                      R_spent_energy=float(host["E_R_out"][ix]),
                      W_out_energy=float(host["E_W_out"][ix]))
            fr.update({k: float(v[ix]) for k,v in flow_host.items()})
            flows.append(fr)
        metrics += batch_metrics(rho, cond, seeds, cycle+1, prev, bits, maxmix)
        if save_states and cycle + 1 in CHECKPOINTS:
            states[f"cycle{cycle+1:03d}"] = rho.detach().cpu().numpy().astype(np.complex64)

        if not torch.isfinite(rho).all():
            raise RuntimeError(f"non-finite density: {cond.condition_id} cycle {cycle+1}")
        tr = rho.diagonal(dim1=-2,dim2=-1).sum(-1).real
        if torch.max(torch.abs(tr - 1)).item() > 1e-7:
            raise RuntimeError(f"trace drift: {cond.condition_id} cycle {cycle+1}")

    prefix = part_dir / cond.condition_id
    write_csv(prefix.with_name(prefix.name + "_metrics.csv"), metrics)
    write_csv(prefix.with_name(prefix.name + "_ledger.csv"), ledger)
    write_csv(prefix.with_name(prefix.name + "_flows.csv"), flows)
    if states:
        tmp = prefix.with_name(prefix.name + "_states.tmp.npz")
        final = prefix.with_name(prefix.name + "_states.npz")
        np.savez_compressed(tmp, **states)
        os.replace(tmp, final)
    marker = prefix.with_name(prefix.name + "_complete.json")
    tmp = marker.with_suffix(".tmp")
    tmp.write_text(json.dumps({
        "condition": asdict(cond), "n_seeds": len(seeds),
        "metric_rows": len(metrics), "ledger_rows": len(ledger),
        "flow_rows": len(flows), "checkpoint_cycles": sorted(CHECKPOINTS) if save_states else [],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, marker)
    return len(metrics), len(ledger), len(flows), len(states)


def concatenate_csv(inputs, output):
    if not inputs:
        return
    fieldnames = []
    for path in inputs:
        with path.open(newline="", encoding="utf-8") as f:
            row = next(csv.reader(f), [])
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    tmp = output.with_suffix(output.suffix + ".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=fieldnames)
        writer.writeheader()
        for path in inputs:
            with path.open(newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    writer.writerow(row)
    os.replace(tmp, output)


def merge_parts(out, conds):
    part_dir = out / "parts"
    concatenate_csv(
        [part_dir / f"{c.condition_id}_metrics.csv" for c in conds],
        out / f"{BASE}_cyclewise_state_metrics.csv",
    )
    concatenate_csv(
        [part_dir / f"{c.condition_id}_ledger.csv" for c in conds],
        out / f"{BASE}_thermodynamic_ledger.csv",
    )
    concatenate_csv(
        [part_dir / f"{c.condition_id}_flows.csv" for c in conds],
        out / f"{BASE}_linkwise_energy_flow.csv",
    )
    state_files = [part_dir / f"{c.condition_id}_states.npz" for c in conds
                   if (part_dir / f"{c.condition_id}_states.npz").exists()]
    index = {"format": "per-condition NPZ", "files": [str(p.relative_to(out)) for p in state_files]}
    (out / f"{BASE}_checkpoint_density_matrices_index.json").write_text(
        json.dumps(index, indent=2), encoding="utf-8"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=f"{BASE}_outputs_gpu")
    ap.add_argument("--profile", choices=("smoke", "final"), default="final")
    ap.add_argument("--n-seeds", type=int, default=100)
    ap.add_argument("--max-conditions", type=int, default=0)
    ap.add_argument("--condition-start", type=int, default=0)
    ap.add_argument("--condition-end", type=int, default=0)
    ap.add_argument("--shard-index", type=int, default=0)
    ap.add_argument("--shard-count", type=int, default=1)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--no-merge", action="store_true")
    ap.add_argument("--device", default="cuda")
    args = ap.parse_args()

    if args.device.startswith("cuda") and not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable")
    device = torch.device(args.device)
    out = Path(args.outdir)
    part_dir = out / "parts"
    part_dir.mkdir(parents=True, exist_ok=True)
    conds = cpu.conditions(args.profile)
    if args.max_conditions:
        conds = conds[:args.max_conditions]
    end = args.condition_end or len(conds)
    conds = conds[args.condition_start:end]
    conds = [c for i,c in enumerate(conds) if i % args.shard_count == args.shard_index]
    seeds = cpu.MAIN_SEEDS[:args.n_seeds]
    save_ids = {
        c.condition_id for c in conds
        if c.resource in ("R3_pure_1","R4_plus","R1_max_mixed")
        and c.variant in ("ring","chain","middle_cut","coupling_off","converter_off")
    }
    t0 = time.time()
    totals = [0,0,0,0]
    completed = 0
    for index, cond in enumerate(conds, 1):
        marker = part_dir / f"{cond.condition_id}_complete.json"
        if args.resume and marker.exists():
            print(f"skip {cond.condition_id} ({index}/{len(conds)})", flush=True)
            completed += 1
            continue
        c0 = time.time()
        result = run_condition(cond, seeds, device, part_dir, cond.condition_id in save_ids)
        totals = [a+b for a,b in zip(totals, result)]
        completed += 1
        print(f"completed {cond.condition_id} {index}/{len(conds)} "
              f"condition_seconds={time.time()-c0:.2f} total_seconds={time.time()-t0:.2f}",
              flush=True)
    if not args.no_merge and completed == len(conds):
        merge_parts(out, conds)
    manifest = {
        "experiment": BASE, "runner": "batched_cuda", "device": str(device),
        "gpu": torch.cuda.get_device_name(device) if device.type == "cuda" else "",
        "n_conditions": len(conds), "n_seeds": len(seeds), "cycles": 200,
        "completed_conditions": completed, "new_rows": {
            "metrics": totals[0], "ledger": totals[1], "flows": totals[2],
            "checkpoint_arrays": totals[3],
        },
        "wall_seconds": time.time()-t0, "resume_supported": True,
        "shard": {"index": args.shard_index, "count": args.shard_count},
    }
    (out / f"{BASE}_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
