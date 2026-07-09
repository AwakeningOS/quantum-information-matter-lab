#!/usr/bin/env python3
"""Resource partition counterfactual: keep quantum structure vs route to W."""
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


EXPERIMENT = "qcell_resource_partition_counterfactual_v0"
GRID_ID = "QFCBM_0988"
ARMS = [
    ("quantum_keep_structure", "ring", 0.0),
    ("dephase_after_internal_25", "ring", 0.25),
    ("dephase_after_internal_50", "ring", 0.50),
    ("dephase_after_internal_75", "ring", 0.75),
    ("full_dephase_after_internal", "ring", 1.0),
    ("classical_same_graph_transport", "classical_probability_transport", 1.0),
    ("no_internal_links", "coupling_off", 0.0),
]


def write_csv_atomic(path: Path, rows: list[dict]) -> None:
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


def q0988_grid():
    for grid in fixedmap.grids():
        if grid.grid_id == GRID_ID:
            return grid
    raise RuntimeError(f"{GRID_ID} not found")


def cond_for(grid, variant):
    return cpu.Condition(GRID_ID, variant, "R3_pure_1", "N4_dephase_plus_amplitude_damping", 0.06, grid.g_internal, grid.theta_in_RE, "none", "staged")


def diagonal_shadow(rho):
    out = torch.zeros_like(rho)
    idx = torch.arange(cpu.DIM_SYS, device=rho.device)
    out[:, idx, idx] = rho.diagonal(dim1=-2, dim2=-1)
    return out


def offdiag_l1(rho, device):
    mask = torch.as_tensor(cpu.OFFDIAG_SYS, dtype=torch.bool, device=device)
    return rho.abs()[:, mask].sum(dim=1).real


def mean_negativity(rho):
    vals = []
    for i, j, _ in cpu.PAIR_SYS:
        _mi, neg = eng.pair_metrics(rho, i, j)
        vals.append(neg)
    return torch.stack(vals).mean(dim=0)


def corr_t(x, y):
    xm = x - x.mean()
    ym = y - y.mean()
    den = torch.sqrt((xm * xm).sum() * (ym * ym).sum()).clamp_min(1e-15)
    return float(((xm * ym).sum() / den).detach().cpu())


def run_arm(grid, arm, variant, dephase_strength, seeds, resource_on, device):
    cond = cond_for(grid, variant)
    n = len(seeds)
    bits = torch.as_tensor(cpu.SYS_BITS, dtype=eng.RDTYPE, device=device)
    hamming = torch.as_tensor(cpu.HAMMING_SYS, dtype=eng.RDTYPE, device=device)
    zero = eng.t(cpu.r_state("R2_pure_0"), device)
    resource = eng.t(cpu.r_state("R3_pure_1"), device)
    rho = eng.random_products(seeds, device)
    out_angle = torch.full((n,), grid.theta_out_DW * grid.out_layers, dtype=eng.RDTYPE, device=device)
    initial_energy = eng.sys_energy(rho, bits)
    cum = {k: torch.zeros(n, dtype=eng.RDTYPE, device=device) for k in ("rin", "rout", "w", "w_diag", "loss", "coh", "neg", "qnoise")}
    max_res = torch.zeros(n, dtype=eng.RDTYPE, device=device)
    loss_ts, coh_ts, neg_ts = [], [], []
    checkpoints = []
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
        before_output = rho
        diag = diagonal_shadow(before_output)
        coh = offdiag_l1(before_output, device)
        neg = mean_negativity(before_output)
        full = eng.full_state(before_output, zero, zero)
        full = lc.apply_two_local_batched_u(full, lc.exchange_batch(out_angle, device), cpu.N_FULL, 5, 6)
        w = eng.trace_full_w(full)[:, 1, 1].real
        rho = eng.trace_full_to_sys(full)
        full_d = eng.full_state(diag, zero, zero)
        full_d = lc.apply_two_local_batched_u(full_d, lc.exchange_batch(out_angle, device), cpu.N_FULL, 5, 6)
        w_diag = eng.trace_full_w(full_d)[:, 1, 1].real
        loss = w_diag - w
        rho, qnoise = eng.apply_noise(rho, cond.noise, cond.p, hamming, bits, device, strong=False)
        end_energy = eng.sys_energy(rho, bits)
        residual = rin - ((end_energy - start_energy) + rout + w + qnoise)
        max_res = torch.maximum(max_res, residual.abs())
        for k, v in (("rin", rin), ("rout", rout), ("w", w), ("w_diag", w_diag), ("loss", loss), ("coh", coh), ("neg", neg), ("qnoise", qnoise)):
            cum[k] += v
        loss_ts.append(loss); coh_ts.append(coh); neg_ts.append(neg)
        if cycle in (0, 49, 74, 124, 149, 199):
            host = {k: v.detach().cpu() for k, v in {"w": w, "w_diag": w_diag, "loss": loss, "coh": coh, "neg": neg}.items()}
            for ix, seed in enumerate(seeds):
                checkpoints.append({"arm": arm, "resource_on": int(resource_on), "seed": int(seed), "cycle": cycle + 1, **{k: float(v[ix]) for k, v in host.items()}})
    loss_mat = torch.stack(loss_ts); coh_mat = torch.stack(coh_ts); neg_mat = torch.stack(neg_ts)
    host = {k: v.detach().cpu().numpy() for k, v in cum.items()}
    final_parts = eng.part_energies(rho, bits).detach().cpu().numpy()
    final_energy = eng.sys_energy(rho, bits).detach().cpu().numpy()
    rows = []
    for ix, seed in enumerate(seeds):
        rows.append({
            "arm": arm, "variant": variant, "dephase_strength": dephase_strength, "resource_on": int(resource_on), "seed": int(seed),
            "W": float(host["w"][ix]), "W_diag_same_population": float(host["w_diag"][ix]), "W_loss_to_structure": float(host["loss"][ix]),
            "R_in_cum": float(host["rin"][ix]), "R_out_cum": float(host["rout"][ix]), "Q_noise_cum": float(host["qnoise"][ix]),
            "Delta_E_internal": float(final_energy[ix] - initial_energy.detach().cpu().numpy()[ix]),
            "final_E_total": float(final_energy[ix]),
            "final_E": float(final_parts[ix, 0]), "final_A": float(final_parts[ix, 1]), "final_B": float(final_parts[ix, 2]),
            "final_C": float(final_parts[ix, 3]), "final_D": float(final_parts[ix, 4]),
            "mean_coherence": float(host["coh"][ix] / 200), "mean_negativity": float(host["neg"][ix] / 200),
            "corr_coherence_vs_W_loss": corr_t(coh_mat[:, ix], loss_mat[:, ix]),
            "corr_negativity_vs_W_loss": corr_t(neg_mat[:, ix], loss_mat[:, ix]),
            "max_residual": float(max_res.detach().cpu().numpy()[ix]),
        })
    return rows, checkpoints


def main():
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
    t0 = time.time(); device = torch.device(args.device)
    grid = q0988_grid(); seeds = cpu.MAIN_SEEDS[40:40 + args.n_seeds]
    out = Path(args.outdir); out.mkdir(parents=True, exist_ok=True)
    rows, checkpoints = [], []
    for arm, variant, dep in ARMS:
        print(f"arm={arm}", flush=True)
        res, chk = run_arm(grid, arm, variant, dep, seeds, True, device)
        no, chk_no = run_arm(grid, arm, variant, dep, seeds, False, device)
        no_by = {r["seed"]: r for r in no}
        for r in res:
            n = no_by[r["seed"]]
            rows.append({**r, "W_no_resource": n["W"], "resource_attributable_W": r["W"] - n["W"], "diag_resource_attributable_W": r["W_diag_same_population"] - n["W_diag_same_population"]})
        checkpoints.extend(chk); checkpoints.extend(chk_no)
    summaries = []
    for arm, _v, _d in ARMS:
        sub = [r for r in rows if r["arm"] == arm]
        summaries.append({
            "arm": arm, "n_seed": len(sub),
            "mean_resource_attributable_W": sum(r["resource_attributable_W"] for r in sub)/len(sub),
            "mean_diag_resource_attributable_W": sum(r["diag_resource_attributable_W"] for r in sub)/len(sub),
            "mean_W_loss_to_structure": sum(r["W_loss_to_structure"] for r in sub)/len(sub),
            "mean_R_in_cum": sum(r["R_in_cum"] for r in sub)/len(sub),
            "mean_R_out_cum": sum(r["R_out_cum"] for r in sub)/len(sub),
            "mean_Q_noise_cum": sum(r["Q_noise_cum"] for r in sub)/len(sub),
            "mean_Delta_E_internal": sum(r["Delta_E_internal"] for r in sub)/len(sub),
            "mean_final_E_total": sum(r["final_E_total"] for r in sub)/len(sub),
            "mean_final_E": sum(r["final_E"] for r in sub)/len(sub),
            "mean_final_A": sum(r["final_A"] for r in sub)/len(sub),
            "mean_final_B": sum(r["final_B"] for r in sub)/len(sub),
            "mean_final_C": sum(r["final_C"] for r in sub)/len(sub),
            "mean_final_D": sum(r["final_D"] for r in sub)/len(sub),
            "mean_coherence": sum(r["mean_coherence"] for r in sub)/len(sub),
            "mean_negativity": sum(r["mean_negativity"] for r in sub)/len(sub),
            "positive_W_loss_seed_count": sum(1 for r in sub if r["W_loss_to_structure"] > 0),
            "mean_corr_coherence_vs_W_loss": sum(r["corr_coherence_vs_W_loss"] for r in sub)/len(sub),
            "max_residual": max(r["max_residual"] for r in sub),
        })
    write_csv_atomic(out / f"{EXPERIMENT}_seed_summary.csv", rows)
    write_csv_atomic(out / f"{EXPERIMENT}_arm_summary.csv", summaries)
    write_csv_atomic(out / f"{EXPERIMENT}_checkpoint_trace.csv", checkpoints)
    manifest = {"experiment": EXPERIMENT, "grid_id": GRID_ID, "n_seeds": len(seeds), "cycles": 200, "arms": [a for a,_,_ in ARMS], "wall_seconds": time.time()-t0, "max_residual": max(r["max_residual"] for r in summaries), "claim_ceiling": "model-level resource partition counterfactual; no quantum advantage or physical energy claim"}
    (out / f"{EXPERIMENT}_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    report = ["# Q-cell resource partition counterfactual v0", "", "Date: 2026-07-10 JST", "", "## Readout", ""]
    for r in summaries:
        report.append(f"- {r['arm']}: W_attr `{r['mean_resource_attributable_W']:.6f}`, diag W_attr `{r['mean_diag_resource_attributable_W']:.6f}`, W_loss `{r['mean_W_loss_to_structure']:.6f}`, coherence `{r['mean_coherence']:.6f}`.")
    report += ["", "## Claim Ceiling", "", manifest["claim_ceiling"], ""]
    (out / f"{EXPERIMENT}_report_2026-07-10.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
