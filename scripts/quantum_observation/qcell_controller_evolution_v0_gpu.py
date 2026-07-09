#!/usr/bin/env python3
"""Small evolutionary search for Q-cell local controller parameters.

Observation-only.  No claim of agency, purpose, life, homeostasis, global
optimality, or quantum advantage.
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
import qcell_local_controller_causal_test_v0_gpu as lc


EXPERIMENT = "qcell_controller_evolution_v0"
PARAM_BOUNDS = {
    "gain": (0.25, 3.0),
    "leak": (0.0, 0.30),
    "downstream_bias": (0.5, 2.0),
    "ad_gate": (0.0, 2.0),
    "d_block": (0.0, 2.0),
    "max_angle_mult": (1.0, 2.5),
}
HAND_CODED = {
    "gain": 1.0,
    "leak": 0.0,
    "downstream_bias": 1.0,
    "ad_gate": 1.0,
    "d_block": 1.0,
    "max_angle_mult": 2.0,
}


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


def sample_params(rng):
    return {k: float(rng.uniform(lo, hi)) for k, (lo, hi) in PARAM_BOUNDS.items()}


def mutate_params(parent, rng, scale=0.20):
    out = {}
    for k, (lo, hi) in PARAM_BOUNDS.items():
        span = hi - lo
        v = parent[k] + rng.normal(0, scale * span)
        out[k] = float(np.clip(v, lo, hi))
    return out


def links_for_grid(grid):
    return lc.links_for_grid(grid)


def param_angles_from_parts(parts, grid, params):
    links = links_for_grid(grid)
    weights = []
    for pos, (a, b, name) in enumerate(links):
        grad = torch.relu(parts[:, a] - parts[:, b])
        w = torch.pow(grad + 1e-12, params["gain"])
        w = w + params["leak"]
        w = w * (params["downstream_bias"] ** pos)
        if name == "AD":
            w = w * params["ad_gate"] * (parts[:, b] < 0.5).to(parts.dtype)
        if b == 4:
            w = w * torch.clamp(1.0 - params["d_block"] * parts[:, b], min=0.0)
        weights.append(w)
    W = torch.stack(weights, dim=1)
    budget = grid.g_internal * len(links)
    denom = W.sum(dim=1, keepdim=True)
    fixed = torch.full_like(W, grid.g_internal)
    angles = torch.where(denom > 1e-12, W / denom.clamp_min(1e-12) * budget, fixed)
    max_angle = min(params["max_angle_mult"] * grid.g_internal, 0.8)
    angles = angles.clamp_max(max_angle)
    return angles


def run_pair(grid, seeds, params, device, controller=True):
    """Return per-seed resource/no_resource summaries for fixed or candidate."""
    out = {}
    for resource_on in (True, False):
        bits = torch.as_tensor(cpu.SYS_BITS, dtype=eng.RDTYPE, device=device)
        hamming = torch.as_tensor(cpu.HAMMING_SYS, dtype=eng.RDTYPE, device=device)
        zero = eng.t(cpu.r_state("R2_pure_0"), device)
        resource = eng.t(cpu.r_state("R3_pure_1"), device)
        rho = eng.random_products(seeds, device)
        n = len(seeds)
        links = links_for_grid(grid)
        initial_energy = eng.sys_energy(rho, bits)
        cum = {k: torch.zeros(n, dtype=eng.RDTYPE, device=device) for k in ("rin", "rout", "wout", "qnoise", "fcons")}
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
            if controller:
                angles = param_angles_from_parts(parts, grid, params)
            else:
                angles = torch.full((n, len(links)), grid.g_internal, dtype=eng.RDTYPE, device=device)
            for col, (a, b, _) in enumerate(links):
                angle = angles[:, col]
                rho = lc.apply_two_local_batched_u(rho, lc.exchange_batch(angle, device), cpu.N_SYS, a, b)
                angle_budget += angle.abs()
            full = eng.full_state(rho, zero, zero)
            fixed_out_angle = torch.full((n,), grid.theta_out_DW * grid.out_layers, dtype=eng.RDTYPE, device=device)
            full = lc.apply_two_local_batched_u(full, lc.exchange_batch(fixed_out_angle, device), cpu.N_FULL, 5, 6)
            wred = eng.trace_full_w(full)
            wout = wred[:, 1, 1].real
            rho = eng.trace_full_to_sys(full)
            rho, qnoise = eng.apply_noise(rho, "N4_dephase_plus_amplitude_damping", 0.06, hamming, bits, device, strong=False)
            end_energy = eng.sys_energy(rho, bits)
            residual = rin - ((end_energy - start_energy) + rout + wout + qnoise)
            max_res = torch.maximum(max_res, residual.abs())
            for key, val in (("rin", rin), ("rout", rout), ("wout", wout), ("qnoise", qnoise), ("fcons", fcons)):
                cum[key] += val
            if not torch.isfinite(rho).all():
                raise RuntimeError(f"non-finite state {grid.grid_id}")
        final_energy = eng.sys_energy(rho, bits)
        host = {k: v.detach().cpu().numpy() for k, v in cum.items()}
        host.update({
            "angle_budget": angle_budget.detach().cpu().numpy(),
            "max_res": max_res.detach().cpu().numpy(),
            "initial_energy": initial_energy.detach().cpu().numpy(),
            "final_energy": final_energy.detach().cpu().numpy(),
        })
        out["resource" if resource_on else "no_resource"] = host
    rows = []
    res = out["resource"]
    no = out["no_resource"]
    fixed_budget = grid.g_internal * len(links) * 200
    for ix, seed in enumerate(seeds):
        w_res = float(res["wout"][ix])
        w_no = float(no["wout"][ix])
        rows.append({
            "grid_id": grid.grid_id,
            "seed": int(seed),
            "W_resource": w_res,
            "W_no_resource": w_no,
            "resource_attributable_W": w_res - w_no,
            "net_resource_transfer": float(res["rin"][ix] - res["rout"][ix]),
            "Q_noise_cum": float(res["qnoise"][ix]),
            "resource_free_energy_consumed_cum": float(res["fcons"][ix]),
            "angle_budget": float(res["angle_budget"][ix]),
            "fixed_angle_budget": fixed_budget,
            "energy_balance_residual_max_abs": float(max(res["max_res"][ix], no["max_res"][ix])),
        })
    return rows


def evaluate_candidate(candidate_id, params, grids, seeds, device, fixed_cache):
    rows = []
    all_gain = []
    all_penalty = []
    for grid in grids:
        cand = run_pair(grid, seeds, params, device, controller=True)
        fixed = fixed_cache[grid.grid_id]
        by_seed = {r["seed"]: r for r in fixed}
        for row in cand:
            f = by_seed[row["seed"]]
            gain = row["resource_attributable_W"] - f["resource_attributable_W"]
            no_trick = (
                gain > 0
                and row["W_resource"] - f["W_resource"] <= 0
                and row["W_no_resource"] - f["W_no_resource"] < 0
            )
            budget_excess = max(0.0, row["angle_budget"] - row["fixed_angle_budget"])
            penalty = (10.0 if no_trick else 0.0) + 100.0 * budget_excess
            all_gain.append(gain)
            all_penalty.append(penalty)
            rows.append({
                "candidate_id": candidate_id,
                **{f"param_{k}": v for k, v in params.items()},
                **row,
                "fixed_resource_attributable_W": f["resource_attributable_W"],
                "gain_over_fixed": gain,
                "W_resource_delta_vs_fixed": row["W_resource"] - f["W_resource"],
                "W_no_resource_delta_vs_fixed": row["W_no_resource"] - f["W_no_resource"],
                "no_resource_trick_flag": no_trick,
                "budget_excess": budget_excess,
                "penalty": penalty,
            })
    gains = np.array(all_gain, dtype=float)
    penalties = np.array(all_penalty, dtype=float)
    score = float(np.mean(gains - penalties))
    summary = {
        "candidate_id": candidate_id,
        **{f"param_{k}": v for k, v in params.items()},
        "score": score,
        "mean_gain": float(np.mean(gains)),
        "median_gain": float(np.median(gains)),
        "n_positive_gain": int(np.sum(gains > 0)),
        "n_eval": int(len(gains)),
        "mean_penalty": float(np.mean(penalties)),
        "max_residual": float(max(r["energy_balance_residual_max_abs"] for r in rows)),
    }
    return summary, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grid-ids-file", default="data/quantum_observation/qcell_controller_evolution_v0_grid_ids.txt")
    ap.add_argument("--outdir", default=f"{EXPERIMENT}_outputs")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--population", type=int, default=24)
    ap.add_argument("--generations", type=int, default=5)
    ap.add_argument("--parents", type=int, default=6)
    ap.add_argument("--n-train-seeds", type=int, default=20)
    ap.add_argument("--n-validation-seeds", type=int, default=20)
    ap.add_argument("--n-holdout-seeds", type=int, default=60)
    ap.add_argument("--rng-seed", type=int, default=20260710)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.device.startswith("cuda") and not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable")
    if args.smoke:
        args.population = 4
        args.generations = 2
        args.parents = 2
        args.n_train_seeds = 3
        args.n_validation_seeds = 3
        args.n_holdout_seeds = 3
    device = torch.device(args.device)
    rng = np.random.default_rng(args.rng_seed)
    grids = selected_grids(args.grid_ids_file)
    train = cpu.MAIN_SEEDS[:args.n_train_seeds]
    val = cpu.MAIN_SEEDS[20:20 + args.n_validation_seeds]
    hold = cpu.MAIN_SEEDS[40:40 + args.n_holdout_seeds]
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    fixed_train = {g.grid_id: run_pair(g, train, HAND_CODED, device, controller=False) for g in grids}
    population = [{"id": "hand_coded", "params": HAND_CODED.copy(), "origin": "seed"}]
    while len(population) < args.population:
        population.append({"id": f"gen0_rand{len(population):03d}", "params": sample_params(rng), "origin": "random"})

    history = []
    detail_rows = []
    current = population
    for gen in range(args.generations):
        scored = []
        for cand in current:
            summary, rows = evaluate_candidate(cand["id"], cand["params"], grids, train, device, fixed_train)
            summary["generation"] = gen
            summary["origin"] = cand.get("origin", "")
            scored.append((summary["score"], cand, summary))
            detail_rows.extend(rows)
            history.append(summary)
        scored.sort(key=lambda x: x[0], reverse=True)
        parents = [cand for _, cand, _ in scored[:args.parents]]
        if gen == args.generations - 1:
            break
        next_pop = [{"id": p["id"], "params": p["params"], "origin": "elite"} for p in parents]
        while len(next_pop) < args.population:
            p = parents[len(next_pop) % len(parents)]
            cid = f"gen{gen+1}_mut{len(next_pop):03d}_from_{p['id']}"
            next_pop.append({"id": cid, "params": mutate_params(p["params"], rng), "origin": "mutation"})
        current = next_pop
        print(f"generation {gen} best={scored[0][2]}", flush=True)

    write_csv_atomic(out / f"{EXPERIMENT}_candidate_history.csv", history)
    write_csv_atomic(out / f"{EXPERIMENT}_train_detail_rows.csv", detail_rows)

    top = sorted(history, key=lambda r: r["score"], reverse=True)[:max(args.parents, 2)]
    fixed_val = {g.grid_id: run_pair(g, val, HAND_CODED, device, controller=False) for g in grids}
    validation = []
    validation_details = []
    for item in top:
        params = {k.replace("param_", ""): item[k] for k in item if k.startswith("param_")}
        s, rows = evaluate_candidate(item["candidate_id"], params, grids, val, device, fixed_val)
        s["stage"] = "validation"
        validation.append(s)
        validation_details.extend(rows)
    write_csv_atomic(out / f"{EXPERIMENT}_validation_summary.csv", validation)
    write_csv_atomic(out / f"{EXPERIMENT}_validation_detail_rows.csv", validation_details)

    hold_candidates = sorted(validation, key=lambda r: r["score"], reverse=True)[:2]
    hand_summary = next((r for r in history if r["candidate_id"] == "hand_coded"), None)
    if hand_summary and all(c["candidate_id"] != "hand_coded" for c in hold_candidates):
        hold_candidates.append(hand_summary)
    fixed_hold = {g.grid_id: run_pair(g, hold, HAND_CODED, device, controller=False) for g in grids}
    holdout = []
    holdout_details = []
    for item in hold_candidates:
        params = {k.replace("param_", ""): item[k] for k in item if k.startswith("param_")}
        s, rows = evaluate_candidate(item["candidate_id"], params, grids, hold, device, fixed_hold)
        s["stage"] = "holdout"
        holdout.append(s)
        holdout_details.extend(rows)
    write_csv_atomic(out / f"{EXPERIMENT}_holdout_summary.csv", holdout)
    write_csv_atomic(out / f"{EXPERIMENT}_holdout_detail_rows.csv", holdout_details)

    best = sorted(holdout, key=lambda r: r["score"], reverse=True)[0]
    best_params = {k.replace("param_", ""): best[k] for k in best if k.startswith("param_")}
    (out / f"{EXPERIMENT}_best_params.json").write_text(
        json.dumps({"candidate_id": best["candidate_id"], "params": best_params, "holdout": best}, indent=2),
        encoding="utf-8",
    )
    manifest = {
        "experiment": EXPERIMENT,
        "device": str(device),
        "gpu": torch.cuda.get_device_name(device) if device.type == "cuda" else "",
        "grids": [g.grid_id for g in grids],
        "population": args.population,
        "generations": args.generations,
        "parents": args.parents,
        "train_seeds": train,
        "validation_seeds": val,
        "holdout_seeds": hold,
        "wall_seconds": time.time() - t0,
        "switching_cost_status": "not_modeled",
    }
    (out / f"{EXPERIMENT}_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

