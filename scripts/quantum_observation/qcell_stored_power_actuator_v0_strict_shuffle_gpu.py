#!/usr/bin/env python3
"""Strict trajectory-matched store-shuffle control for stored-power actuator v0."""
from __future__ import annotations

import argparse
import csv
import json
import os
import time
from pathlib import Path

import torch

import qcell_stored_power_actuator_v0_gpu as base


EXPERIMENT = "qcell_stored_power_actuator_v0_strict_shuffle"
SOURCE_CONDITION = "supply_restart_after_stop_initial_zero"


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


def build_store_schedule(trace: list[dict], seeds: list[int], mode: str) -> dict[tuple[int, int], float]:
    by_seed = {seed: [] for seed in seeds}
    for row in trace:
        by_seed[int(row["seed"])].append(float(row["store_before_action"]))
    schedule: dict[tuple[int, int], float] = {}
    for seed in seeds:
        values = by_seed[seed]
        if len(values) != base.N_CYCLES:
            raise RuntimeError(f"bad trace length for seed {seed}: {len(values)}")
        if mode == "reverse":
            shuffled = list(reversed(values))
        elif mode == "roll_73":
            shuffled = values[73:] + values[:73]
        elif mode == "block_swap":
            shuffled = values[120:200] + values[60:120] + values[0:60]
        else:
            raise RuntimeError(mode)
        for t, value in enumerate(shuffled):
            schedule[(seed, t)] = value
    return schedule


def run_forced_store(grid, seeds, label: str, schedule: dict[tuple[int, int], float], resource_on: bool, device):
    bits = torch.as_tensor(base.cpu.SYS_BITS, dtype=base.eng.RDTYPE, device=device)
    hamming = torch.as_tensor(base.cpu.HAMMING_SYS, dtype=base.eng.RDTYPE, device=device)
    zero = base.eng.t(base.cpu.r_state("R2_pure_0"), device)
    resource = base.eng.t(base.cpu.r_state("R3_pure_1"), device)
    rho = base.eng.random_products(seeds, device)
    links = base.evo.links_for_grid(grid)
    n = len(seeds)
    cumulative_w = torch.zeros(n, dtype=base.eng.RDTYPE, device=device)
    trace: list[dict] = []

    for cycle in range(base.N_CYCLES):
        start_energy = base.eng.sys_energy(rho, bits)
        external_supply_in = base.supply_for(SOURCE_CONDITION, cycle) if resource_on else 0.0
        store_before_action = torch.tensor(
            [schedule[(int(seed), cycle)] for seed in seeds],
            dtype=base.eng.RDTYPE,
            device=device,
        )

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
        angles = torch.where(action_allowed[:, None], intended, torch.zeros_like(intended))
        spent = torch.where(action_allowed, action_cost, torch.zeros_like(action_cost))
        starved = action_requested & (~action_allowed)
        store_after_action = (store_before_action - spent - base.LEAK).clamp(0.0, base.STORE_CAPACITY)

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
                "resource_on": int(resource_on),
                "supply_on": int(external_supply_in > 0),
                "external_supply_in": external_supply_in,
                "store_before_fill": float(host["store_before_action"][ix]),
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


def summarize(seed_rows: list[dict]) -> list[dict]:
    out = []
    by_condition: dict[str, list[dict]] = {}
    for row in seed_rows:
        by_condition.setdefault(row["condition"], []).append(row)
    for condition, rows in by_condition.items():
        out.append({
            "condition": condition,
            "n_seed": len(rows),
            "mean_W_attr": sum(float(r["resource_attributable_W"]) for r in rows) / len(rows),
            "mean_allowed": sum(float(r["controller_action_allowed_cycles"]) for r in rows) / len(rows),
            "mean_starved": sum(float(r["controller_starved_cycles"]) for r in rows) / len(rows),
            "mean_spent": sum(float(r["controller_energy_spent"]) for r in rows) / len(rows),
            "mean_S_final": sum(float(r["S_final"]) for r in rows) / len(rows),
            "max_zero_store_action_violations": max(int(r["zero_store_action_violations"]) for r in rows),
            "max_action_without_spend_violations": max(int(r["action_without_spend_violations"]) for r in rows),
            "max_empty_store_action_violations": max(int(r["empty_store_action_violations"]) for r in rows),
            "max_residual": max(float(r["max_accounting_residual_abs"]) for r in rows),
        })
    return out


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

    real_resource = base.run_trajectory(grid, seeds, SOURCE_CONDITION, 0.0, True, device)
    real_no = base.run_trajectory(grid, seeds, SOURCE_CONDITION, 0.0, False, device)
    cycle_rows, seed_rows = base.paired_rows(real_resource, real_no)
    for mode in ("reverse", "roll_73", "block_swap"):
        print(f"strict_shuffle={mode}", flush=True)
        schedule = build_store_schedule(real_resource, seeds, mode)
        res = run_forced_store(grid, seeds, f"strict_shuffle_{mode}", schedule, True, device)
        no = run_forced_store(grid, seeds, f"strict_shuffle_{mode}", schedule, False, device)
        c, s = base.paired_rows(res, no)
        cycle_rows.extend(c)
        seed_rows.extend(s)

    condition_rows = summarize(seed_rows)
    write_csv_atomic(out / f"{EXPERIMENT}_condition_summary.csv", condition_rows)
    write_csv_atomic(out / f"{EXPERIMENT}_seed_summary.csv", seed_rows)
    write_csv_atomic(out / f"{EXPERIMENT}_cycle_trace.csv", cycle_rows)
    manifest = {
        "experiment": EXPERIMENT,
        "status": "completed",
        "grid_id": base.GRID_ID,
        "device": str(device),
        "gpu": torch.cuda.get_device_name(device) if device.type == "cuda" else "",
        "n_seeds": len(seeds),
        "conditions": [r["condition"] for r in condition_rows],
        "n_cycles": base.N_CYCLES,
        "cycle_rows": len(cycle_rows),
        "seed_rows": len(seed_rows),
        "wall_seconds": time.time() - t0,
        "max_zero_store_action_violations": max(r["max_zero_store_action_violations"] for r in condition_rows),
        "max_action_without_spend_violations": max(r["max_action_without_spend_violations"] for r in condition_rows),
        "max_empty_store_action_violations": max(r["max_empty_store_action_violations"] for r in condition_rows),
        "max_accounting_residual_abs": max(r["max_residual"] for r in condition_rows),
    }
    (out / f"{EXPERIMENT}_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    report_lines = [
        "# Q-cell stored-power actuator v0 strict shuffle",
        "",
        "Date: 2026-07-10 JST",
        "",
        "## Readout",
        "",
    ]
    for row in condition_rows:
        report_lines.append(
            f"- {row['condition']}: W_attr `{row['mean_W_attr']:.6f}`, allowed `{row['mean_allowed']:.2f}`, starved `{row['mean_starved']:.2f}`."
        )
    report_lines.extend([
        "",
        "## Claim Ceiling",
        "",
        "This is a trajectory-matched time-shuffle control. It tests whether the same store values still work when their timing is broken.",
        "",
    ])
    (out / f"{EXPERIMENT}_report_2026-07-10.md").write_text("\n".join(report_lines), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
