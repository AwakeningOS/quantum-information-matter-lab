#!/usr/bin/env python3
"""Prototype model-level quantum-structure maintenance cost test for QFCBM_0988.

Draft status: smoke-tested only. The repair actuator is a nonunitary convex
blend toward the pre-noise state, so this runner separates physical residual
from store residual and must not be treated as a thermodynamic ledger result.
"""
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


EXPERIMENT = "qcell_quantum_structure_maintenance_cost_v0"
GRID_ID = "QFCBM_0988"
N_CYCLES = 200
STORE_CAPACITY = 1.0
SUPPLY_GAIN = 0.08
STRUCTURE_COST_RATE = 0.35
OUTPUT_COST_RATE = 0.08
REPAIR_FRACTION = 0.70
EPS = 1e-12
ARMS = [
    ("quantum_no_repair", "ring"),
    ("quantum_repair_shared_store", "ring"),
    ("quantum_repair_free", "ring"),
    ("fake_charge_no_repair", "ring"),
    ("classical_probability_transport", "classical_probability_transport"),
    ("diag_same_population_shadow", "ring"),
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


def make_cond(grid, variant: str) -> cpu.Condition:
    return cpu.Condition(
        condition_id=f"{GRID_ID}_{variant}",
        variant=variant,
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


def diagonal_shadow(rho):
    out = torch.zeros_like(rho)
    idx = torch.arange(cpu.DIM_SYS, device=rho.device)
    out[:, idx, idx] = rho.diagonal(dim1=-2, dim2=-1)
    return out


def run_arm(grid, arm: str, variant: str, seeds: list[int], resource_on: bool, device):
    cond = make_cond(grid, variant)
    bits = torch.as_tensor(cpu.SYS_BITS, dtype=eng.RDTYPE, device=device)
    hamming = torch.as_tensor(cpu.HAMMING_SYS, dtype=eng.RDTYPE, device=device)
    zero = eng.t(cpu.r_state("R2_pure_0"), device)
    resource = eng.t(cpu.r_state("R3_pure_1"), device)
    rho = eng.random_products(seeds, device)
    n = len(seeds)
    store = torch.zeros(n, dtype=eng.RDTYPE, device=device)
    cum = {k: torch.zeros(n, dtype=eng.RDTYPE, device=device) for k in (
        "rin", "rout", "wout", "qnoise", "structure_loss", "structure_repaired", "structure_cost",
        "diag_shadow_wout", "physical_residual", "store_residual",
    )}
    pre_coh = torch.zeros(n, dtype=eng.RDTYPE, device=device)
    post_noise_coh = torch.zeros(n, dtype=eng.RDTYPE, device=device)
    post_repair_coh = torch.zeros(n, dtype=eng.RDTYPE, device=device)
    pre_neg = torch.zeros(n, dtype=eng.RDTYPE, device=device)
    post_noise_neg = torch.zeros(n, dtype=eng.RDTYPE, device=device)
    post_repair_neg = torch.zeros(n, dtype=eng.RDTYPE, device=device)
    allowed_w_cycles = torch.zeros(n, dtype=eng.RDTYPE, device=device)
    max_res = torch.zeros(n, dtype=eng.RDTYPE, device=device)
    trace_rows: list[dict] = []

    for cycle in range(N_CYCLES):
        start_energy = eng.sys_energy(rho, bits)
        external_supply_in = 1.0 if resource_on else 0.0
        store_before_cycle = store.clone()
        supplied = torch.full((n,), SUPPLY_GAIN * external_supply_in, dtype=eng.RDTYPE, device=device)
        overflow = (store + supplied - STORE_CAPACITY).clamp_min(0.0)
        store = (store + supplied).clamp(0.0, STORE_CAPACITY)
        store_after_supply = store.clone()

        rin = torch.zeros(n, dtype=eng.RDTYPE, device=device)
        rout = torch.zeros_like(rin)
        if resource_on:
            rin += 1.0
            full = eng.full_state(rho, resource, zero)
            full = eng.apply_two_local(full, eng.exchange(grid.theta_in_RE, device), cpu.N_FULL, 0, 1)
            rred = eng.trace_full_r(full)
            rho = eng.trace_full_to_sys(full)
            rout += rred[:, 1, 1].real

        if arm == "diag_same_population_shadow":
            rho = diagonal_shadow(rho)

        rho, _flows = eng.apply_internal(rho, cond, cycle, bits, device)
        if arm == "classical_probability_transport":
            rho = diagonal_shadow(rho)

        rho_pre_noise = rho
        coh_pre = offdiag_l1(rho_pre_noise, device)
        neg_pre = mean_negativity(rho_pre_noise)
        rho_post_noise, qnoise = eng.apply_noise(rho_pre_noise, cond.noise, cond.p, hamming, bits, device, strong=arm in ("classical_probability_transport", "diag_same_population_shadow"))
        coh_noise = offdiag_l1(rho_post_noise, device)
        neg_noise = mean_negativity(rho_post_noise)
        structure_loss = (coh_pre - coh_noise).clamp_min(0.0)

        store_before_repair = store.clone()
        repair_fraction = torch.zeros(n, dtype=eng.RDTYPE, device=device)
        if arm in ("quantum_repair_shared_store", "quantum_repair_free"):
            target_cost = STRUCTURE_COST_RATE * REPAIR_FRACTION * structure_loss
            if arm == "quantum_repair_shared_store":
                repair_fraction = torch.where(
                    target_cost > EPS,
                    REPAIR_FRACTION * (store / target_cost).clamp(max=1.0),
                    torch.zeros_like(store),
                )
            else:
                repair_fraction = torch.full((n,), REPAIR_FRACTION, dtype=eng.RDTYPE, device=device)
        rho_repaired = (1.0 - repair_fraction)[:, None, None] * rho_post_noise + repair_fraction[:, None, None] * rho_pre_noise
        structure_repaired = (offdiag_l1(rho_repaired, device) - coh_noise).clamp_min(0.0)
        structure_cost = STRUCTURE_COST_RATE * structure_repaired
        if arm == "fake_charge_no_repair":
            structure_cost = STRUCTURE_COST_RATE * REPAIR_FRACTION * structure_loss
            structure_repaired = torch.zeros_like(structure_repaired)
            rho_repaired = rho_post_noise
        elif arm != "quantum_repair_shared_store":
            structure_cost = torch.zeros_like(structure_cost)
        structure_cost = torch.minimum(structure_cost, store)
        store = (store - structure_cost).clamp(0.0, STORE_CAPACITY)
        rho = rho_repaired
        coh_repair = offdiag_l1(rho, device)
        neg_repair = mean_negativity(rho)

        store_before_w = store.clone()
        out_angle = torch.full((n,), grid.theta_out_DW * grid.out_layers, dtype=eng.RDTYPE, device=device)
        output_cost = OUTPUT_COST_RATE * out_angle.abs()
        w_scale = torch.where(output_cost > EPS, (store / output_cost).clamp(max=1.0), torch.ones_like(store))
        if arm in ("quantum_repair_free",):
            w_scale = torch.ones_like(w_scale)
        full = eng.full_state(rho, zero, zero)
        full = lc.apply_two_local_batched_u(full, lc.exchange_batch(out_angle * w_scale, device), cpu.N_FULL, 5, 6)
        wred = eng.trace_full_w(full)
        wout = wred[:, 1, 1].real
        rho = eng.trace_full_to_sys(full)
        output_spend = output_cost * w_scale
        store = (store - output_spend).clamp(0.0, STORE_CAPACITY)
        allowed_w_cycles += (w_scale > EPS).to(eng.RDTYPE)

        diag_rho = diagonal_shadow(rho_repaired)
        diag_full = eng.full_state(diag_rho, zero, zero)
        diag_full = lc.apply_two_local_batched_u(diag_full, lc.exchange_batch(out_angle, device), cpu.N_FULL, 5, 6)
        diag_wout = eng.trace_full_w(diag_full)[:, 1, 1].real

        end_energy = eng.sys_energy(rho, bits)
        physical_residual = rin - ((end_energy - start_energy) + rout + wout + qnoise)
        store_residual = store_before_cycle + supplied - overflow - structure_cost - output_spend - store
        max_res = torch.maximum(max_res, torch.maximum(physical_residual.abs(), store_residual.abs()))
        for key, value in (
            ("rin", rin), ("rout", rout), ("wout", wout), ("qnoise", qnoise),
            ("structure_loss", structure_loss), ("structure_repaired", structure_repaired),
            ("structure_cost", structure_cost), ("diag_shadow_wout", diag_wout),
            ("physical_residual", physical_residual.abs()), ("store_residual", store_residual.abs()),
        ):
            cum[key] += value
        pre_coh += coh_pre
        post_noise_coh += coh_noise
        post_repair_coh += coh_repair
        pre_neg += neg_pre
        post_noise_neg += neg_noise
        post_repair_neg += neg_repair

        if cycle in (0, 49, 99, 149, 199):
            host = {k: v.detach().cpu() for k, v in {
                "store_before_cycle": store_before_cycle, "store_after_supply": store_after_supply,
                "store_before_repair": store_before_repair, "store_before_w": store_before_w,
                "store_after_w": store, "coh_pre": coh_pre, "coh_noise": coh_noise,
                "coh_repair": coh_repair, "neg_pre": neg_pre, "neg_noise": neg_noise,
                "neg_repair": neg_repair, "structure_loss": structure_loss,
                "structure_repaired": structure_repaired, "structure_cost": structure_cost,
                "wout": wout, "diag_wout": diag_wout, "physical_residual": physical_residual,
                "store_residual": store_residual,
            }.items()}
            for ix, seed in enumerate(seeds):
                trace_rows.append({
                    "arm": arm, "resource_on": int(resource_on), "seed": int(seed), "cycle": cycle + 1,
                    **{k: float(v[ix]) for k, v in host.items()},
                })

    host = {k: v.detach().cpu().numpy() for k, v in cum.items()}
    rows = []
    for ix, seed in enumerate(seeds):
        rows.append({
            "arm": arm,
            "variant": variant,
            "resource_on": int(resource_on),
            "seed": int(seed),
            "W_cum": float(host["wout"][ix]),
            "diag_shadow_W_cum": float(host["diag_shadow_wout"][ix]),
            "R_in_cum": float(host["rin"][ix]),
            "R_out_cum": float(host["rout"][ix]),
            "Q_noise_cum": float(host["qnoise"][ix]),
            "structure_loss_cum": float(host["structure_loss"][ix]),
            "structure_repaired_cum": float(host["structure_repaired"][ix]),
            "structure_cost_cum": float(host["structure_cost"][ix]),
            "mean_coherence_pre_noise": float((pre_coh / N_CYCLES).detach().cpu().numpy()[ix]),
            "mean_coherence_post_noise": float((post_noise_coh / N_CYCLES).detach().cpu().numpy()[ix]),
            "mean_coherence_post_repair": float((post_repair_coh / N_CYCLES).detach().cpu().numpy()[ix]),
            "mean_negativity_pre_noise": float((pre_neg / N_CYCLES).detach().cpu().numpy()[ix]),
            "mean_negativity_post_noise": float((post_noise_neg / N_CYCLES).detach().cpu().numpy()[ix]),
            "mean_negativity_post_repair": float((post_repair_neg / N_CYCLES).detach().cpu().numpy()[ix]),
            "allowed_w_cycles": float(allowed_w_cycles.detach().cpu().numpy()[ix]),
            "store_final": float(store.detach().cpu().numpy()[ix]),
            "physical_residual_max_abs": float(host["physical_residual"][ix]),
            "store_residual_max_abs": float(host["store_residual"][ix]),
            "max_residual": float(max_res.detach().cpu().numpy()[ix]),
        })
    return rows, trace_rows


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
    traces = []
    for arm, variant in ARMS:
        print(f"arm={arm}", flush=True)
        res, rt = run_arm(grid, arm, variant, seeds, True, device)
        no, nt = run_arm(grid, arm, variant, seeds, False, device)
        no_by_seed = {r["seed"]: r for r in no}
        for r in res:
            n = no_by_seed[r["seed"]]
            rows.append({
                **r,
                "W_no_resource": n["W_cum"],
                "resource_attributable_W": r["W_cum"] - n["W_cum"],
                "diag_shadow_resource_attributable_W": r["diag_shadow_W_cum"] - n["diag_shadow_W_cum"],
            })
        traces.extend(rt)
        traces.extend(nt)

    arm_rows = []
    for arm, _variant in ARMS:
        sub = [r for r in rows if r["arm"] == arm]
        arm_rows.append({
            "arm": arm,
            "n_seed": len(sub),
            "mean_resource_attributable_W": sum(r["resource_attributable_W"] for r in sub) / len(sub),
            "mean_diag_shadow_resource_attributable_W": sum(r["diag_shadow_resource_attributable_W"] for r in sub) / len(sub),
            "mean_structure_loss": sum(r["structure_loss_cum"] for r in sub) / len(sub),
            "mean_structure_repaired": sum(r["structure_repaired_cum"] for r in sub) / len(sub),
            "mean_structure_cost": sum(r["structure_cost_cum"] for r in sub) / len(sub),
            "mean_coherence_post_noise": sum(r["mean_coherence_post_noise"] for r in sub) / len(sub),
            "mean_coherence_post_repair": sum(r["mean_coherence_post_repair"] for r in sub) / len(sub),
            "mean_negativity_post_noise": sum(r["mean_negativity_post_noise"] for r in sub) / len(sub),
            "mean_negativity_post_repair": sum(r["mean_negativity_post_repair"] for r in sub) / len(sub),
            "mean_allowed_w_cycles": sum(r["allowed_w_cycles"] for r in sub) / len(sub),
            "mean_store_final": sum(r["store_final"] for r in sub) / len(sub),
            "max_physical_residual": max(r["physical_residual_max_abs"] for r in sub),
            "max_store_residual": max(r["store_residual_max_abs"] for r in sub),
            "max_residual": max(r["max_residual"] for r in sub),
        })
    write_csv_atomic(out / f"{EXPERIMENT}_seed_summary.csv", rows)
    write_csv_atomic(out / f"{EXPERIMENT}_arm_summary.csv", arm_rows)
    write_csv_atomic(out / f"{EXPERIMENT}_checkpoint_trace.csv", traces)
    manifest = {
        "experiment": EXPERIMENT,
        "status": "completed",
        "grid_id": GRID_ID,
        "n_seeds": len(seeds),
        "cycles": N_CYCLES,
        "arms": [a for a, _ in ARMS],
        "store_capacity": STORE_CAPACITY,
        "supply_gain": SUPPLY_GAIN,
        "structure_cost_rate": STRUCTURE_COST_RATE,
        "output_cost_rate": OUTPUT_COST_RATE,
        "repair_fraction": REPAIR_FRACTION,
        "seed_rows": len(rows),
        "wall_seconds": time.time() - t0,
        "max_residual": max(r["max_residual"] for r in arm_rows),
    }
    (out / f"{EXPERIMENT}_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# Q-cell quantum structure maintenance cost v0", "", "Date: 2026-07-10 JST", "", "## Readout", ""]
    for r in arm_rows:
        lines.append(
            f"- {r['arm']}: W_attr `{r['mean_resource_attributable_W']:.6f}`, repaired `{r['mean_structure_repaired']:.6f}`, cost `{r['mean_structure_cost']:.6f}`, coherence post-noise/repair `{r['mean_coherence_post_noise']:.6f}`/`{r['mean_coherence_post_repair']:.6f}`."
        )
    lines.extend(["", "## Claim Ceiling", "", "Model-level shared-store accounting only; not physical thermodynamic proof.", ""])
    (out / f"{EXPERIMENT}_report_2026-07-10.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
