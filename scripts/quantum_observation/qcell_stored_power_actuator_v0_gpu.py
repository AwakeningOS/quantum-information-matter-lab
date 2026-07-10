#!/usr/bin/env python3
"""Stored-power actuator trace test for QFCBM_0988."""
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
import qcell_local_controller_causal_test_v0_gpu as lc
import qcell_controller_evolution_v0_gpu as evo


EXPERIMENT = "qcell_stored_power_actuator_v0"
GRID_ID = "QFCBM_0988"
N_CYCLES = 200
KAPPA = 0.03
STORE_CAPACITY = 1.0
SUPPLY_GAIN = 0.08
LEAK = 0.0
INITIAL_POSITIVE_STORE = 1.0
EPS = 1e-12
EVOLVED_PARAMS = {
    "gain": 0.8954970900800753,
    "leak": 0.0,
    "downstream_bias": 1.6168544646335714,
    "ad_gate": 1.2724551382033202,
    "d_block": 1.2411067859023053,
    "max_angle_mult": 1.9116732153219738,
}


CONDITIONS = [
    ("supply_never_on_initial_zero", 0.0),
    ("supply_always_on_initial_zero", 0.0),
    ("supply_stop_midway_initial_zero", 0.0),
    ("supply_restart_after_stop_initial_zero", 0.0),
    ("supply_never_on_initial_positive", INITIAL_POSITIVE_STORE),
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


def q0988_grid():
    for grid in fixedmap.grids():
        if grid.grid_id == GRID_ID:
            return grid
    raise RuntimeError(f"{GRID_ID} not found")


def supply_for(condition: str, cycle: int) -> float:
    if condition.startswith("supply_always_on"):
        return 1.0
    if condition.startswith("supply_stop_midway"):
        return 1.0 if cycle < 80 else 0.0
    if condition.startswith("supply_restart_after_stop"):
        return 1.0 if cycle < 60 or cycle >= 120 else 0.0
    return 0.0


def run_trajectory(grid, seeds, condition: str, initial_store: float, resource_on: bool, device):
    bits = torch.as_tensor(cpu.SYS_BITS, dtype=eng.RDTYPE, device=device)
    hamming = torch.as_tensor(cpu.HAMMING_SYS, dtype=eng.RDTYPE, device=device)
    zero = eng.t(cpu.r_state("R2_pure_0"), device)
    resource = eng.t(cpu.r_state("R3_pure_1"), device)
    rho = eng.random_products(seeds, device)
    links = evo.links_for_grid(grid)
    n = len(seeds)
    store = torch.full((n,), initial_store, dtype=eng.RDTYPE, device=device).clamp(0.0, STORE_CAPACITY)
    cumulative_w = torch.zeros(n, dtype=eng.RDTYPE, device=device)
    trace: list[dict] = []

    for cycle in range(N_CYCLES):
        start_energy = eng.sys_energy(rho, bits)
        external_supply_in = supply_for(condition, cycle) if resource_on else 0.0
        store_before_fill = store.clone()
        store_before_action = (store + SUPPLY_GAIN * external_supply_in).clamp(0.0, STORE_CAPACITY)
        store = store_before_action

        rin = torch.zeros(n, dtype=eng.RDTYPE, device=device)
        rout = torch.zeros_like(rin)
        fcons = torch.zeros_like(rin)
        interact, _, mult = cpu.resource_for_cycle("R3_pure_1", cycle, "staged")
        if not resource_on:
            interact, mult = False, 0
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
        intended = evo.param_angles_from_parts(parts, grid, EVOLVED_PARAMS)
        requested_budget = intended.abs().sum(dim=1)
        action_cost = KAPPA * requested_budget
        action_requested = requested_budget > EPS
        action_allowed = action_requested & (store_before_action + EPS >= action_cost)
        angles = torch.where(action_allowed[:, None], intended, torch.zeros_like(intended))
        controller_energy_spent = torch.where(action_allowed, action_cost, torch.zeros_like(action_cost))
        controller_starved = action_requested & (~action_allowed)
        store_after_action = (store_before_action - controller_energy_spent - LEAK).clamp(0.0, STORE_CAPACITY)
        store = store_after_action

        for col, (a, b, _) in enumerate(links):
            rho = lc.apply_two_local_batched_u(rho, lc.exchange_batch(angles[:, col], device), cpu.N_SYS, a, b)
        full = eng.full_state(rho, zero, zero)
        out_angle = torch.full((n,), grid.theta_out_DW * grid.out_layers, dtype=eng.RDTYPE, device=device)
        full = lc.apply_two_local_batched_u(full, lc.exchange_batch(out_angle, device), cpu.N_FULL, 5, 6)
        wred = eng.trace_full_w(full)
        wout = wred[:, 1, 1].real
        cumulative_w += wout
        rho = eng.trace_full_to_sys(full)
        rho, qnoise = eng.apply_noise(rho, "N4_dephase_plus_amplitude_damping", 0.06, hamming, bits, device, strong=False)
        end_energy = eng.sys_energy(rho, bits)
        residual = rin - ((end_energy - start_energy) + rout + wout + qnoise)

        host = {
            "store_before_fill": store_before_fill.detach().cpu(),
            "store_before_action": store_before_action.detach().cpu(),
            "requested_budget": requested_budget.detach().cpu(),
            "action_cost": action_cost.detach().cpu(),
            "action_requested": action_requested.detach().cpu(),
            "action_allowed": action_allowed.detach().cpu(),
            "spent": controller_energy_spent.detach().cpu(),
            "store_after_action": store_after_action.detach().cpu(),
            "starved": controller_starved.detach().cpu(),
            "wout": wout.detach().cpu(),
            "cum_w": cumulative_w.detach().cpu(),
            "residual": residual.detach().cpu(),
        }
        for ix, seed in enumerate(seeds):
            trace.append(
                {
                    "t": cycle,
                    "seed": int(seed),
                    "condition": condition,
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
                }
            )
    return trace


def paired_rows(resource_trace: list[dict], no_resource_trace: list[dict]) -> tuple[list[dict], list[dict]]:
    paired: list[dict] = []
    summary: dict[tuple[str, int], dict] = {}
    no_by_key = {(r["condition"], r["seed"], r["t"]): r for r in no_resource_trace}
    for r in resource_trace:
        n = no_by_key[(r["condition"], r["seed"], r["t"])]
        w_attr = r["W_cumulative"] - n["W_cumulative"]
        row = {
            **r,
            "W_resource_cycle": r["W_cycle"],
            "W_no_resource_cycle": n["W_cycle"],
            "resource_attributable_W_cycle": r["W_cycle"] - n["W_cycle"],
            "W_resource": r["W_cumulative"],
            "W_no_resource": n["W_cumulative"],
            "resource_attributable_W": w_attr,
            "accounting_residual_no_resource": n["accounting_residual"],
        }
        paired.append(row)
        key = (r["condition"], r["seed"])
        s = summary.setdefault(
            key,
            {
                "condition": r["condition"],
                "seed": r["seed"],
                "S_initial": r["store_before_fill"],
                "S_final": r["store_after_action"],
                "S_min": r["store_after_action"],
                "S_max": r["store_before_action"],
                "external_supply_added": 0.0,
                "controller_energy_spent": 0.0,
                "controller_starved_cycles": 0,
                "controller_action_requested_cycles": 0,
                "controller_action_allowed_cycles": 0,
                "zero_store_action_violations": 0,
                "action_without_spend_violations": 0,
                "empty_store_action_violations": 0,
                "max_accounting_residual_abs": 0.0,
                "W_resource": 0.0,
                "W_no_resource": 0.0,
                "resource_attributable_W": 0.0,
            },
        )
        s["S_final"] = r["store_after_action"]
        s["S_min"] = min(s["S_min"], r["store_after_action"], r["store_before_action"])
        s["S_max"] = max(s["S_max"], r["store_after_action"], r["store_before_action"])
        s["external_supply_added"] += SUPPLY_GAIN * r["external_supply_in"]
        s["controller_energy_spent"] += r["controller_energy_spent"]
        s["controller_starved_cycles"] += r["controller_starved"]
        s["controller_action_requested_cycles"] += r["controller_action_requested"]
        s["controller_action_allowed_cycles"] += r["controller_action_allowed"]
        if r["store_before_action"] <= EPS and r["controller_action_allowed"]:
            s["zero_store_action_violations"] += 1
        if r["controller_action_allowed"] and r["controller_energy_spent"] <= EPS:
            s["action_without_spend_violations"] += 1
        if r["store_before_action"] + EPS < r["controller_action_cost"] and r["controller_action_allowed"]:
            s["empty_store_action_violations"] += 1
        s["max_accounting_residual_abs"] = max(
            s["max_accounting_residual_abs"],
            abs(r["accounting_residual"]),
            abs(n["accounting_residual"]),
        )
        s["W_resource"] = r["W_cumulative"]
        s["W_no_resource"] = n["W_cumulative"]
        s["resource_attributable_W"] = w_attr
    return paired, list(summary.values())


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

    resource_trace: list[dict] = []
    no_resource_trace: list[dict] = []
    for condition, initial_store in CONDITIONS:
        print(f"condition={condition}", flush=True)
        resource_trace.extend(run_trajectory(grid, seeds, condition, initial_store, True, device))
        no_resource_trace.extend(run_trajectory(grid, seeds, condition, initial_store, False, device))

    cycle_rows, seed_rows = paired_rows(resource_trace, no_resource_trace)
    write_csv_atomic(out / f"{EXPERIMENT}_cycle_trace.csv", cycle_rows)
    write_csv_atomic(out / f"{EXPERIMENT}_seed_summary.csv", seed_rows)

    manifest = {
        "experiment": EXPERIMENT,
        "status": "completed",
        "grid_id": GRID_ID,
        "device": str(device),
        "gpu": torch.cuda.get_device_name(device) if device.type == "cuda" else "",
        "n_seeds": len(seeds),
        "seeds": seeds,
        "conditions": [c for c, _ in CONDITIONS],
        "n_cycles": N_CYCLES,
        "kappa": KAPPA,
        "store_capacity": STORE_CAPACITY,
        "supply_gain": SUPPLY_GAIN,
        "leak": LEAK,
        "gate_policy": "strict: controller_action_allowed iff requested and store_before_action >= action_cost",
        "cycle_rows": len(cycle_rows),
        "seed_rows": len(seed_rows),
        "wall_seconds": time.time() - t0,
        "max_zero_store_action_violations": max(r["zero_store_action_violations"] for r in seed_rows),
        "max_action_without_spend_violations": max(r["action_without_spend_violations"] for r in seed_rows),
        "max_empty_store_action_violations": max(r["empty_store_action_violations"] for r in seed_rows),
        "max_accounting_residual_abs": max(r["max_accounting_residual_abs"] for r in seed_rows),
        "claim_ceiling": "model-level finite internal store gating, not a physical energy reservoir",
    }
    (out / f"{EXPERIMENT}_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
