#!/usr/bin/env python3
"""Anti-bookkeeping controls for Q-cell stored-power actuator v0."""
from __future__ import annotations

import argparse
import csv
import json
import os
import time
from pathlib import Path

import torch

import qcell_stored_power_actuator_v0_gpu as base


EXPERIMENT = "qcell_stored_power_actuator_v0_controls"


CONTROL_CONDITIONS = [
    ("real_restart", "supply_restart_after_stop_initial_zero", 0.0, "normal"),
    ("supply_label_only_restart", "supply_restart_after_stop_initial_zero", 0.0, "label_only"),
    ("store_shuffle_restart", "supply_restart_after_stop_initial_zero", 0.0, "store_shuffle"),
    ("equal_total_early", "equal_total_early_initial_zero", 0.0, "normal"),
    ("equal_total_late", "equal_total_late_initial_zero", 0.0, "normal"),
    ("equal_total_pulsed", "equal_total_pulsed_initial_zero", 0.0, "normal"),
    ("equal_total_continuous", "equal_total_continuous_initial_zero", 0.0, "normal"),
    ("no_controller_drain_always", "supply_always_on_initial_zero", 0.0, "no_controller_drain"),
]


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


def supply_for(condition: str, cycle: int) -> float:
    if condition.startswith("equal_total_early"):
        return 1.0 if cycle < 80 else 0.0
    if condition.startswith("equal_total_late"):
        return 1.0 if cycle >= 120 else 0.0
    if condition.startswith("equal_total_pulsed"):
        return 1.0 if cycle % 2 == 0 and cycle < 160 else 0.0
    if condition.startswith("equal_total_continuous"):
        return 0.4
    return base.supply_for(condition, cycle)


def shuffled_gate_store(condition: str, cycle: int, device) -> torch.Tensor:
    # Fixed deterministic time shuffle: use the restart schedule, but read it in
    # a scrambled order so total values are similar while causal timing is broken.
    permuted_cycle = (cycle * 37 + 19) % base.N_CYCLES
    s = 0.0
    values = []
    for t in range(base.N_CYCLES):
        s = min(base.STORE_CAPACITY, s + base.SUPPLY_GAIN * base.supply_for(condition, t))
        values.append(s)
        # approximate the normal evolved spend scale from the successful run:
        # this is only a negative-control gate trace, not the accounting store.
        s = max(0.0, s - 0.045)
    return torch.tensor(values[permuted_cycle], dtype=base.eng.RDTYPE, device=device)


def run_trajectory(grid, seeds, label: str, condition: str, initial_store: float, mode: str, resource_on: bool, device):
    bits = torch.as_tensor(base.cpu.SYS_BITS, dtype=base.eng.RDTYPE, device=device)
    hamming = torch.as_tensor(base.cpu.HAMMING_SYS, dtype=base.eng.RDTYPE, device=device)
    zero = base.eng.t(base.cpu.r_state("R2_pure_0"), device)
    resource = base.eng.t(base.cpu.r_state("R3_pure_1"), device)
    rho = base.eng.random_products(seeds, device)
    links = base.evo.links_for_grid(grid)
    n = len(seeds)
    store = torch.full((n,), initial_store, dtype=base.eng.RDTYPE, device=device).clamp(0.0, base.STORE_CAPACITY)
    cumulative_w = torch.zeros(n, dtype=base.eng.RDTYPE, device=device)
    trace: list[dict] = []

    for cycle in range(base.N_CYCLES):
        start_energy = base.eng.sys_energy(rho, bits)
        external_supply_in = supply_for(condition, cycle) if resource_on else 0.0
        store_before_fill = store.clone()
        charge = 0.0 if mode == "label_only" else base.SUPPLY_GAIN * external_supply_in
        store_before_action = (store + charge).clamp(0.0, base.STORE_CAPACITY)
        if mode == "store_shuffle":
            store_before_action = shuffled_gate_store(condition, cycle, device).repeat(n)
        store = store_before_action

        rin = torch.zeros(n, dtype=base.eng.RDTYPE, device=device)
        rout = torch.zeros_like(rin)
        interact, _, mult = base.cpu.resource_for_cycle("R3_pure_1", cycle, "staged")
        if not resource_on:
            interact, mult = False, 0
        if interact:
            for _ in range(mult):
                rin += 1.0
                full = base.eng.full_state(rho, resource, zero)
                full = base.eng.apply_two_local(full, base.eng.exchange(grid.theta_in_RE, device), base.cpu.N_FULL, 0, 1)
                rred = base.eng.trace_full_r(full)
                rho = base.eng.trace_full_to_sys(full)
                rout += rred[:, 1, 1].real

        parts = base.eng.part_energies(rho, bits)
        intended = base.evo.param_angles_from_parts(parts, grid, base.EVOLVED_PARAMS)
        requested_budget = intended.abs().sum(dim=1)
        action_cost = base.KAPPA * requested_budget
        action_requested = requested_budget > base.EPS
        action_allowed = action_requested & (store_before_action + base.EPS >= action_cost)
        if mode == "no_controller_drain":
            action_allowed = torch.zeros_like(action_allowed)
        angles = torch.where(action_allowed[:, None], intended, torch.zeros_like(intended))
        spent = torch.where(action_allowed, action_cost, torch.zeros_like(action_cost))
        starved = action_requested & (~action_allowed)
        store_after_action = (store_before_action - spent - base.LEAK).clamp(0.0, base.STORE_CAPACITY)
        store = store_after_action

        for col, (a, b, _) in enumerate(links):
            rho = base.lc.apply_two_local_batched_u(rho, base.lc.exchange_batch(angles[:, col], device), base.cpu.N_SYS, a, b)
        full = base.eng.full_state(rho, zero, zero)
        out_angle = torch.full((n,), grid.theta_out_DW * grid.out_layers, dtype=base.eng.RDTYPE, device=device)
        full = base.lc.apply_two_local_batched_u(full, base.lc.exchange_batch(out_angle, device), base.cpu.N_FULL, 5, 6)
        wred = base.eng.trace_full_w(full)
        wout = wred[:, 1, 1].real
        cumulative_w += wout
        rho = base.eng.trace_full_to_sys(full)
        rho, qnoise = base.eng.apply_noise(rho, "N4_dephase_plus_amplitude_damping", 0.06, hamming, bits, device, strong=False)
        end_energy = base.eng.sys_energy(rho, bits)
        residual = rin - ((end_energy - start_energy) + rout + wout + qnoise)

        host = {k: v.detach().cpu() for k, v in {
            "store_before_fill": store_before_fill,
            "store_before_action": store_before_action,
            "requested_budget": requested_budget,
            "action_cost": action_cost,
            "action_requested": action_requested,
            "action_allowed": action_allowed,
            "spent": spent,
            "store_after_action": store_after_action,
            "starved": starved,
            "wout": wout,
            "cum_w": cumulative_w,
            "residual": residual,
        }.items()}
        for ix, seed in enumerate(seeds):
            trace.append({
                "t": cycle,
                "seed": int(seed),
                "condition": label,
                "source_condition": condition,
                "control_mode": mode,
                "resource_on": int(resource_on),
                "supply_on": int(external_supply_in > 0),
                "external_supply_in": external_supply_in,
                "store_before_fill": float(host["store_before_fill"][ix]),
                "store_before_action": float(host["store_before_action"][ix]),
                "controller_action_requested": int(bool(host["action_requested"][ix])),
                "controller_action_allowed": int(bool(host["action_allowed"][ix])),
                "controller_requested_angle_budget": float(host["requested_budget"][ix]),
                "controller_action_cost": float(host["action_cost"][ix]),
                "controller_energy_spent": float(host["spent"][ix]),
                "store_after_action": float(host["store_after_action"][ix]),
                "controller_starved": int(bool(host["starved"][ix])),
                "W_cycle": float(host["wout"][ix]),
                "W_cumulative": float(host["cum_w"][ix]),
                "accounting_residual": float(host["residual"][ix]),
            })
    return trace


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
    grid = base.q0988_grid()
    seeds = base.cpu.MAIN_SEEDS[40 : 40 + args.n_seeds]
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)

    resource_trace: list[dict] = []
    no_resource_trace: list[dict] = []
    for label, condition, initial_store, mode in CONTROL_CONDITIONS:
        print(f"condition={label}", flush=True)
        resource_trace.extend(run_trajectory(grid, seeds, label, condition, initial_store, mode, True, device))
        no_resource_trace.extend(run_trajectory(grid, seeds, label, condition, initial_store, mode, False, device))

    cycle_rows, seed_rows = base.paired_rows(resource_trace, no_resource_trace)
    write_csv_atomic(out / f"{EXPERIMENT}_cycle_trace.csv", cycle_rows)
    write_csv_atomic(out / f"{EXPERIMENT}_seed_summary.csv", seed_rows)
    manifest = {
        "experiment": EXPERIMENT,
        "status": "completed",
        "grid_id": base.GRID_ID,
        "device": str(device),
        "gpu": torch.cuda.get_device_name(device) if device.type == "cuda" else "",
        "n_seeds": len(seeds),
        "conditions": [c[0] for c in CONTROL_CONDITIONS],
        "n_cycles": base.N_CYCLES,
        "kappa": base.KAPPA,
        "store_capacity": base.STORE_CAPACITY,
        "supply_gain": base.SUPPLY_GAIN,
        "cycle_rows": len(cycle_rows),
        "seed_rows": len(seed_rows),
        "wall_seconds": time.time() - t0,
        "max_zero_store_action_violations": max(r["zero_store_action_violations"] for r in seed_rows),
        "max_action_without_spend_violations": max(r["action_without_spend_violations"] for r in seed_rows),
        "max_empty_store_action_violations": max(r["empty_store_action_violations"] for r in seed_rows),
        "max_accounting_residual_abs": max(r["max_accounting_residual_abs"] for r in seed_rows),
    }
    (out / f"{EXPERIMENT}_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
