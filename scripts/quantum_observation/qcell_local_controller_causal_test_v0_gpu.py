#!/usr/bin/env python3
"""Pilot GPU runner for qcell_local_controller_causal_test_v0.

This runner intentionally stays small:

- selected Stage-2 grid IDs only
- compact per-seed summaries
- no full cyclewise raw logs by default
- raw outputs should live outside the repository

The physical primitives are reused from the full 2^7 CUDA implementation.
The new code only changes how local/internal or outlet actions are selected.
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
import qcell_local_linked_energy_machine_full2q7_final_v0_gpu as eng
import qcell_fixed_circuit_output_bottleneck_map_v0_gpu as fixedmap


EXPERIMENT = "qcell_local_controller_causal_test_v0"
SHIFT = 37
VARIANTS = [
    "fixed_local_resource",
    "fixed_local_no_resource",
    "internal_controller_resource",
    "internal_controller_no_resource",
    "internal_shuffled_signal_resource",
    "internal_shuffled_signal_no_resource",
    "internal_time_shift_action_resource",
    "internal_time_shift_action_no_resource",
    "output_controller_resource",
    "output_controller_no_resource",
    "output_shuffled_signal_resource",
    "output_shuffled_signal_no_resource",
    "output_time_shift_action_resource",
    "output_time_shift_action_no_resource",
    "matched_central_resource",
    "matched_central_no_resource",
]


def read_grid_ids(path):
    return fixedmap.read_grid_ids_file(path)


def selected_grids(path):
    ids = read_grid_ids(path)
    by_id = {g.grid_id: g for g in fixedmap.grids()}
    missing = [x for x in ids if x not in by_id]
    if missing:
        raise SystemExit(f"unknown grid IDs: {missing}")
    return [by_id[x] for x in ids]


def write_csv_atomic(path, rows):
    if not rows:
        return
    fields = []
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


def exchange_batch(theta, device):
    """Batched 2-qubit exchange matrices for per-seed control angles."""
    theta = theta.to(dtype=eng.RDTYPE, device=device)
    n = theta.shape[0]
    u = torch.zeros((n, 4, 4), dtype=eng.DTYPE, device=device)
    idx = torch.arange(4, device=device)
    u[:, idx, idx] = 1
    c = torch.cos(theta).to(eng.DTYPE)
    s = torch.sin(theta).to(eng.DTYPE)
    u[:, 1, 1] = c
    u[:, 2, 2] = c
    u[:, 1, 2] = -1j * s
    u[:, 2, 1] = -1j * s
    return u


def apply_two_local_batched_u(rho, u2, n, q1, q2):
    """Apply one two-qubit unitary per batch item."""
    keep = [q1, q2]
    rest = [q for q in range(n) if q not in keep]
    axes = [0] + [1 + q for q in keep + rest]
    axes += [1 + n + q for q in keep + rest]
    inverse = np.argsort(axes)
    batch = rho.shape[0]
    drest = 2 ** (n - 2)
    x = rho.reshape([batch] + [2] * (2 * n)).permute(axes)
    x = x.reshape(batch, 4, drest, 4, drest)
    y = torch.einsum("nai,nirjs,nbj->narbs", u2, x, u2.conj())
    y = y.reshape([batch] + [2] * (2 * n)).permute(tuple(inverse))
    return y.reshape(batch, 2**n, 2**n)


def has_resource(variant):
    return variant.endswith("_resource") and "no_resource" not in variant


def controller_family(variant):
    if variant.startswith("fixed_local"):
        return "fixed"
    if variant.startswith("internal_controller"):
        return "internal"
    if variant.startswith("internal_shuffled_signal"):
        return "internal_shuffled_signal"
    if variant.startswith("internal_time_shift_action"):
        return "internal_time_shift"
    if variant.startswith("output_controller"):
        return "output"
    if variant.startswith("output_shuffled_signal"):
        return "output_shuffled_signal"
    if variant.startswith("output_time_shift_action"):
        return "output_time_shift"
    if variant.startswith("matched_central"):
        return "central"
    raise ValueError(variant)


def links_for_grid(grid):
    links = [(0, 1, "EA"), (1, 2, "AB"), (2, 3, "BC"), (3, 4, "CD")]
    if grid.structure == "ring":
        links.append((1, 4, "AD"))
    return links


def derangement(n, device):
    return torch.roll(torch.arange(n, device=device), shifts=1)


def internal_angles_from_parts(parts, grid, signal_parts=None):
    """Budgeted local-gradient internal policy.

    Returns [batch, n_links] angles.  Sum per seed is <= fixed budget.
    """
    src = parts if signal_parts is None else signal_parts
    links = links_for_grid(grid)
    weights = []
    for a, b, name in links:
        if name == "AD":
            w = torch.relu(src[:, a] - src[:, b]) * (src[:, b] < 0.5).to(src.dtype)
        else:
            w = torch.relu(src[:, a] - src[:, b])
        weights.append(w)
    W = torch.stack(weights, dim=1)
    budget = grid.g_internal * len(links)
    denom = W.sum(dim=1, keepdim=True)
    fixed = torch.full_like(W, grid.g_internal)
    dyn = torch.where(denom > 1e-12, W / denom.clamp_min(1e-12) * budget, fixed)
    max_angle = min(2.0 * grid.g_internal, 0.8)
    dyn = dyn.clamp_max(max_angle)
    return dyn


def output_angle_from_parts(parts, grid, signal_parts=None):
    """Budgeted D-gated outlet policy.

    Uses only D population.  The total angle per active cycle is not higher than
    the fixed effective outlet angle.
    """
    src = parts if signal_parts is None else signal_parts
    effective = grid.theta_out_DW * grid.out_layers
    d = src[:, 4]
    threshold = 0.25
    return torch.where(d > threshold, torch.full_like(d, effective), torch.zeros_like(d))


def precompute_action_sequences(grid, seeds, device, family):
    """Run the unshuffled controller once to get action sequences only."""
    bits = torch.as_tensor(cpu.SYS_BITS, dtype=eng.RDTYPE, device=device)
    hamming = torch.as_tensor(cpu.HAMMING_SYS, dtype=eng.RDTYPE, device=device)
    zero = eng.t(cpu.r_state("R2_pure_0"), device)
    resource = eng.t(cpu.r_state("R3_pure_1"), device)
    rho = eng.random_products(seeds, device)
    n = len(seeds)
    internal_seq = []
    output_seq = []
    links = links_for_grid(grid)
    for cycle in range(200):
        interact, _, mult = cpu.resource_for_cycle("R3_pure_1", cycle, "staged")
        if interact:
            for _ in range(mult):
                full = eng.full_state(rho, resource, zero)
                full = eng.apply_two_local(full, eng.exchange(grid.theta_in_RE, device), cpu.N_FULL, 0, 1)
                rho = eng.trace_full_to_sys(full)
        parts = eng.part_energies(rho, bits)
        if family == "internal":
            angles = internal_angles_from_parts(parts, grid)
            internal_seq.append(angles.detach())
            for col, (a, b, _) in enumerate(links):
                rho = apply_two_local_batched_u(rho, exchange_batch(angles[:, col], device), cpu.N_SYS, a, b)
            out_angle = torch.full((n,), grid.theta_out_DW * grid.out_layers, dtype=eng.RDTYPE, device=device)
        elif family == "output":
            fixed_angle = torch.full((n,), grid.g_internal, dtype=eng.RDTYPE, device=device)
            for a, b, _ in links:
                rho = apply_two_local_batched_u(rho, exchange_batch(fixed_angle, device), cpu.N_SYS, a, b)
            out_angle = output_angle_from_parts(parts, grid)
            output_seq.append(out_angle.detach())
        else:
            raise ValueError(family)
        full = eng.full_state(rho, zero, zero)
        full = apply_two_local_batched_u(full, exchange_batch(out_angle, device), cpu.N_FULL, 5, 6)
        rho = eng.trace_full_to_sys(full)
        rho, _ = eng.apply_noise(rho, "N4_dephase_plus_amplitude_damping", 0.06, hamming, bits, device, strong=False)
    return internal_seq, output_seq


def run_variant(grid, variant, seeds, device, precomputed):
    family = controller_family(variant)
    n = len(seeds)
    bits = torch.as_tensor(cpu.SYS_BITS, dtype=eng.RDTYPE, device=device)
    hamming = torch.as_tensor(cpu.HAMMING_SYS, dtype=eng.RDTYPE, device=device)
    zero = eng.t(cpu.r_state("R2_pure_0"), device)
    resource = eng.t(cpu.r_state("R3_pure_1"), device)
    rho = eng.random_products(seeds, device)
    initial_energy = eng.sys_energy(rho, bits)
    links = links_for_grid(grid)
    perm = derangement(n, device)
    fixed_internal_budget = grid.g_internal * len(links) * 200
    fixed_output_budget = grid.theta_out_DW * grid.out_layers * 200
    cumulative = {k: torch.zeros(n, dtype=eng.RDTYPE, device=device)
                  for k in ("rin", "rout", "wout", "qnoise", "fcons", "dflow")}
    residence = torch.zeros((n, cpu.N_SYS), dtype=eng.RDTYPE, device=device)
    d_sum = torch.zeros(n, dtype=eng.RDTYPE, device=device)
    d_peak = torch.zeros(n, dtype=eng.RDTYPE, device=device)
    max_res = torch.zeros(n, dtype=eng.RDTYPE, device=device)
    action_count = torch.zeros(n, dtype=eng.RDTYPE, device=device)
    internal_action_count = torch.zeros_like(action_count)
    output_action_count = torch.zeros_like(action_count)
    total_angle_budget = torch.zeros_like(action_count)
    internal_angle_budget = torch.zeros_like(action_count)
    output_angle_budget = torch.zeros_like(action_count)
    per_link_budget = {name: torch.zeros(n, dtype=eng.RDTYPE, device=device) for _, _, name in links}
    per_link_count = {name: torch.zeros(n, dtype=eng.RDTYPE, device=device) for _, _, name in links}
    max_link_angle = torch.zeros(n, dtype=eng.RDTYPE, device=device)
    central = family == "central"

    for cycle in range(200):
        start_energy = eng.sys_energy(rho, bits)
        interact, _, mult = cpu.resource_for_cycle("R3_pure_1", cycle, "staged")
        if not has_resource(variant):
            interact, mult = False, 0
        rin = torch.zeros(n, dtype=eng.RDTYPE, device=device)
        rout = torch.zeros_like(rin)
        fcons = torch.zeros_like(rin)
        if interact:
            for _ in range(mult):
                rin += 1.0
                full = eng.full_state(rho, resource, zero)
                full = eng.apply_two_local(full, eng.exchange(grid.theta_in_RE, device), cpu.N_FULL, 0, 1)
                rred = eng.trace_full_r(full)
                rho = eng.trace_full_to_sys(full)
                rout += rred[:, 1, 1].real
                fcons += 1.0 - (rred[:, 1, 1].real - eng.entropy_batch(rred, base2=False))

        parts_before = eng.part_energies(rho, bits)
        signal = parts_before[perm] if "shuffled_signal" in family else parts_before
        if family in ("fixed", "output", "output_shuffled_signal", "output_time_shift", "central"):
            internal_angles = torch.full((n, len(links)), grid.g_internal, dtype=eng.RDTYPE, device=device)
        elif family in ("internal", "internal_shuffled_signal"):
            internal_angles = internal_angles_from_parts(parts_before, grid, signal)
        elif family == "internal_time_shift":
            seq = precomputed["internal"]
            internal_angles = seq[(cycle + SHIFT) % 200]
        else:
            raise ValueError(family)

        for col, (a, b, name) in enumerate(links):
            angle = internal_angles[:, col]
            before = eng.part_energies(rho, bits)
            rho = apply_two_local_batched_u(rho, exchange_batch(angle, device), cpu.N_SYS, a, b)
            after = eng.part_energies(rho, bits)
            per_link_budget[name] += angle.abs()
            per_link_count[name] += (angle.abs() > 1e-12).to(eng.RDTYPE)
            internal_angle_budget += angle.abs()
            internal_action_count += (angle.abs() > 1e-12).to(eng.RDTYPE)
            max_link_angle = torch.maximum(max_link_angle, angle.abs())
            cumulative["dflow"] += torch.zeros_like(rin)

        if central:
            rho = eng.apply_two_local(rho, eng.exchange(grid.g_internal * 2.0, device), cpu.N_SYS, 0, 4)

        parts_after_internal = eng.part_energies(rho, bits)
        if family in ("fixed", "internal", "internal_shuffled_signal", "internal_time_shift", "central"):
            out_angle = torch.full((n,), grid.theta_out_DW * grid.out_layers, dtype=eng.RDTYPE, device=device)
        elif family in ("output", "output_shuffled_signal"):
            out_signal = parts_after_internal[perm] if family == "output_shuffled_signal" else parts_after_internal
            out_angle = output_angle_from_parts(parts_after_internal, grid, out_signal)
        elif family == "output_time_shift":
            seq = precomputed["output"]
            out_angle = seq[(cycle + SHIFT) % 200]
        else:
            raise ValueError(family)
        full = eng.full_state(rho, zero, zero)
        full = apply_two_local_batched_u(full, exchange_batch(out_angle, device), cpu.N_FULL, 5, 6)
        wred = eng.trace_full_w(full)
        wout = wred[:, 1, 1].real
        rho = eng.trace_full_to_sys(full)
        output_angle_budget += out_angle.abs()
        output_action_count += (out_angle.abs() > 1e-12).to(eng.RDTYPE)
        action_count = internal_action_count + output_action_count
        total_angle_budget = internal_angle_budget + output_angle_budget

        rho, qnoise = eng.apply_noise(rho, "N4_dephase_plus_amplitude_damping", 0.06, hamming, bits, device, strong=False)
        end_energy = eng.sys_energy(rho, bits)
        residual = rin - ((end_energy - start_energy) + rout + wout + qnoise)
        max_res = torch.maximum(max_res, residual.abs())
        parts = eng.part_energies(rho, bits)
        residence += parts
        d = parts[:, 4]
        d_sum += d
        d_peak = torch.maximum(d_peak, d)
        for key, value in (("rin", rin), ("rout", rout), ("wout", wout), ("qnoise", qnoise), ("fcons", fcons)):
            cumulative[key] += value

        if not torch.isfinite(rho).all():
            raise RuntimeError(f"non-finite state {grid.grid_id} {variant} cycle={cycle+1}")
        tr = rho.diagonal(dim1=-2, dim2=-1).sum(-1).real
        if torch.max(torch.abs(tr - 1)).item() > 1e-7:
            raise RuntimeError(f"trace drift {grid.grid_id} {variant} cycle={cycle+1}")

    final_energy = eng.sys_energy(rho, bits)
    host = {
        "initial_energy": initial_energy, "final_energy": final_energy,
        "d_mean": d_sum / 200, "d_peak": d_peak, "max_res": max_res,
        "action_count": action_count,
        "internal_action_count": internal_action_count,
        "output_action_count": output_action_count,
        "total_angle_budget": total_angle_budget,
        "internal_angle_budget": internal_angle_budget,
        "output_angle_budget": output_angle_budget,
        "max_link_angle": max_link_angle,
    }
    for k, v in cumulative.items():
        host[k] = v
    for idx, name in enumerate(cpu.SYS_NAMES):
        host[f"residence_{name}"] = residence[:, idx]
    for name in per_link_budget:
        host[f"angle_budget_{name}"] = per_link_budget[name]
        host[f"action_count_{name}"] = per_link_count[name]
    host = {k: v.detach().cpu().numpy() for k, v in host.items()}

    rows = []
    for ix, seed in enumerate(seeds):
        row = {
            "grid_id": grid.grid_id,
            "controller_variant": variant,
            "controller_family": family,
            "seed": seed,
            "structure": grid.structure,
            "g_internal": grid.g_internal,
            "theta_in_RE": grid.theta_in_RE,
            "theta_out_DW": grid.theta_out_DW,
            "out_layers": grid.out_layers,
            "n_cycles": 200,
            "E_R_in_cum": float(host["rin"][ix]),
            "E_R_out_cum": float(host["rout"][ix]),
            "net_resource_transfer": float(host["rin"][ix] - host["rout"][ix]),
            "E_W_out_cum": float(host["wout"][ix]),
            "resource_free_energy_consumed_cum": float(host["fcons"][ix]),
            "Delta_E_Qcell_cum": float(host["final_energy"][ix] - host["initial_energy"][ix]),
            "initial_E_Qcell": float(host["initial_energy"][ix]),
            "final_E_Qcell": float(host["final_energy"][ix]),
            "Q_noise_cum": float(host["qnoise"][ix]),
            "W_external_cum": 0.0,
            "energy_balance_residual_max_abs": float(host["max_res"][ix]),
            "D_population_mean": float(host["d_mean"][ix]),
            "D_population_peak": float(host["d_peak"][ix]),
            "D_to_W_flow_cum": float(host["wout"][ix]),
            "controller_action_count": float(host["action_count"][ix]),
            "controller_internal_action_count": float(host["internal_action_count"][ix]),
            "controller_output_action_count": float(host["output_action_count"][ix]),
            "controller_total_angle_budget": float(host["total_angle_budget"][ix]),
            "controller_internal_angle_budget": float(host["internal_angle_budget"][ix]),
            "controller_output_angle_budget": float(host["output_angle_budget"][ix]),
            "fixed_internal_angle_budget": fixed_internal_budget,
            "fixed_output_angle_budget": fixed_output_budget,
            "max_link_angle": float(host["max_link_angle"][ix]),
            "controller_switching_cost_status": "not_modeled",
            "signal_shuffle_seed": int(seeds[int(perm[ix].item())]) if "shuffled_signal" in family else "",
            "time_shift_amount": SHIFT if "time_shift" in family else 0,
            "action_source_variant": (
                "internal_controller" if family == "internal_time_shift"
                else "output_controller" if family == "output_time_shift"
                else ""
            ),
        }
        for name in cpu.SYS_NAMES:
            row[f"residence_{name}"] = float(host[f"residence_{name}"][ix])
        for _, _, name in links:
            row[f"controller_angle_budget_{name}"] = float(host[f"angle_budget_{name}"][ix])
            row[f"controller_action_count_{name}"] = float(host[f"action_count_{name}"][ix])
        rows.append(row)
    return rows


def run_grid(grid, seeds, device, part_dir, variants):
    precomputed = {}
    if any("internal_time_shift" in v for v in variants):
        precomputed["internal"], _ = precompute_action_sequences(grid, seeds, device, "internal")
    if any("output_time_shift" in v for v in variants):
        _, precomputed["output"] = precompute_action_sequences(grid, seeds, device, "output")
    rows = []
    for variant in variants:
        rows.extend(run_variant(grid, variant, seeds, device, precomputed))
    prefix = part_dir / grid.grid_id
    write_csv_atomic(prefix.with_name(prefix.name + "_summary.csv"), rows)
    marker = prefix.with_name(prefix.name + "_complete.json")
    tmp = marker.with_suffix(".tmp")
    tmp.write_text(json.dumps({
        "grid": asdict(grid),
        "variants": variants,
        "n_seeds": len(seeds),
        "summary_rows": len(rows),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, marker)


def concatenate_csv(inputs, output):
    fields = []
    for path in inputs:
        with path.open(newline="", encoding="utf-8") as f:
            for key in next(csv.reader(f), []):
                if key not in fields:
                    fields.append(key)
    tmp = output.with_suffix(output.suffix + ".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as dst:
        writer = csv.DictWriter(dst, fieldnames=fields)
        writer.writeheader()
        for path in inputs:
            with path.open(newline="", encoding="utf-8") as src:
                for row in csv.DictReader(src):
                    writer.writerow(row)
    os.replace(tmp, output)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", choices=("smoke", "pilot"), default="pilot")
    ap.add_argument("--n-seeds", type=int, default=20)
    ap.add_argument("--grid-ids-file", default="data/quantum_observation/qcell_local_controller_causal_test_v0_pilot_grid_ids.txt")
    ap.add_argument("--outdir", default=f"{EXPERIMENT}_outputs")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--max-grids", type=int, default=0)
    ap.add_argument("--minimal-variants", action="store_true")
    args = ap.parse_args()
    if args.device.startswith("cuda") and not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable")
    device = torch.device(args.device)
    grids = selected_grids(args.grid_ids_file)
    if args.max_grids:
        grids = grids[:args.max_grids]
    seeds = cpu.MAIN_SEEDS[:args.n_seeds]
    variants = VARIANTS
    if args.minimal_variants:
        variants = [
            "fixed_local_resource", "fixed_local_no_resource",
            "internal_controller_resource", "internal_controller_no_resource",
            "internal_shuffled_signal_resource", "internal_shuffled_signal_no_resource",
            "internal_time_shift_action_resource", "internal_time_shift_action_no_resource",
            "matched_central_resource", "matched_central_no_resource",
        ]
    out = Path(args.outdir)
    part_dir = out / "parts"
    part_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    completed = 0
    for i, grid in enumerate(grids, 1):
        marker = part_dir / f"{grid.grid_id}_complete.json"
        if args.resume and marker.exists():
            completed += 1
            print(f"skip {grid.grid_id} {i}/{len(grids)}", flush=True)
            continue
        g0 = time.time()
        run_grid(grid, seeds, device, part_dir, variants)
        completed += 1
        print(f"completed {grid.grid_id} {i}/{len(grids)} grid_seconds={time.time()-g0:.2f} total_seconds={time.time()-t0:.2f}", flush=True)
    if completed == len(grids):
        concatenate_csv([part_dir / f"{g.grid_id}_summary.csv" for g in grids],
                        out / f"{EXPERIMENT}_{args.profile}_seed_summary.csv")
    manifest = {
        "experiment": EXPERIMENT,
        "profile": args.profile,
        "device": str(device),
        "gpu": torch.cuda.get_device_name(device) if device.type == "cuda" else "",
        "n_grids": len(grids),
        "grid_ids": [g.grid_id for g in grids],
        "n_seeds": len(seeds),
        "cycles": 200,
        "variants": variants,
        "completed_grids": completed,
        "wall_seconds": time.time() - t0,
        "controller_switching_cost_status": "not_modeled",
        "time_shift_amount": SHIFT,
    }
    (out / f"{EXPERIMENT}_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

