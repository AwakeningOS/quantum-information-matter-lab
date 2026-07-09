#!/usr/bin/env python3
"""Map internal information retained by quantum vs classical Q-cell links."""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import time
from pathlib import Path

import torch

import qcell_local_linked_energy_machine_full2q7_final_v0 as cpu
import qcell_local_linked_energy_machine_full2q7_final_v0_gpu as eng
import qcell_fixed_circuit_output_bottleneck_map_v0_gpu as fixedmap
import qcell_local_controller_causal_test_v0_gpu as lc


EXPERIMENT = "qcell_internal_information_map_v0"
GRID_ID = "QFCBM_0988"
ARMS = [
    ("quantum_keep_structure", "ring", 0.0),
    ("full_dephase_after_internal", "ring", 1.0),
    ("classical_same_graph_transport", "classical_probability_transport", 1.0),
    ("no_internal_links", "coupling_off", 0.0),
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


def cond_for(grid, variant: str) -> cpu.Condition:
    return cpu.Condition(
        GRID_ID,
        variant,
        "R3_pure_1",
        "N4_dephase_plus_amplitude_damping",
        0.06,
        grid.g_internal,
        grid.theta_in_RE,
        "none",
        "staged",
    )


def offdiag_l1(rho, device):
    mask = torch.as_tensor(cpu.OFFDIAG_SYS, dtype=torch.bool, device=device)
    return rho.abs()[:, mask].sum(dim=1).real


def diagonal_shadow(rho):
    out = torch.zeros_like(rho)
    idx = torch.arange(cpu.DIM_SYS, device=rho.device)
    out[:, idx, idx] = rho.diagonal(dim1=-2, dim2=-1)
    return out


def diag_entropy(diag):
    vals = diag.clamp_min(0)
    logs = torch.where(vals > 1e-14, torch.log2(vals), 0)
    return -(vals * logs).sum(dim=1)


def diag_l2(diag):
    return torch.sqrt((diag * diag).sum(dim=1))


def pair_observables(rho):
    vals = {}
    diag = rho.diagonal(dim1=-2, dim2=-1).real
    bits = torch.as_tensor(cpu.SYS_BITS, dtype=eng.RDTYPE, device=rho.device)
    for i, j, name in cpu.PAIR_SYS:
        mi, neg = eng.pair_metrics(rho, i, j)
        z = (1 - 2 * bits[:, i]) * (1 - 2 * bits[:, j])
        vals[f"MI_{name}"] = mi
        vals[f"neg_{name}"] = neg
        vals[f"ZZ_{name}"] = diag @ z
    return vals


def run_arm(grid, arm: str, variant: str, dephase_strength: float, seeds: list[int], resource_on: bool, device):
    cond = cond_for(grid, variant)
    n = len(seeds)
    bits = torch.as_tensor(cpu.SYS_BITS, dtype=eng.RDTYPE, device=device)
    hamming = torch.as_tensor(cpu.HAMMING_SYS, dtype=eng.RDTYPE, device=device)
    zero = eng.t(cpu.r_state("R2_pure_0"), device)
    resource = eng.t(cpu.r_state("R3_pure_1"), device)
    rho = eng.random_products(seeds, device)
    initial_energy = eng.sys_energy(rho, bits)
    out_angle = torch.full((n,), grid.theta_out_DW * grid.out_layers, dtype=eng.RDTYPE, device=device)
    cum = {k: torch.zeros(n, dtype=eng.RDTYPE, device=device) for k in ("rin", "rout", "w", "qnoise", "coh", "purity", "entropy", "diag_entropy", "diag_l2")}
    pair_cum = {f"{kind}_{name}": torch.zeros(n, dtype=eng.RDTYPE, device=device) for kind in ("MI", "neg", "ZZ") for _, _, name in cpu.PAIR_SYS}
    max_res = torch.zeros(n, dtype=eng.RDTYPE, device=device)
    checkpoints: list[dict] = []

    for cycle in range(200):
        start_energy = eng.sys_energy(rho, bits)
        rin = torch.zeros(n, dtype=eng.RDTYPE, device=device)
        rout = torch.zeros_like(rin)
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

        rho, _flows = eng.apply_internal(rho, cond, cycle, bits, device)
        if dephase_strength > 0:
            rho = rho * ((1.0 - dephase_strength) ** hamming)
        if variant == "classical_probability_transport":
            rho = diagonal_shadow(rho)

        full = eng.full_state(rho, zero, zero)
        full = lc.apply_two_local_batched_u(full, lc.exchange_batch(out_angle, device), cpu.N_FULL, 5, 6)
        w = eng.trace_full_w(full)[:, 1, 1].real
        rho = eng.trace_full_to_sys(full)
        rho, qnoise = eng.apply_noise(rho, cond.noise, cond.p, hamming, bits, device, strong=False)

        diag = rho.diagonal(dim1=-2, dim2=-1).real
        purity = torch.einsum("nij,nji->n", rho, rho).real
        entropy = eng.entropy_batch(rho)
        coh = offdiag_l1(rho, device)
        pairs = pair_observables(rho)

        end_energy = eng.sys_energy(rho, bits)
        residual = rin - ((end_energy - start_energy) + rout + w + qnoise)
        max_res = torch.maximum(max_res, residual.abs())
        for k, v in (
            ("rin", rin),
            ("rout", rout),
            ("w", w),
            ("qnoise", qnoise),
            ("coh", coh),
            ("purity", purity),
            ("entropy", entropy),
            ("diag_entropy", diag_entropy(diag)),
            ("diag_l2", diag_l2(diag)),
        ):
            cum[k] += v
        for k, v in pairs.items():
            pair_cum[k] += v

        if cycle in (49, 99, 149, 199):
            host = {k: v.detach().cpu() for k, v in {"W": w, "R_out": rout, "Q_noise": qnoise, "coherence": coh, "entropy": entropy}.items()}
            for ix, seed in enumerate(seeds):
                checkpoints.append({
                    "arm": arm,
                    "resource_on": int(resource_on),
                    "seed": int(seed),
                    "cycle": cycle + 1,
                    **{k: float(v[ix]) for k, v in host.items()},
                })

    diag = rho.diagonal(dim1=-2, dim2=-1).real
    parts = eng.part_energies(rho, bits)
    final_energy = eng.sys_energy(rho, bits)
    host = {k: v.detach().cpu().numpy() for k, v in cum.items()}
    pair_host = {k: v.detach().cpu().numpy() for k, v in pair_cum.items()}
    diag_host = diag.detach().cpu().numpy()
    parts_host = parts.detach().cpu().numpy()
    initial_host = initial_energy.detach().cpu().numpy()
    final_host = final_energy.detach().cpu().numpy()
    rows: list[dict] = []
    for ix, seed in enumerate(seeds):
        row = {
            "arm": arm,
            "variant": variant,
            "resource_on": int(resource_on),
            "seed": int(seed),
            "W": float(host["w"][ix]),
            "R_in_cum": float(host["rin"][ix]),
            "R_out_cum": float(host["rout"][ix]),
            "Q_noise_cum": float(host["qnoise"][ix]),
            "Delta_E_internal": float(final_host[ix] - initial_host[ix]),
            "final_E_total": float(final_host[ix]),
            "final_E": float(parts_host[ix, 0]),
            "final_A": float(parts_host[ix, 1]),
            "final_B": float(parts_host[ix, 2]),
            "final_C": float(parts_host[ix, 3]),
            "final_D": float(parts_host[ix, 4]),
            "mean_l1_coherence": float(host["coh"][ix] / 200),
            "mean_purity": float(host["purity"][ix] / 200),
            "mean_entropy": float(host["entropy"][ix] / 200),
            "mean_diag_entropy": float(host["diag_entropy"][ix] / 200),
            "mean_diag_l2": float(host["diag_l2"][ix] / 200),
            "max_residual": float(max_res.detach().cpu().numpy()[ix]),
        }
        for key, val in pair_host.items():
            row[f"mean_{key}"] = float(val[ix] / 200)
        for state in range(cpu.DIM_SYS):
            row[f"p_{state:05b}"] = float(diag_host[ix, state])
        rows.append(row)
    return rows, checkpoints


def mean(rows, key):
    return sum(r[key] for r in rows) / len(rows)


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

    rows: list[dict] = []
    checkpoints: list[dict] = []
    for arm, variant, dep in ARMS:
        print(f"arm={arm}", flush=True)
        res, chk = run_arm(grid, arm, variant, dep, seeds, True, device)
        no, chk_no = run_arm(grid, arm, variant, dep, seeds, False, device)
        no_by = {r["seed"]: r for r in no}
        for r in res:
            n = no_by[r["seed"]]
            rows.append({
                **r,
                "W_no_resource": n["W"],
                "resource_attributable_W": r["W"] - n["W"],
                "delta_l1_coherence": r["mean_l1_coherence"] - n["mean_l1_coherence"],
                "delta_entropy": r["mean_entropy"] - n["mean_entropy"],
                "delta_diag_entropy": r["mean_diag_entropy"] - n["mean_diag_entropy"],
                "delta_mean_MI": sum(r[f"mean_MI_{name}"] - n[f"mean_MI_{name}"] for _, _, name in cpu.PAIR_SYS) / len(cpu.PAIR_SYS),
                "delta_mean_ZZ_abs": sum(abs(r[f"mean_ZZ_{name}"] - n[f"mean_ZZ_{name}"]) for _, _, name in cpu.PAIR_SYS) / len(cpu.PAIR_SYS),
            })
        checkpoints.extend(chk)
        checkpoints.extend(chk_no)

    arm_rows: list[dict] = []
    for arm, _variant, _dep in ARMS:
        sub = [r for r in rows if r["arm"] == arm]
        arm_rows.append({
            "arm": arm,
            "n_seed": len(sub),
            "mean_resource_attributable_W": mean(sub, "resource_attributable_W"),
            "mean_R_out_cum": mean(sub, "R_out_cum"),
            "mean_Q_noise_cum": mean(sub, "Q_noise_cum"),
            "mean_Delta_E_internal": mean(sub, "Delta_E_internal"),
            "mean_final_E_total": mean(sub, "final_E_total"),
            "mean_final_E": mean(sub, "final_E"),
            "mean_final_A": mean(sub, "final_A"),
            "mean_final_B": mean(sub, "final_B"),
            "mean_final_C": mean(sub, "final_C"),
            "mean_final_D": mean(sub, "final_D"),
            "mean_l1_coherence": mean(sub, "mean_l1_coherence"),
            "mean_purity": mean(sub, "mean_purity"),
            "mean_entropy": mean(sub, "mean_entropy"),
            "mean_diag_entropy": mean(sub, "mean_diag_entropy"),
            "mean_diag_l2": mean(sub, "mean_diag_l2"),
            "delta_l1_coherence": mean(sub, "delta_l1_coherence"),
            "delta_entropy": mean(sub, "delta_entropy"),
            "delta_diag_entropy": mean(sub, "delta_diag_entropy"),
            "delta_mean_MI": mean(sub, "delta_mean_MI"),
            "delta_mean_ZZ_abs": mean(sub, "delta_mean_ZZ_abs"),
            "mean_MI": sum(mean(sub, f"mean_MI_{name}") for _, _, name in cpu.PAIR_SYS) / len(cpu.PAIR_SYS),
            "mean_negativity": sum(mean(sub, f"mean_neg_{name}") for _, _, name in cpu.PAIR_SYS) / len(cpu.PAIR_SYS),
            "mean_abs_ZZ": sum(abs(mean(sub, f"mean_ZZ_{name}")) for _, _, name in cpu.PAIR_SYS) / len(cpu.PAIR_SYS),
            "max_residual": max(r["max_residual"] for r in sub),
        })

    by_arm_seed = {(r["arm"], r["seed"]): r for r in rows}
    comparisons: list[dict] = []
    q_arm = "quantum_keep_structure"
    for other, _variant, _dep in ARMS:
        if other == q_arm:
            continue
        for seed in seeds:
            q = by_arm_seed[(q_arm, seed)]
            o = by_arm_seed[(other, seed)]
            l1 = sum(abs(o[f"p_{state:05b}"] - q[f"p_{state:05b}"]) for state in range(cpu.DIM_SYS))
            comparisons.append({
                "comparison": f"{other}_minus_{q_arm}",
                "other_arm": other,
                "seed": seed,
                "W_attr_diff": o["resource_attributable_W"] - q["resource_attributable_W"],
                "R_out_diff": o["R_out_cum"] - q["R_out_cum"],
                "Q_noise_diff": o["Q_noise_cum"] - q["Q_noise_cum"],
                "Delta_E_internal_diff": o["Delta_E_internal"] - q["Delta_E_internal"],
                "final_population_l1_distance": l1,
                "final_population_tv_distance": 0.5 * l1,
                "final_D_diff": o["final_D"] - q["final_D"],
                "coherence_diff": o["mean_l1_coherence"] - q["mean_l1_coherence"],
                "entropy_diff": o["mean_entropy"] - q["mean_entropy"],
                "diag_entropy_diff": o["mean_diag_entropy"] - q["mean_diag_entropy"],
                "mean_MI_diff": sum(o[f"mean_MI_{name}"] - q[f"mean_MI_{name}"] for _, _, name in cpu.PAIR_SYS) / len(cpu.PAIR_SYS),
                "mean_ZZ_abs_delta": sum(abs(o[f"mean_ZZ_{name}"] - q[f"mean_ZZ_{name}"]) for _, _, name in cpu.PAIR_SYS) / len(cpu.PAIR_SYS),
            })

    comparison_summary: list[dict] = []
    for comp in sorted({r["comparison"] for r in comparisons}):
        sub = [r for r in comparisons if r["comparison"] == comp]
        comparison_summary.append({
            "comparison": comp,
            "n_seed": len(sub),
            "mean_W_attr_diff": mean(sub, "W_attr_diff"),
            "mean_R_out_diff": mean(sub, "R_out_diff"),
            "mean_Q_noise_diff": mean(sub, "Q_noise_diff"),
            "mean_Delta_E_internal_diff": mean(sub, "Delta_E_internal_diff"),
            "mean_final_population_tv_distance": mean(sub, "final_population_tv_distance"),
            "mean_final_D_diff": mean(sub, "final_D_diff"),
            "mean_coherence_diff": mean(sub, "coherence_diff"),
            "mean_entropy_diff": mean(sub, "entropy_diff"),
            "mean_diag_entropy_diff": mean(sub, "diag_entropy_diff"),
            "mean_MI_diff": mean(sub, "mean_MI_diff"),
            "mean_ZZ_abs_delta": mean(sub, "mean_ZZ_abs_delta"),
        })

    write_csv_atomic(out / f"{EXPERIMENT}_seed_summary.csv", rows)
    write_csv_atomic(out / f"{EXPERIMENT}_arm_summary.csv", arm_rows)
    write_csv_atomic(out / f"{EXPERIMENT}_comparison_seed_summary.csv", comparisons)
    write_csv_atomic(out / f"{EXPERIMENT}_comparison_summary.csv", comparison_summary)
    write_csv_atomic(out / f"{EXPERIMENT}_checkpoint_trace.csv", checkpoints)

    manifest = {
        "experiment": EXPERIMENT,
        "status": "completed",
        "grid_id": GRID_ID,
        "n_seeds": len(seeds),
        "cycles": 200,
        "arms": [a for a, _, _ in ARMS],
        "wall_seconds": time.time() - t0,
        "max_residual": max(r["max_residual"] for r in arm_rows),
        "claim_ceiling": "model-level internal information map; no quantum advantage or physical energy claim",
    }
    (out / f"{EXPERIMENT}_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = ["# Q-cell internal information map v0", "", "Date: 2026-07-10 JST", "", "## Arm Readout", ""]
    for r in arm_rows:
        lines.append(
            f"- {r['arm']}: W_attr `{r['mean_resource_attributable_W']:.6f}`, R_out `{r['mean_R_out_cum']:.6f}`, Q_noise `{r['mean_Q_noise_cum']:.6f}`, coherence `{r['mean_l1_coherence']:.6f}`, entropy `{r['mean_entropy']:.6f}`, MI `{r['mean_MI']:.6f}`."
        )
    lines += ["", "## Quantum-Referenced Differences", ""]
    for r in comparison_summary:
        lines.append(
            f"- {r['comparison']}: W `{r['mean_W_attr_diff']:.6f}`, R_out `{r['mean_R_out_diff']:.6f}`, Q_noise `{r['mean_Q_noise_diff']:.6f}`, final TV `{r['mean_final_population_tv_distance']:.6f}`, coherence `{r['mean_coherence_diff']:.6f}`, MI `{r['mean_MI_diff']:.6f}`."
        )
    lines += ["", "## Claim Ceiling", "", manifest["claim_ceiling"], ""]
    (out / f"{EXPERIMENT}_report_2026-07-10.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
