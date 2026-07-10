#!/usr/bin/env python3
"""Delayed-use stored-power test: fill early, spend later."""
from __future__ import annotations

import argparse
import csv
import json
import os
import time
from pathlib import Path

import torch

import qcell_stored_power_actuator_v0_gpu as base


EXPERIMENT = "qcell_stored_power_delayed_use_v0"
ACTION_START = 120
CONDITIONS = [
    ("no_supply_late_action", "none", 0.0),
    ("early_supply_late_action", "early", 0.0),
    ("late_supply_late_action", "late", 0.0),
    ("continuous_supply_late_action", "continuous", 0.0),
    ("initial_store_late_action", "none", 1.0),
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


def supply_for(kind: str, cycle: int) -> float:
    if kind == "early":
        return 1.0 if cycle < 80 else 0.0
    if kind == "late":
        return 1.0 if cycle >= ACTION_START else 0.0
    if kind == "continuous":
        return 0.4
    return 0.0


def run_trajectory(grid, seeds, condition: str, supply_kind: str, initial_store: float, resource_on: bool, device):
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
        external_supply_in = supply_for(supply_kind, cycle) if resource_on else 0.0
        store_before_fill = store.clone()
        store_before_action = (store + base.SUPPLY_GAIN * external_supply_in).clamp(0.0, base.STORE_CAPACITY)
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
        action_window_open = cycle >= ACTION_START
        action_allowed = action_requested & action_window_open & (store_before_action + base.EPS >= action_cost)
        angles = torch.where(action_allowed[:, None], intended, torch.zeros_like(intended))
        spent = torch.where(action_allowed, action_cost, torch.zeros_like(action_cost))
        starved = action_requested & action_window_open & (~action_allowed)
        blocked_before_window = action_requested & (not action_window_open)
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
            "blocked_before_window": blocked_before_window,
            "wout": wout,
            "cum_w": cumulative_w,
            "residual": residual,
        }.items()}
        for ix, seed in enumerate(seeds):
            trace.append({
                "t": cycle,
                "seed": int(seed),
                "condition": condition,
                "resource_on": int(resource_on),
                "supply_on": int(external_supply_in > 0),
                "external_supply_in": external_supply_in,
                "action_window_open": int(action_window_open),
                "store_before_fill": float(host["store_before_fill"][ix]),
                "store_before_action": float(host["store_before_action"][ix]),
                "controller_action_requested": int(bool(host["action_requested"][ix])),
                "controller_action_allowed": int(bool(host["action_allowed"][ix])),
                "controller_blocked_before_window": int(bool(host["blocked_before_window"][ix])),
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


def summarize(seed_rows: list[dict], cycle_rows: list[dict]) -> list[dict]:
    cycle_by = {}
    for r in cycle_rows:
        cycle_by.setdefault((r["condition"], r["seed"]), []).append(r)
    out = []
    by = {}
    for r in seed_rows:
        by.setdefault(r["condition"], []).append(r)
    for condition, rows in by.items():
        late_w = []
        for r in rows:
            c = cycle_by[(condition, r["seed"])]
            late_w.append(sum(x["resource_attributable_W_cycle"] for x in c if x["t"] >= ACTION_START))
        out.append({
            "condition": condition,
            "n_seed": len(rows),
            "mean_W_attr": sum(float(r["resource_attributable_W"]) for r in rows) / len(rows),
            "mean_late_W_attr": sum(late_w) / len(late_w),
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

    resource_trace = []
    no_resource_trace = []
    for condition, supply_kind, initial_store in CONDITIONS:
        print(f"condition={condition}", flush=True)
        resource_trace.extend(run_trajectory(grid, seeds, condition, supply_kind, initial_store, True, device))
        no_resource_trace.extend(run_trajectory(grid, seeds, condition, supply_kind, initial_store, False, device))
    cycle_rows, seed_rows = base.paired_rows(resource_trace, no_resource_trace)
    condition_rows = summarize(seed_rows, cycle_rows)
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
        "conditions": [c[0] for c in CONDITIONS],
        "action_start": ACTION_START,
        "cycle_rows": len(cycle_rows),
        "seed_rows": len(seed_rows),
        "wall_seconds": time.time() - t0,
        "max_zero_store_action_violations": max(r["max_zero_store_action_violations"] for r in condition_rows),
        "max_action_without_spend_violations": max(r["max_action_without_spend_violations"] for r in condition_rows),
        "max_empty_store_action_violations": max(r["max_empty_store_action_violations"] for r in condition_rows),
        "max_accounting_residual_abs": max(r["max_residual"] for r in condition_rows),
    }
    (out / f"{EXPERIMENT}_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# Q-cell stored-power delayed-use v0", "", "Date: 2026-07-10 JST", "", "## Readout", ""]
    for r in condition_rows:
        lines.append(
            f"- {r['condition']}: W_attr `{r['mean_W_attr']:.6f}`, late W_attr `{r['mean_late_W_attr']:.6f}`, allowed `{r['mean_allowed']:.2f}`, final store `{r['mean_S_final']:.6f}`."
        )
    lines.extend(["", "## Claim Ceiling", "", "This tests whether stored budget can be held while action is blocked, then spent later. It remains a model-level store test, not physical energy storage.", ""])
    (out / f"{EXPERIMENT}_report_2026-07-10.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
