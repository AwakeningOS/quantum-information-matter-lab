#!/usr/bin/env python3
"""GPU runner for the corrected fixed-circuit output bottleneck map.

Each grid point contains four matched variants and is saved atomically.
Completed grid points are resumable. Stage 1 intentionally records only
the state and flow quantities required by the preregistered bottleneck map.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import os
import time
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np
import torch

import qcell_local_linked_energy_machine_full2q7_final_v0 as cpu
import qcell_local_linked_energy_machine_full2q7_final_v0_gpu as eng


EXPERIMENT = "qcell_fixed_circuit_output_bottleneck_map_v0"
G_VALUES = [0.025, 0.05, 0.10, 0.20, 0.40]
THETA_IN_VALUES = [0.05, 0.10, 0.20, 0.40, 0.80]
THETA_OUT_VALUES = [0.05, 0.10, 0.20, 0.40, 0.80]
OUT_LAYERS_VALUES = [1, 2, 4, 8]
STRUCTURES = ["chain", "ring"]
VARIANTS = [
    "local_resource", "local_no_resource",
    "central_resource", "central_no_resource",
]


@dataclass(frozen=True)
class Grid:
    grid_id: str
    structure: str
    g_internal: float
    theta_in_RE: float
    theta_out_DW: float
    out_layers: int


def grids():
    out = []
    for structure in STRUCTURES:
        for g in G_VALUES:
            for tin in THETA_IN_VALUES:
                for tout in THETA_OUT_VALUES:
                    for layers in OUT_LAYERS_VALUES:
                        out.append(Grid(
                            f"QFCBM_{len(out)+1:04d}", structure, g, tin, tout, layers
                        ))
    return out


def write_gzip_csv_atomic(path, rows):
    if not rows:
        return
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with gzip.open(tmp, "wt", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    os.replace(tmp, path)


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
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    os.replace(tmp, path)


def output_commutator_norm(theta):
    u = cpu.exchange2(theta)
    h = np.diag([0, 1, 1, 2]).astype(np.complex128)
    return float(np.linalg.norm(u @ h - h @ u))


def condition_for(grid, central):
    variant = grid.structure
    cond = cpu.Condition(
        condition_id=grid.grid_id,
        variant=variant,
        resource="R3_pure_1",
        noise="N4_dephase_plus_amplitude_damping",
        p=0.06,
        g=grid.g_internal,
        theta=grid.theta_in_RE,
        fault="none",
        schedule="staged",
    )
    return cond, central


def meta(grid, variant_type):
    return {
        "grid_id": grid.grid_id,
        "variant_type": variant_type,
        "structure": grid.structure,
        "g_internal": grid.g_internal,
        "theta_in_RE": grid.theta_in_RE,
        "theta_out_DW": grid.theta_out_DW,
        "out_layers": grid.out_layers,
    }


def run_variant(grid, variant_type, seeds, device):
    has_resource = variant_type.endswith("_resource") and "no_resource" not in variant_type
    central = variant_type.startswith("central_")
    cond, _ = condition_for(grid, central)
    n = len(seeds)
    bits = torch.as_tensor(cpu.SYS_BITS, dtype=eng.RDTYPE, device=device)
    hamming = torch.as_tensor(cpu.HAMMING_SYS, dtype=eng.RDTYPE, device=device)
    zero = eng.t(cpu.r_state("R2_pure_0"), device)
    resource = eng.t(cpu.r_state("R3_pure_1"), device)
    uin = eng.exchange(grid.theta_in_RE, device)
    uout = eng.exchange(grid.theta_out_DW, device)
    rho = eng.random_products(seeds, device)
    initial_energy = eng.sys_energy(rho, bits).detach().cpu().numpy()
    residence = torch.zeros((n, cpu.N_SYS), dtype=eng.RDTYPE, device=device)
    cumulative = {
        key: torch.zeros(n, dtype=eng.RDTYPE, device=device)
        for key in ("rin", "rout", "wout", "qnoise", "wext", "fcons", "dflow")
    }
    max_residual = torch.zeros(n, dtype=eng.RDTYPE, device=device)
    d_peak = torch.zeros(n, dtype=eng.RDTYPE, device=device)
    d_sum = torch.zeros(n, dtype=eng.RDTYPE, device=device)
    cyclewise, ledger, linkflow = [], [], []

    fixed = meta(grid, variant_type)
    for cycle in range(200):
        start_energy = eng.sys_energy(rho, bits)
        interact, _, mult = cpu.resource_for_cycle("R3_pure_1", cycle, "staged")
        if not has_resource:
            interact, mult = False, 0
        rin = torch.zeros(n, dtype=eng.RDTYPE, device=device)
        rout = torch.zeros_like(rin)
        fcons = torch.zeros_like(rin)
        if interact:
            for _ in range(mult):
                rin += 1.0
                full = eng.full_state(rho, resource, zero)
                full = eng.apply_two_local(full, uin, cpu.N_FULL, 0, 1)
                rred = eng.trace_full_r(full)
                rho = eng.trace_full_to_sys(full)
                rout += rred[:, 1, 1].real
                fcons += 1.0 - (
                    rred[:, 1, 1].real - eng.entropy_batch(rred, base2=False)
                )

        before_links = eng.part_energies(rho, bits)
        link_values = {}
        for a, b, angle, name in cpu.links(cond, cycle):
            before = eng.part_energies(rho, bits)
            rho = eng.apply_two_local(rho, eng.exchange(angle, device), cpu.N_SYS, a, b)
            after = eng.part_energies(rho, bits)
            link_values[f"flow_{name}"] = (
                link_values.get(f"flow_{name}", torch.zeros_like(rin))
                + after[:, b] - before[:, b]
            )
        if central:
            before = eng.part_energies(rho, bits)
            rho = eng.apply_two_local(
                rho, eng.exchange(grid.g_internal * 2.0, device), cpu.N_SYS, 0, 4
            )
            after = eng.part_energies(rho, bits)
            link_values["flow_ED_direct_upper_bound"] = after[:, 4] - before[:, 4]

        full = eng.full_state(rho, zero, zero)
        for _ in range(grid.out_layers):
            full = eng.apply_two_local(full, uout, cpu.N_FULL, 5, 6)
        wred = eng.trace_full_w(full)
        wout = wred[:, 1, 1].real
        rho = eng.trace_full_to_sys(full)

        rho, qnoise = eng.apply_noise(
            rho, cond.noise, cond.p, hamming, bits, device, strong=False
        )
        end_energy = eng.sys_energy(rho, bits)
        delta = end_energy - start_energy
        residual = rin - (delta + rout + wout + qnoise)
        max_residual = torch.maximum(max_residual, residual.abs())
        parts = eng.part_energies(rho, bits)
        residence += parts
        d = parts[:, 4]
        d_sum += d
        d_peak = torch.maximum(d_peak, d)
        for key, value in (
            ("rin", rin), ("rout", rout), ("wout", wout),
            ("qnoise", qnoise), ("fcons", fcons), ("dflow", wout),
        ):
            cumulative[key] += value

        diag = rho.diagonal(dim1=-2, dim2=-1).real
        coh = rho.abs().sum(dim=(1, 2)) - diag.abs().sum(dim=1)
        pur = torch.einsum("nij,nji->n", rho, rho).real
        host = {
            "E_internal": end_energy, "l1_coherence": coh, "purity": pur,
            "E_E": parts[:,0], "E_A": parts[:,1], "E_B": parts[:,2],
            "E_C": parts[:,3], "E_D": parts[:,4],
            "D_population": d, "E_W_out": wout,
        }
        host = {k: v.detach().cpu().numpy() for k,v in host.items()}
        led_host = {
            "E_R_in": rin, "E_R_out": rout, "Delta_E_Qcell": delta,
            "E_W_out": wout, "Q_noise": qnoise,
            "W_external": torch.zeros_like(rin),
            "energy_balance_residual": residual,
            "resource_free_energy_consumed": fcons,
        }
        led_host = {k: v.detach().cpu().numpy() for k,v in led_host.items()}
        flow_host = {k: v.detach().cpu().numpy() for k,v in link_values.items()}
        for ix, seed in enumerate(seeds):
            cyclewise.append({
                **fixed, "seed": seed, "cycle": cycle+1,
                **{k: float(v[ix]) for k,v in host.items()},
            })
            ledger.append({
                **fixed, "seed": seed, "cycle": cycle+1,
                **{k: float(v[ix]) for k,v in led_host.items()},
            })
            linkflow.append({
                **fixed, "seed": seed, "cycle": cycle+1,
                "D_to_W_flow": float(wout[ix].item()),
                **{k: float(v[ix]) for k,v in flow_host.items()},
            })

        if not torch.isfinite(rho).all():
            raise RuntimeError(f"non-finite state {grid.grid_id} {variant_type} cycle={cycle+1}")
        tr = rho.diagonal(dim1=-2, dim2=-1).sum(-1).real
        if torch.max(torch.abs(tr - 1)).item() > 1e-7:
            raise RuntimeError(f"trace drift {grid.grid_id} {variant_type} cycle={cycle+1}")

    final_energy = eng.sys_energy(rho, bits).detach().cpu().numpy()
    cum = {k: v.detach().cpu().numpy() for k,v in cumulative.items()}
    residence_host = residence.detach().cpu().numpy()
    d_mean = (d_sum / 200).detach().cpu().numpy()
    d_peak_host = d_peak.detach().cpu().numpy()
    max_res = max_residual.detach().cpu().numpy()
    comm = output_commutator_norm(grid.theta_out_DW)
    summary = []
    for ix, seed in enumerate(seeds):
        row = {
            **fixed, "seed": seed,
            "E_R_in_cum": float(cum["rin"][ix]),
            "E_R_out_cum": float(cum["rout"][ix]),
            "E_W_out_cum": float(cum["wout"][ix]),
            "Delta_E_Qcell_cum": float(final_energy[ix] - initial_energy[ix]),
            "Q_noise_cum": float(cum["qnoise"][ix]),
            "W_external_cum": 0.0,
            "energy_balance_residual_max_abs": float(max_res[ix]),
            "resource_free_energy_consumed_cum": float(cum["fcons"][ix]),
            "initial_E_Qcell": float(initial_energy[ix]),
            "final_E_Qcell": float(final_energy[ix]),
            "D_population_mean": float(d_mean[ix]),
            "D_population_peak": float(d_peak_host[ix]),
            "D_to_W_flow_cum": float(cum["dflow"][ix]),
            "U_DW_commutator_norm": comm,
            "output_switching_cost_status": "not_modeled",
        }
        for q, name in enumerate(cpu.SYS_NAMES):
            row[f"residence_{name}"] = float(residence_host[ix, q])
        summary.append(row)
    return summary, cyclewise, linkflow, ledger


def run_grid(grid, seeds, device, part_dir):
    summaries, cycles, flows, ledgers = [], [], [], []
    for variant in VARIANTS:
        s, c, f, l = run_variant(grid, variant, seeds, device)
        summaries += s
        cycles += c
        flows += f
        ledgers += l
    prefix = part_dir / grid.grid_id
    write_csv_atomic(prefix.with_name(prefix.name + "_summary.csv"), summaries)
    write_gzip_csv_atomic(prefix.with_name(prefix.name + "_cyclewise.csv.gz"), cycles)
    write_gzip_csv_atomic(prefix.with_name(prefix.name + "_linkflow.csv.gz"), flows)
    write_gzip_csv_atomic(prefix.with_name(prefix.name + "_ledger.csv.gz"), ledgers)
    marker = prefix.with_name(prefix.name + "_complete.json")
    tmp = marker.with_suffix(".tmp")
    tmp.write_text(json.dumps({
        "grid": asdict(grid), "variants": VARIANTS, "n_seeds": len(seeds),
        "summary_rows": len(summaries), "cyclewise_rows": len(cycles),
        "linkflow_rows": len(flows), "ledger_rows": len(ledgers),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, marker)


def concatenate_csv(inputs, output, compressed=False):
    if not inputs:
        return
    fields = []
    opener = gzip.open if compressed else open
    for path in inputs:
        with opener(path, "rt", newline="", encoding="utf-8") as f:
            for key in next(csv.reader(f), []):
                if key not in fields:
                    fields.append(key)
    tmp = output.with_suffix(output.suffix + ".tmp")
    with open(tmp, "w", newline="", encoding="utf-8") as dst:
        writer = csv.DictWriter(dst, fieldnames=fields)
        writer.writeheader()
        for path in inputs:
            with opener(path, "rt", newline="", encoding="utf-8") as src:
                for row in csv.DictReader(src):
                    writer.writerow(row)
    os.replace(tmp, output)


def merge(out, selected, stage):
    parts = out / "parts"
    concatenate_csv(
        [parts / f"{g.grid_id}_summary.csv" for g in selected],
        out / f"{stage}_condition_seed_summary.csv",
    )
    concatenate_csv(
        [parts / f"{g.grid_id}_cyclewise.csv.gz" for g in selected],
        out / f"{EXPERIMENT}_{stage}_cyclewise.csv",
        compressed=True,
    )
    concatenate_csv(
        [parts / f"{g.grid_id}_linkflow.csv.gz" for g in selected],
        out / f"{EXPERIMENT}_{stage}_linkflow.csv",
        compressed=True,
    )
    concatenate_csv(
        [parts / f"{g.grid_id}_ledger.csv.gz" for g in selected],
        out / f"{EXPERIMENT}_{stage}_ledger.csv",
        compressed=True,
    )


def read_grid_ids_file(path):
    """Read one grid_id per line, allowing comments and comma-separated lines."""
    ids = []
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        for part in line.split(","):
            grid_id = part.strip()
            if grid_id:
                ids.append(grid_id)
    return ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=("stage1", "stage2"), default="stage1")
    ap.add_argument("--n-seeds", type=int, default=10)
    ap.add_argument("--outdir", default=f"{EXPERIMENT}_outputs")
    ap.add_argument("--grid-start", type=int, default=0)
    ap.add_argument("--grid-end", type=int, default=0)
    ap.add_argument(
        "--grid-ids-file",
        default="",
        help="Optional file with explicit QFCBM_#### grid IDs to run, one per line.",
    )
    ap.add_argument("--max-grids", type=int, default=0)
    ap.add_argument("--shard-index", type=int, default=0)
    ap.add_argument("--shard-count", type=int, default=1)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--no-merge", action="store_true")
    ap.add_argument("--device", default="cuda")
    args = ap.parse_args()
    if args.device.startswith("cuda") and not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable")
    device = torch.device(args.device)
    selected = grids()
    if args.grid_ids_file:
        wanted = read_grid_ids_file(args.grid_ids_file)
        by_id = {g.grid_id: g for g in selected}
        missing = [grid_id for grid_id in wanted if grid_id not in by_id]
        if missing:
            raise SystemExit(f"unknown grid IDs in {args.grid_ids_file}: {missing}")
        selected = [by_id[grid_id] for grid_id in wanted]
    end = args.grid_end or len(selected)
    selected = selected[args.grid_start:end]
    selected = [g for i,g in enumerate(selected) if i % args.shard_count == args.shard_index]
    if args.max_grids:
        selected = selected[:args.max_grids]
    seeds = cpu.MAIN_SEEDS[:args.n_seeds]
    out = Path(args.outdir)
    part_dir = out / "parts"
    part_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    completed = 0
    for i, grid in enumerate(selected, 1):
        marker = part_dir / f"{grid.grid_id}_complete.json"
        if args.resume and marker.exists():
            completed += 1
            print(f"skip {grid.grid_id} {i}/{len(selected)}", flush=True)
            continue
        g0 = time.time()
        run_grid(grid, seeds, device, part_dir)
        completed += 1
        print(f"completed {grid.grid_id} {i}/{len(selected)} "
              f"grid_seconds={time.time()-g0:.2f} total_seconds={time.time()-t0:.2f}",
              flush=True)
    if not args.no_merge and completed == len(selected):
        merge(out, selected, args.stage)
    manifest = {
        "experiment": EXPERIMENT, "stage": args.stage,
        "device": str(device),
        "gpu": torch.cuda.get_device_name(device) if device.type == "cuda" else "",
        "n_grids": len(selected), "variants_per_grid": 4,
        "n_seeds": len(seeds), "cycles": 200,
        "completed_grids": completed, "resume_supported": True,
        "grid_ids_file": args.grid_ids_file,
        "grid_ids": [g.grid_id for g in selected],
        "wall_seconds": time.time()-t0,
        "output_switching_cost_status": "not_modeled",
    }
    (out / f"{EXPERIMENT}_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
