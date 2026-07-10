#!/usr/bin/env python3
"""QFCBM_0988 classical-vs-quantum coupling comparison."""
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


EXPERIMENT = "qcell_classical_vs_quantum_coupling_v0"
GRID_ID = "QFCBM_0988"
ARMS = [
    ("quantum_direct", "ring"),
    ("quantum_no_internal_links", "coupling_off"),
    ("quantum_post_internal_dephased", "strong_dephase"),
    ("quantum_dephase_after_each_link", "dephase_each_link"),
    ("classical_probability_transport", "classical_probability_transport"),
    ("central_upper_quantum", "central_control"),
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


def make_cond(grid, arm: str, variant: str) -> cpu.Condition:
    cond_variant = "ring" if variant == "dephase_each_link" else variant
    return cpu.Condition(
        condition_id=f"{GRID_ID}_{arm}",
        variant=cond_variant,
        resource="R3_pure_1",
        noise="N4_dephase_plus_amplitude_damping",
        p=0.06,
        g=grid.g_internal,
        theta=grid.theta_in_RE,
        fault="none",
        schedule="staged",
        note="qcell classical-vs-quantum coupling comparison",
    )


def run_arm(grid, arm: str, variant: str, seeds: list[int], resource_on: bool, device):
    cond = make_cond(grid, arm, variant)
    bits = torch.as_tensor(cpu.SYS_BITS, dtype=eng.RDTYPE, device=device)
    hamming = torch.as_tensor(cpu.HAMMING_SYS, dtype=eng.RDTYPE, device=device)
    zero = eng.t(cpu.r_state("R2_pure_0"), device)
    resource = eng.t(cpu.r_state("R3_pure_1"), device)
    rho = eng.random_products(seeds, device)
    n = len(seeds)
    cum = {k: torch.zeros(n, dtype=eng.RDTYPE, device=device) for k in ("rin", "rout", "wout", "qnoise")}
    neg_int = {name: torch.zeros(n, dtype=eng.RDTYPE, device=device) for _, _, name in cpu.PAIR_SYS}
    mi_int = {name: torch.zeros(n, dtype=eng.RDTYPE, device=device) for _, _, name in cpu.PAIR_SYS}
    coh_int = torch.zeros(n, dtype=eng.RDTYPE, device=device)
    max_res = torch.zeros(n, dtype=eng.RDTYPE, device=device)
    cycle_rows: list[dict] = []
    max_trace_error = torch.zeros(n, dtype=eng.RDTYPE, device=device)
    max_hermiticity_error = torch.zeros(n, dtype=eng.RDTYPE, device=device)
    min_eigenvalue = torch.full((n,), float("inf"), dtype=eng.RDTYPE, device=device)
    nan_count = torch.zeros(n, dtype=eng.RDTYPE, device=device)

    for cycle in range(200):
        start_energy = eng.sys_energy(rho, bits)
        interact, _, mult = cpu.resource_for_cycle("R3_pure_1", cycle, "staged")
        if not resource_on:
            interact, mult = False, 0
        rin = torch.zeros(n, dtype=eng.RDTYPE, device=device)
        rout = torch.zeros_like(rin)
        if interact:
            for _ in range(mult):
                rin += 1.0
                full = eng.full_state(rho, resource, zero)
                full = eng.apply_two_local(full, eng.exchange(grid.theta_in_RE, device), cpu.N_FULL, 0, 1)
                rred = eng.trace_full_r(full)
                rho = eng.trace_full_to_sys(full)
                rout += rred[:, 1, 1].real

        if variant == "dephase_each_link":
            for a, b, angle, _name in cpu.links(cond, cycle):
                rho = eng.apply_two_local(rho, eng.exchange(angle, device), cpu.N_SYS, a, b)
                rho = rho * (0.0 ** hamming)
        else:
            rho, _flows = eng.apply_internal(rho, cond, cycle, bits, device)
        if variant == "strong_dephase":
            rho = rho * (0.0 ** hamming)

        full = eng.full_state(rho, zero, zero)
        out_angle = torch.full((n,), grid.theta_out_DW * grid.out_layers, dtype=eng.RDTYPE, device=device)
        full = lc.apply_two_local_batched_u(full, lc.exchange_batch(out_angle, device), cpu.N_FULL, 5, 6)
        wred = eng.trace_full_w(full)
        wout = wred[:, 1, 1].real
        rho = eng.trace_full_to_sys(full)

        rho, qnoise = eng.apply_noise(
            rho,
            cond.noise,
            cond.p,
            hamming,
            bits,
            device,
            strong=variant in ("strong_dephase", "classical_probability_transport"),
        )
        end_energy = eng.sys_energy(rho, bits)
        residual = rin - ((end_energy - start_energy) + rout + wout + qnoise)
        max_res = torch.maximum(max_res, residual.abs())
        cum["rin"] += rin
        cum["rout"] += rout
        cum["wout"] += wout
        cum["qnoise"] += qnoise

        diag = rho.diagonal(dim1=-2, dim2=-1).real
        coh = rho.abs().sum(dim=(1, 2)) - diag.abs().sum(dim=1)
        coh_int += coh
        neg_vals = {}
        mi_vals = {}
        for i, j, name in cpu.PAIR_SYS:
            mi, neg = eng.pair_metrics(rho, i, j)
            neg_int[name] += neg
            mi_int[name] += mi
            neg_vals[f"neg_{name}"] = neg
            mi_vals[f"MI_{name}"] = mi

        if cycle in (0, 49, 74, 124, 149, 199):
            host = {
                "wout": wout.detach().cpu(),
                "coh": coh.detach().cpu(),
                "residual": residual.detach().cpu(),
                **{k: v.detach().cpu() for k, v in neg_vals.items()},
            }
            for ix, seed in enumerate(seeds):
                cycle_rows.append({
                    "arm": arm,
                    "variant": variant,
                    "resource_on": int(resource_on),
                    "seed": int(seed),
                    "cycle": cycle + 1,
                    "W_cycle": float(host["wout"][ix]),
                    "l1_coherence": float(host["coh"][ix]),
                    "neg_EA": float(host["neg_EA"][ix]),
                    "neg_AB": float(host["neg_AB"][ix]),
                    "neg_BC": float(host["neg_BC"][ix]),
                    "neg_CD": float(host["neg_CD"][ix]),
                    "neg_AD": float(host["neg_AD"][ix]),
                    "accounting_residual": float(host["residual"][ix]),
                })

        tr = rho.diagonal(dim1=-2, dim2=-1).sum(-1).real
        max_trace_error = torch.maximum(max_trace_error, (tr - 1.0).abs())
        herm = (rho - rho.mH).abs().amax(dim=(1, 2))
        max_hermiticity_error = torch.maximum(max_hermiticity_error, herm.real)
        eig = torch.linalg.eigvalsh((rho + rho.mH) * 0.5).real
        min_eigenvalue = torch.minimum(min_eigenvalue, eig.min(dim=1).values)
        nan_count += (~torch.isfinite(rho)).reshape(n, -1).any(dim=1).to(eng.RDTYPE)

    host = {k: v.detach().cpu().numpy() for k, v in cum.items()}
    neg_host = {k: (v / 200).detach().cpu().numpy() for k, v in neg_int.items()}
    mi_host = {k: (v / 200).detach().cpu().numpy() for k, v in mi_int.items()}
    coh_host = (coh_int / 200).detach().cpu().numpy()
    res_host = max_res.detach().cpu().numpy()
    trace_host = max_trace_error.detach().cpu().numpy()
    herm_host = max_hermiticity_error.detach().cpu().numpy()
    mineig_host = min_eigenvalue.detach().cpu().numpy()
    nan_host = nan_count.detach().cpu().numpy()
    rows = []
    for ix, seed in enumerate(seeds):
        rows.append({
            "arm": arm,
            "variant": variant,
            "resource_on": int(resource_on),
            "seed": int(seed),
            "W_cum": float(host["wout"][ix]),
            "R_in_cum": float(host["rin"][ix]),
            "R_out_cum": float(host["rout"][ix]),
            "Q_noise_cum": float(host["qnoise"][ix]),
            "mean_l1_coherence": float(coh_host[ix]),
            "mean_link_negativity": float(sum(neg_host[name][ix] for _, _, name in cpu.PAIR_SYS) / len(cpu.PAIR_SYS)),
            "mean_link_MI": float(sum(mi_host[name][ix] for _, _, name in cpu.PAIR_SYS) / len(cpu.PAIR_SYS)),
            "mean_neg_EA": float(neg_host["EA"][ix]),
            "mean_neg_AB": float(neg_host["AB"][ix]),
            "mean_neg_BC": float(neg_host["BC"][ix]),
            "mean_neg_CD": float(neg_host["CD"][ix]),
            "mean_neg_AD": float(neg_host["AD"][ix]),
            "energy_balance_residual_max_abs": float(res_host[ix]),
            "trace_error_max": float(trace_host[ix]),
            "hermiticity_error_max": float(herm_host[ix]),
            "min_eigenvalue_min": float(mineig_host[ix]),
            "nan_count": int(nan_host[ix]),
        })
    return rows, cycle_rows


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
    cycle_rows = []
    for arm, variant in ARMS:
        print(f"arm={arm}", flush=True)
        res_rows, res_cycles = run_arm(grid, arm, variant, seeds, True, device)
        no_rows, no_cycles = run_arm(grid, arm, variant, seeds, False, device)
        no_by_seed = {r["seed"]: r for r in no_rows}
        for r in res_rows:
            no = no_by_seed[r["seed"]]
            rows.append({
                **r,
                "W_no_resource": no["W_cum"],
                "resource_attributable_W": r["W_cum"] - no["W_cum"],
                "mean_link_negativity_no_resource": no["mean_link_negativity"],
                "delta_link_negativity": r["mean_link_negativity"] - no["mean_link_negativity"],
                "mean_link_MI_no_resource": no["mean_link_MI"],
                "delta_link_MI": r["mean_link_MI"] - no["mean_link_MI"],
                "mean_l1_coherence_no_resource": no["mean_l1_coherence"],
                "delta_l1_coherence": r["mean_l1_coherence"] - no["mean_l1_coherence"],
            })
        cycle_rows.extend(res_cycles)
        cycle_rows.extend(no_cycles)

    write_csv_atomic(out / f"{EXPERIMENT}_seed_summary.csv", rows)
    write_csv_atomic(out / f"{EXPERIMENT}_checkpoint_trace.csv", cycle_rows)

    arm_rows = []
    for arm, _variant in ARMS:
        sub = [r for r in rows if r["arm"] == arm]
        vals = sorted(r["resource_attributable_W"] for r in sub)
        mean = sum(vals) / len(vals)
        std = (sum((x - mean) ** 2 for x in vals) / (len(vals) - 1)) ** 0.5
        ci = 1.96 * std / (len(vals) ** 0.5)
        arm_rows.append({
            "arm": arm,
            "n_seed": len(sub),
            "mean_W_resource": sum(r["W_cum"] for r in sub) / len(sub),
            "mean_W_no_resource": sum(r["W_no_resource"] for r in sub) / len(sub),
            "mean_resource_attributable_W": mean,
            "std_resource_attributable_W": std,
            "median_resource_attributable_W": vals[len(vals) // 2],
            "ci95_low_resource_attributable_W": mean - ci,
            "ci95_high_resource_attributable_W": mean + ci,
            "seed_win_count_resource_gt_no_resource": sum(1 for r in sub if r["resource_attributable_W"] > 0),
            "min_resource_attributable_W": min(vals),
            "max_resource_attributable_W": max(vals),
            "mean_link_negativity": sum(r["mean_link_negativity"] for r in sub) / len(sub),
            "mean_link_negativity_no_resource": sum(r["mean_link_negativity_no_resource"] for r in sub) / len(sub),
            "delta_link_negativity": sum(r["delta_link_negativity"] for r in sub) / len(sub),
            "mean_link_MI": sum(r["mean_link_MI"] for r in sub) / len(sub),
            "mean_link_MI_no_resource": sum(r["mean_link_MI_no_resource"] for r in sub) / len(sub),
            "delta_link_MI": sum(r["delta_link_MI"] for r in sub) / len(sub),
            "mean_l1_coherence": sum(r["mean_l1_coherence"] for r in sub) / len(sub),
            "mean_l1_coherence_no_resource": sum(r["mean_l1_coherence_no_resource"] for r in sub) / len(sub),
            "delta_l1_coherence": sum(r["delta_l1_coherence"] for r in sub) / len(sub),
            "max_residual": max(r["energy_balance_residual_max_abs"] for r in sub),
            "trace_error_max": max(r["trace_error_max"] for r in sub),
            "hermiticity_error_max": max(r["hermiticity_error_max"] for r in sub),
            "min_eigenvalue_min": min(r["min_eigenvalue_min"] for r in sub),
            "nan_count": sum(r["nan_count"] for r in sub),
        })
    write_csv_atomic(out / f"{EXPERIMENT}_arm_summary.csv", arm_rows)

    manifest = {
        "experiment": EXPERIMENT,
        "status": "completed",
        "grid_id": GRID_ID,
        "device": str(device),
        "gpu": torch.cuda.get_device_name(device) if device.type == "cuda" else "",
        "n_seeds": len(seeds),
        "arms": [a for a, _ in ARMS],
        "seed_rows": len(rows),
        "checkpoint_rows": len(cycle_rows),
        "wall_seconds": time.time() - t0,
        "max_residual": max(r["max_residual"] for r in arm_rows),
        "claim_ceiling": "comparison of modeled quantum links, dephased links, no links, classical probability transport, and central upper bound; no quantum advantage claim",
    }
    (out / f"{EXPERIMENT}_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = ["# Q-cell classical vs quantum coupling v0", "", "Date: 2026-07-10 JST", "", "## Readout", ""]
    for r in arm_rows:
        lines.append(
            f"- {r['arm']}: W_attr `{r['mean_resource_attributable_W']:.6f}`, mean link negativity `{r['mean_link_negativity']:.6f}`, mean coherence `{r['mean_l1_coherence']:.6f}`."
        )
    lines.extend(["", "## Claim Ceiling", "", manifest["claim_ceiling"], ""])
    (out / f"{EXPERIMENT}_report_2026-07-10.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
