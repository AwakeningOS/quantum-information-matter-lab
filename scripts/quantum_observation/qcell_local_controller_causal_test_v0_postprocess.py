#!/usr/bin/env python3
"""Postprocess qcell_local_controller_causal_test_v0 compact summaries."""
from __future__ import annotations

import argparse
import numpy as np
import pandas as pd


PAIRS = {
    "fixed": ("fixed_local_resource", "fixed_local_no_resource"),
    "internal": ("internal_controller_resource", "internal_controller_no_resource"),
    "internal_shuffled_signal": ("internal_shuffled_signal_resource", "internal_shuffled_signal_no_resource"),
    "internal_time_shift": ("internal_time_shift_action_resource", "internal_time_shift_action_no_resource"),
    "output": ("output_controller_resource", "output_controller_no_resource"),
    "output_shuffled_signal": ("output_shuffled_signal_resource", "output_shuffled_signal_no_resource"),
    "output_time_shift": ("output_time_shift_action_resource", "output_time_shift_action_no_resource"),
    "central": ("matched_central_resource", "matched_central_no_resource"),
}


def safe_div(a, b):
    return np.where(np.abs(b) > 1e-12, a / b, np.nan)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out-prefix", required=True)
    args = ap.parse_args()
    df = pd.read_csv(args.input)
    idx = ["grid_id", "seed"]
    meta_cols = ["structure", "g_internal", "theta_in_RE", "theta_out_DW", "out_layers"]
    metrics = [
        "E_W_out_cum", "E_R_in_cum", "E_R_out_cum", "net_resource_transfer",
        "resource_free_energy_consumed_cum", "Q_noise_cum",
        "Delta_E_Qcell_cum", "energy_balance_residual_max_abs",
        "D_population_mean", "D_population_peak", "D_to_W_flow_cum",
        "controller_action_count", "controller_internal_action_count",
        "controller_output_action_count", "controller_total_angle_budget",
        "controller_internal_angle_budget", "controller_output_angle_budget",
        "fixed_internal_angle_budget", "fixed_output_angle_budget",
        "max_link_angle",
    ]
    wide = df.pivot_table(index=idx, columns="controller_variant", values=metrics, aggfunc="first")
    wide.columns = [f"{m}__{v}" for m, v in wide.columns]
    wide = wide.reset_index()
    meta = df[idx + meta_cols].drop_duplicates(idx)
    out = wide.merge(meta, on=idx, how="left")

    def col(metric, variant):
        name = f"{metric}__{variant}"
        if name not in out.columns:
            out[name] = np.nan
        return out[name]

    for family, (res, nores) in PAIRS.items():
        out[f"{family}_W_resource"] = col("E_W_out_cum", res)
        out[f"{family}_W_no_resource"] = col("E_W_out_cum", nores)
        out[f"{family}_resource_attributable_W"] = out[f"{family}_W_resource"] - out[f"{family}_W_no_resource"]

    for family in ["internal", "internal_shuffled_signal", "internal_time_shift", "output", "output_shuffled_signal", "output_time_shift"]:
        out[f"{family}_gain_over_fixed"] = out[f"{family}_resource_attributable_W"] - out["fixed_resource_attributable_W"]
        out[f"{family}_W_resource_delta_vs_fixed"] = out[f"{family}_W_resource"] - out["fixed_W_resource"]
        out[f"{family}_W_no_resource_delta_vs_fixed"] = out[f"{family}_W_no_resource"] - out["fixed_W_no_resource"]
        out[f"{family}_to_central_ratio"] = safe_div(out[f"{family}_resource_attributable_W"], out["central_resource_attributable_W"])

    out["internal_gain_over_shuffled_signal"] = out["internal_resource_attributable_W"] - out["internal_shuffled_signal_resource_attributable_W"]
    out["internal_gain_over_time_shift"] = out["internal_resource_attributable_W"] - out["internal_time_shift_resource_attributable_W"]
    out["output_gain_over_shuffled_signal"] = out["output_resource_attributable_W"] - out["output_shuffled_signal_resource_attributable_W"]
    out["output_gain_over_time_shift"] = out["output_resource_attributable_W"] - out["output_time_shift_resource_attributable_W"]

    for family in ["internal", "output"]:
        out[f"{family}_no_resource_trick_flag"] = (
            (out[f"{family}_gain_over_fixed"] > 0)
            & (out[f"{family}_W_resource_delta_vs_fixed"] <= 0)
            & (out[f"{family}_W_no_resource_delta_vs_fixed"] < 0)
        )

    out.to_csv(f"{args.out_prefix}_paired_seed_metrics.csv", index=False)

    agg_spec = {
        "n_seed": ("seed", "count"),
        "fixed_resource_attributable_W_mean": ("fixed_resource_attributable_W", "mean"),
        "central_resource_attributable_W_mean": ("central_resource_attributable_W", "mean"),
        "max_abs_energy_balance_residual": ("energy_balance_residual_max_abs__fixed_local_resource", "max"),
    }
    for family in ["internal", "internal_shuffled_signal", "internal_time_shift", "output", "output_shuffled_signal", "output_time_shift"]:
        agg_spec.update({
            f"{family}_resource_attributable_W_mean": (f"{family}_resource_attributable_W", "mean"),
            f"{family}_gain_over_fixed_mean": (f"{family}_gain_over_fixed", "mean"),
            f"{family}_gain_over_fixed_median": (f"{family}_gain_over_fixed", "median"),
            f"{family}_n_gain_over_fixed_positive": (f"{family}_gain_over_fixed", lambda s: int((s > 0).sum())),
            f"{family}_W_resource_delta_vs_fixed_mean": (f"{family}_W_resource_delta_vs_fixed", "mean"),
            f"{family}_W_no_resource_delta_vs_fixed_mean": (f"{family}_W_no_resource_delta_vs_fixed", "mean"),
        })
    agg_spec.update({
        "internal_gain_over_shuffled_signal_mean": ("internal_gain_over_shuffled_signal", "mean"),
        "internal_gain_over_time_shift_mean": ("internal_gain_over_time_shift", "mean"),
        "internal_n_gain_over_shuffled_signal_positive": ("internal_gain_over_shuffled_signal", lambda s: int((s > 0).sum())),
        "internal_n_gain_over_time_shift_positive": ("internal_gain_over_time_shift", lambda s: int((s > 0).sum())),
        "output_gain_over_shuffled_signal_mean": ("output_gain_over_shuffled_signal", "mean"),
        "output_gain_over_time_shift_mean": ("output_gain_over_time_shift", "mean"),
        "output_n_gain_over_shuffled_signal_positive": ("output_gain_over_shuffled_signal", lambda s: int((s > 0).sum())),
        "output_n_gain_over_time_shift_positive": ("output_gain_over_time_shift", lambda s: int((s > 0).sum())),
        "internal_no_resource_trick_count": ("internal_no_resource_trick_flag", "sum"),
        "output_no_resource_trick_count": ("output_no_resource_trick_flag", "sum"),
    })
    grid = out.groupby(["grid_id"] + meta_cols, dropna=False).agg(**agg_spec).reset_index()
    grid.to_csv(f"{args.out_prefix}_grid_summary.csv", index=False)

    print({
        "paired_seed_metrics": f"{args.out_prefix}_paired_seed_metrics.csv",
        "grid_summary": f"{args.out_prefix}_grid_summary.csv",
        "n_paired_rows": int(len(out)),
        "n_grids": int(grid["grid_id"].nunique()),
    })


if __name__ == "__main__":
    main()

