#!/usr/bin/env python3
"""
Postprocess fixed-circuit output bottleneck map with paired no-resource and matched central controls.

Input CSV must include one row per (grid_id, seed, variant_type), with variant_type:
local_resource, local_no_resource, central_resource, central_no_resource.
"""
from __future__ import annotations

import argparse
import numpy as np
import pandas as pd

REQUIRED = [
    "grid_id", "variant_type", "seed",
    "E_R_in_cum", "E_R_out_cum", "E_W_out_cum",
    "Delta_E_Qcell_cum", "Q_noise_cum", "W_external_cum",
    "energy_balance_residual_max_abs",
    "resource_free_energy_consumed_cum",
    "initial_E_Qcell", "final_E_Qcell",
    "D_population_mean", "D_population_peak", "D_to_W_flow_cum",
    "U_DW_commutator_norm", "output_switching_cost_status",
]

def safe_div(num, den, eps=1e-12):
    return np.where(np.abs(den) > eps, num / den, np.nan)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="condition/seed summary CSV")
    ap.add_argument("--out-prefix", default="qcell_fixed_circuit_output_bottleneck_map")
    args = ap.parse_args()

    df = pd.read_csv(args.input)
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise SystemExit(f"missing required columns: {missing}")

    idx_cols = ["grid_id", "seed"]
    meta_cols = [c for c in ["structure", "g_internal", "theta_in_RE", "theta_out_DW", "out_layers"] if c in df.columns]

    metrics = [
        "E_W_out_cum", "E_R_in_cum", "E_R_out_cum",
        "Delta_E_Qcell_cum", "Q_noise_cum", "W_external_cum",
        "energy_balance_residual_max_abs", "resource_free_energy_consumed_cum",
        "initial_E_Qcell", "final_E_Qcell",
        "D_population_mean", "D_population_peak", "D_to_W_flow_cum",
        "U_DW_commutator_norm",
    ]
    wide = df.pivot_table(index=idx_cols, columns="variant_type", values=metrics, aggfunc="first")
    wide.columns = [f"{a}__{b}" for a, b in wide.columns]
    wide = wide.reset_index()

    meta = df[idx_cols + meta_cols].drop_duplicates(idx_cols)
    out = wide.merge(meta, on=idx_cols, how="left")

    def col(metric, variant):
        name = f"{metric}__{variant}"
        if name not in out.columns:
            out[name] = np.nan
        return out[name]

    out["W_with_resource"] = col("E_W_out_cum", "local_resource")
    out["W_without_resource"] = col("E_W_out_cum", "local_no_resource")
    out["resource_attributable_W"] = out["W_with_resource"] - out["W_without_resource"]

    out["central_W_with_resource"] = col("E_W_out_cum", "central_resource")
    out["central_W_without_resource"] = col("E_W_out_cum", "central_no_resource")
    out["central_resource_attributable_W"] = out["central_W_with_resource"] - out["central_W_without_resource"]
    out["fixed_to_matched_central_ratio"] = safe_div(out["resource_attributable_W"], out["central_resource_attributable_W"])

    out["net_resource_transfer"] = col("E_R_in_cum", "local_resource") - col("E_R_out_cum", "local_resource")
    out["efficiency_resource_to_W"] = safe_div(out["resource_attributable_W"], out["net_resource_transfer"])
    out["efficiency_input_to_W"] = safe_div(out["resource_attributable_W"], col("E_R_in_cum", "local_resource"))
    out["efficiency_free_energy_to_W"] = safe_div(out["resource_attributable_W"], col("resource_free_energy_consumed_cum", "local_resource"))

    out["initial_internal_energy_change"] = col("initial_E_Qcell", "local_resource") - col("final_E_Qcell", "local_resource")

    residual_cols = [c for c in out.columns if c.startswith("energy_balance_residual_max_abs__")]
    out["max_abs_energy_balance_residual_any_variant"] = out[residual_cols].max(axis=1)

    comm_cols = [c for c in out.columns if c.startswith("U_DW_commutator_norm__")]
    out["max_U_DW_commutator_norm_any_variant"] = out[comm_cols].max(axis=1)

    dpop = col("D_population_mean", "local_resource")
    dflow = col("D_to_W_flow_cum", "local_resource")
    attrib = out["resource_attributable_W"]
    out["label_outlet_narrow"] = (dpop > dpop.quantile(0.75)) & (dflow < dflow.quantile(0.25)) & (attrib < attrib.quantile(0.50))
    out["label_efficiency_gt_1"] = out["efficiency_resource_to_W"] > 1.0

    out.to_csv(f"{args.out_prefix}_paired_seed_metrics.csv", index=False)

    group_cols = ["grid_id"] + meta_cols
    agg = out.groupby(group_cols, dropna=False).agg(
        n_seed=("seed", "count"),
        resource_attributable_W_mean=("resource_attributable_W", "mean"),
        resource_attributable_W_std=("resource_attributable_W", "std"),
        central_resource_attributable_W_mean=("central_resource_attributable_W", "mean"),
        fixed_to_matched_central_ratio_mean=("fixed_to_matched_central_ratio", "mean"),
        efficiency_resource_to_W_mean=("efficiency_resource_to_W", "mean"),
        efficiency_resource_to_W_std=("efficiency_resource_to_W", "std"),
        net_resource_transfer_mean=("net_resource_transfer", "mean"),
        initial_internal_energy_change_mean=("initial_internal_energy_change", "mean"),
        Q_noise_cum_mean=("Q_noise_cum__local_resource", "mean"),
        D_population_mean=("D_population_mean__local_resource", "mean"),
        D_to_W_flow_cum_mean=("D_to_W_flow_cum__local_resource", "mean"),
        max_abs_energy_balance_residual=("max_abs_energy_balance_residual_any_variant", "max"),
        max_U_DW_commutator_norm=("max_U_DW_commutator_norm_any_variant", "max"),
        n_efficiency_gt_1=("label_efficiency_gt_1", "sum"),
        n_outlet_narrow=("label_outlet_narrow", "sum"),
    ).reset_index()
    agg.to_csv(f"{args.out_prefix}_grid_summary_corrected.csv", index=False)

    reps = []
    for name, sort_col, ascending in [
        ("top_resource_attributable_W", "resource_attributable_W_mean", False),
        ("top_efficiency_resource_to_W", "efficiency_resource_to_W_mean", False),
        ("top_fixed_to_matched_central_ratio", "fixed_to_matched_central_ratio_mean", False),
        ("outlet_narrow", "n_outlet_narrow", False),
        ("high_residual_check", "max_abs_energy_balance_residual", False),
    ]:
        sub = agg.sort_values(sort_col, ascending=ascending).head(20).copy()
        sub.insert(0, "region_type", name)
        reps.append(sub)
    pd.concat(reps, ignore_index=True).to_csv(f"{args.out_prefix}_promising_regions_corrected.csv", index=False)

    print({
        "paired_seed_metrics": f"{args.out_prefix}_paired_seed_metrics.csv",
        "grid_summary": f"{args.out_prefix}_grid_summary_corrected.csv",
        "promising_regions": f"{args.out_prefix}_promising_regions_corrected.csv",
        "n_rows": int(len(out)),
        "n_grids": int(agg["grid_id"].nunique()),
    })

if __name__ == "__main__":
    main()
