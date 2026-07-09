#!/usr/bin/env python3
"""Post-hoc controller cost accounting for qcell_controller_evolution_v0."""
from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd


EXPERIMENT = "qcell_controller_cost_accounting_v0"
DEFAULT_COSTS = [0, 1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--costs", default=",".join(str(x) for x in DEFAULT_COSTS))
    args = ap.parse_args()

    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    costs = [float(x) for x in args.costs.split(",") if x.strip()]
    df = pd.read_csv(args.input)

    # Remove duplicate rows if the evolution runner evaluated the same top
    # candidate twice because duplicate elites survived validation.
    df = df.drop_duplicates(["candidate_id", "grid_id", "seed"])

    df["break_even_cost_per_angle"] = df["gain_over_fixed"] / df["angle_budget"].replace(0, np.nan)

    sweep_rows = []
    for cost in costs:
        tmp = df.copy()
        tmp["cost_per_angle"] = cost
        tmp["gross_controller_cost"] = tmp["angle_budget"] * cost
        tmp["net_gain_after_cost"] = tmp["gain_over_fixed"] - tmp["gross_controller_cost"]
        tmp["net_positive_after_cost"] = tmp["net_gain_after_cost"] > 0
        sweep_rows.append(tmp)
    sweep = pd.concat(sweep_rows, ignore_index=True)
    sweep.to_csv(out / f"{EXPERIMENT}_seed_cost_sweep.csv", index=False)

    summary = sweep.groupby(["candidate_id", "grid_id", "cost_per_angle"], dropna=False).agg(
        n_seed=("seed", "count"),
        mean_gain_before_cost=("gain_over_fixed", "mean"),
        mean_angle_budget=("angle_budget", "mean"),
        mean_gross_controller_cost=("gross_controller_cost", "mean"),
        mean_net_gain_after_cost=("net_gain_after_cost", "mean"),
        median_net_gain_after_cost=("net_gain_after_cost", "median"),
        n_net_positive_after_cost=("net_positive_after_cost", "sum"),
        min_break_even_cost_per_angle=("break_even_cost_per_angle", "min"),
        mean_break_even_cost_per_angle=("break_even_cost_per_angle", "mean"),
        no_resource_trick_count=("no_resource_trick_flag", "sum"),
        max_budget_excess=("budget_excess", "max"),
        max_residual=("energy_balance_residual_max_abs", "max"),
    ).reset_index()
    summary.to_csv(out / f"{EXPERIMENT}_grid_summary.csv", index=False)

    manifest = {
        "experiment": EXPERIMENT,
        "input": args.input,
        "n_input_rows_deduplicated": int(len(df)),
        "costs": costs,
        "cost_model": "net_gain_after_cost = gain_over_fixed - cost_per_angle * angle_budget",
        "note": "conservative gross controller cost; fixed-circuit operation cost is not subtracted",
    }
    (out / f"{EXPERIMENT}_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

