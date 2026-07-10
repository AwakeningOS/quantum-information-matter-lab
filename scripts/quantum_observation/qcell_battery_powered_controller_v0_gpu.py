#!/usr/bin/env python3
"""Finite-M actuator-budget test for evolved Q-cell local controllers."""
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
import qcell_controller_evolution_v0_gpu as evo


EXPERIMENT = "qcell_battery_powered_controller_v0"
KAPPAS = [0.0, 0.00003, 0.0001, 0.0003, 0.001, 0.003, 0.01, 0.03]
M_LEVELS = ["unlimited", 20.0, 5.0, 1.0, 0.2, 0.0]
CONTROLLERS = [
    "fixed",
    "evolved",
    "hand_coded",
    "evolved_shuffled_signal",
    "evolved_time_shift",
    "evolved_random_budget",
]
EVOLVED_PARAMS = {
    "gain": 0.8954970900800753,
    "leak": 0.0,
    "downstream_bias": 1.6168544646335714,
    "ad_gate": 1.2724551382033202,
    "d_block": 1.2411067859023053,
    "max_angle_mult": 1.9116732153219738,
}
HAND_CODED = evo.HAND_CODED
SHIFT = 37


def parse_float_list(text):
    return [float(x.strip()) for x in text.split(",") if x.strip()]


def parse_m_levels(text):
    levels = []
    for item in text.split(","):
        item = item.strip()
        if not item:
            continue
        levels.append("unlimited" if item == "unlimited" else float(item))
    return levels


def parse_str_list(text):
    return [x.strip() for x in text.split(",") if x.strip()]


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


def read_csv_rows(path):
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def signature_for(args, kappas, m_levels, controllers, seeds):
    return {
        "n_seeds": len(seeds),
        "seeds": list(seeds),
        "kappas": kappas,
        "M_levels": m_levels,
        "controllers": controllers,
    }


def selected_grids(path):
    by_id = {g.grid_id: g for g in fixedmap.grids()}
    ids = fixedmap.read_grid_ids_file(path)
    return [by_id[x] for x in ids]


def m_value(m_level):
    if isinstance(m_level, str) and m_level == "unlimited":
        return math.inf
    return float(m_level)


def random_budget_angles(parts, grid, intended_angles, cycle, seed_offset=9173):
    """Same per-seed angle budget, random link allocation."""
    n, n_links = intended_angles.shape
    device = intended_angles.device
    # Deterministic pseudo-random weights from cycle and link index; same for all
    # seeds except a seed-dependent roll from current local energy ordering.
    gen = torch.Generator(device=device)
    gen.manual_seed(seed_offset + cycle * 131 + n_links)
    w = torch.rand((n, n_links), generator=gen, dtype=eng.RDTYPE, device=device)
    budget = intended_angles.abs().sum(dim=1, keepdim=True)
    return w / w.sum(dim=1, keepdim=True).clamp_min(1e-12) * budget


def precompute_intended_actions(grid, seeds, params, device):
    bits = torch.as_tensor(cpu.SYS_BITS, dtype=eng.RDTYPE, device=device)
    hamming = torch.as_tensor(cpu.HAMMING_SYS, dtype=eng.RDTYPE, device=device)
    zero = eng.t(cpu.r_state("R2_pure_0"), device)
    resource = eng.t(cpu.r_state("R3_pure_1"), device)
    rho = eng.random_products(seeds, device)
    actions = []
    for cycle in range(200):
        interact, _, mult = cpu.resource_for_cycle("R3_pure_1", cycle, "staged")
        if interact:
            for _ in range(mult):
                full = eng.full_state(rho, resource, zero)
                full = eng.apply_two_local(full, eng.exchange(grid.theta_in_RE, device), cpu.N_FULL, 0, 1)
                rho = eng.trace_full_to_sys(full)
        parts = eng.part_energies(rho, bits)
        angles = evo.param_angles_from_parts(parts, grid, params)
        actions.append(angles.detach())
        for col, (a, b, _) in enumerate(evo.links_for_grid(grid)):
            rho = lc.apply_two_local_batched_u(rho, lc.exchange_batch(angles[:, col], device), cpu.N_SYS, a, b)
        full = eng.full_state(rho, zero, zero)
        out_angle = torch.full((len(seeds),), grid.theta_out_DW * grid.out_layers, dtype=eng.RDTYPE, device=device)
        full = lc.apply_two_local_batched_u(full, lc.exchange_batch(out_angle, device), cpu.N_FULL, 5, 6)
        rho = eng.trace_full_to_sys(full)
        rho, _ = eng.apply_noise(rho, "N4_dephase_plus_amplitude_damping", 0.06, hamming, bits, device, strong=False)
    return actions


def run_controller_pair(grid, seeds, controller, params, kappa, m_initial, device, precomputed):
    results = {}
    for resource_on in (True, False):
        bits = torch.as_tensor(cpu.SYS_BITS, dtype=eng.RDTYPE, device=device)
        hamming = torch.as_tensor(cpu.HAMMING_SYS, dtype=eng.RDTYPE, device=device)
        zero = eng.t(cpu.r_state("R2_pure_0"), device)
        resource = eng.t(cpu.r_state("R3_pure_1"), device)
        rho = eng.random_products(seeds, device)
        n = len(seeds)
        links = evo.links_for_grid(grid)
        perm = torch.roll(torch.arange(n, device=device), shifts=1)
        initial_energy = eng.sys_energy(rho, bits)
        M = torch.full((n,), 1e30 if math.isinf(m_value(m_initial)) else m_value(m_initial), dtype=eng.RDTYPE, device=device)
        cum = {x: torch.zeros(n, dtype=eng.RDTYPE, device=device) for x in ("rin", "rout", "wout", "qnoise", "fcons")}
        spent = torch.zeros(n, dtype=eng.RDTYPE, device=device)
        starved = torch.zeros(n, dtype=eng.RDTYPE, device=device)
        emitted_when_starved = torch.zeros(n, dtype=eng.RDTYPE, device=device)
        angle_budget = torch.zeros(n, dtype=eng.RDTYPE, device=device)
        max_res = torch.zeros(n, dtype=eng.RDTYPE, device=device)
        for cycle in range(200):
            start_energy = eng.sys_energy(rho, bits)
            interact, _, mult = cpu.resource_for_cycle("R3_pure_1", cycle, "staged")
            if not resource_on:
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
            parts = eng.part_energies(rho, bits)
            if controller == "fixed":
                angles = torch.full((n, len(links)), grid.g_internal, dtype=eng.RDTYPE, device=device)
                intended = angles
                cost = torch.zeros(n, dtype=eng.RDTYPE, device=device)
            else:
                base_params = HAND_CODED if controller == "hand_coded" else params
                if controller == "evolved_shuffled_signal":
                    intended = evo.param_angles_from_parts(parts[perm], grid, base_params)
                elif controller == "evolved_time_shift":
                    intended = precomputed[(cycle + SHIFT) % 200]
                else:
                    intended = evo.param_angles_from_parts(parts, grid, base_params)
                if controller == "evolved_random_budget":
                    intended = random_budget_angles(parts, grid, intended, cycle)
                budget = intended.abs().sum(dim=1)
                cost = kappa * budget
                if math.isinf(m_value(m_initial)):
                    angles = intended
                    if kappa > 0:
                        spent += cost
                else:
                    has_power = M > 1e-15
                    scale = torch.where(
                        (cost > 1e-15) & has_power,
                        (M / cost).clamp(max=1.0),
                        has_power.to(eng.RDTYPE),
                    )
                    angles = intended * scale[:, None]
                    newly_starved = (~has_power) | ((cost > 1e-15) & (M < cost))
                    starved += (newly_starved & (budget > 1e-15)).to(eng.RDTYPE)
                    emitted_when_starved += ((M <= 1e-15) & (angles.abs().sum(dim=1) > 1e-12)).to(eng.RDTYPE)
                    paid = torch.minimum(M, cost)
                    M = M - paid
                    spent += paid
            angle_budget += angles.abs().sum(dim=1)
            for col, (a, b, _) in enumerate(links):
                rho = lc.apply_two_local_batched_u(rho, lc.exchange_batch(angles[:, col], device), cpu.N_SYS, a, b)
            full = eng.full_state(rho, zero, zero)
            out_angle = torch.full((n,), grid.theta_out_DW * grid.out_layers, dtype=eng.RDTYPE, device=device)
            full = lc.apply_two_local_batched_u(full, lc.exchange_batch(out_angle, device), cpu.N_FULL, 5, 6)
            wred = eng.trace_full_w(full)
            wout = wred[:, 1, 1].real
            rho = eng.trace_full_to_sys(full)
            rho, qnoise = eng.apply_noise(rho, "N4_dephase_plus_amplitude_damping", 0.06, hamming, bits, device, strong=False)
            end_energy = eng.sys_energy(rho, bits)
            residual = rin - ((end_energy - start_energy) + rout + wout + qnoise)
            max_res = torch.maximum(max_res, residual.abs())
            for key, val in (("rin", rin), ("rout", rout), ("wout", wout), ("qnoise", qnoise), ("fcons", fcons)):
                cum[key] += val
        final_energy = eng.sys_energy(rho, bits)
        host = {k: v.detach().cpu().numpy() for k, v in cum.items()}
        host.update({
            "spent": spent.detach().cpu().numpy(),
            "M_final": M.detach().cpu().numpy(),
            "starved": starved.detach().cpu().numpy(),
            "emitted_when_starved": emitted_when_starved.detach().cpu().numpy(),
            "angle_budget": angle_budget.detach().cpu().numpy(),
            "max_res": max_res.detach().cpu().numpy(),
            "initial_energy": initial_energy.detach().cpu().numpy(),
            "final_energy": final_energy.detach().cpu().numpy(),
        })
        results["resource" if resource_on else "no_resource"] = host
    rows = []
    res = results["resource"]
    no = results["no_resource"]
    for ix, seed in enumerate(seeds):
        rows.append({
            "grid_id": grid.grid_id,
            "seed": int(seed),
            "controller": controller,
            "kappa": kappa,
            "M_initial": m_initial,
            "W_resource": float(res["wout"][ix]),
            "W_no_resource": float(no["wout"][ix]),
            "resource_attributable_W": float(res["wout"][ix] - no["wout"][ix]),
            "controller_energy_spent": float(res["spent"][ix]),
            "M_energy_final": float(res["M_final"][ix]) if not math.isinf(m_value(m_initial)) else math.inf,
            "controller_starved_cycles": float(res["starved"][ix]),
            "emitted_when_starved_cycles": float(res["emitted_when_starved"][ix]),
            "angle_budget": float(res["angle_budget"][ix]),
            "net_resource_transfer": float(res["rin"][ix] - res["rout"][ix]),
            "Q_noise_cum": float(res["qnoise"][ix]),
            "energy_balance_residual_max_abs": float(max(res["max_res"][ix], no["max_res"][ix])),
            "signal_cost_status": "not_modelled",
            "computation_cost_status": "not_modelled",
            "coupling_switching_cost_status": "not_modelled",
        })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grid-ids-file", default="data/quantum_observation/qcell_controller_evolution_v0_grid_ids.txt")
    ap.add_argument("--outdir", default=f"{EXPERIMENT}_outputs")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--n-seeds", type=int, default=60)
    ap.add_argument("--kappas", default="")
    ap.add_argument("--m-levels", default="")
    ap.add_argument("--controllers", default="")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.device.startswith("cuda") and not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable")
    if args.smoke:
        args.n_seeds = 3
        kappas = [0.0, 0.0003]
        m_levels = ["unlimited", 0.0]
        controllers = ["fixed", "evolved", "evolved_shuffled_signal"]
    else:
        kappas = parse_float_list(args.kappas) if args.kappas else KAPPAS
        m_levels = parse_m_levels(args.m_levels) if args.m_levels else M_LEVELS
        controllers = parse_str_list(args.controllers) if args.controllers else CONTROLLERS
    device = torch.device(args.device)
    grids = selected_grids(args.grid_ids_file)
    seeds = cpu.MAIN_SEEDS[40:40 + args.n_seeds]
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    parts = out / "parts"
    parts.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    rows = []
    run_signature = signature_for(args, kappas, m_levels, controllers, seeds)
    for grid in grids:
        grid_csv = parts / f"{grid.grid_id}_summary.csv"
        grid_done = parts / f"{grid.grid_id}_complete.json"
        if grid_done.exists() and grid_csv.exists():
            done = json.loads(grid_done.read_text(encoding="utf-8"))
            if done.get("run_signature") == run_signature:
                grid_rows = read_csv_rows(grid_csv)
                rows.extend(grid_rows)
                print(f"skipped {grid.grid_id} rows={len(grid_rows)}", flush=True)
                continue
        precomputed = precompute_intended_actions(grid, seeds, EVOLVED_PARAMS, device)
        grid_rows = []
        for kappa in kappas:
            for m_initial in m_levels:
                for controller in controllers:
                    if controller == "fixed" and (kappa != kappas[0] or m_initial != m_levels[0]):
                        continue
                    grid_rows.extend(run_controller_pair(grid, seeds, controller, EVOLVED_PARAMS, kappa, m_initial, device, precomputed))
        write_csv_atomic(grid_csv, grid_rows)
        grid_done.write_text(
            json.dumps(
                {
                    "grid_id": grid.grid_id,
                    "rows": len(grid_rows),
                    "run_signature": run_signature,
                    "completed_at_unix": time.time(),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        rows.extend(grid_rows)
        print(f"completed {grid.grid_id} elapsed={time.time()-t0:.1f}s", flush=True)
    write_csv_atomic(out / f"{EXPERIMENT}_seed_summary.csv", rows)
    manifest = {
        "experiment": EXPERIMENT,
        "device": str(device),
        "gpu": torch.cuda.get_device_name(device) if device.type == "cuda" else "",
        "grids": [g.grid_id for g in grids],
        "n_seeds": len(seeds),
        "seeds": seeds,
        "kappas": kappas,
        "M_levels": m_levels,
        "controllers": controllers,
        "wall_seconds": time.time() - t0,
        "model_note": "finite actuator budget only; signal/computation/switching costs not modelled",
    }
    (out / f"{EXPERIMENT}_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
