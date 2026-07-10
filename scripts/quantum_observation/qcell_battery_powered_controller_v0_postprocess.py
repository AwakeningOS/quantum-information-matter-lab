#!/usr/bin/env python3
"""Postprocess finite-M battery-powered controller summaries."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


EXPERIMENT = "qcell_battery_powered_controller_v0"


def all_seed_positive(x: pd.Series) -> bool:
    return bool((x > 0).all())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()

    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(args.input)
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))

    df["M_initial_label"] = df["M_initial"].astype(str)
    df["net_after_controller_spend"] = df["resource_attributable_W"] - df["controller_energy_spent"]
    df["resource_attr_positive"] = df["resource_attributable_W"] > 0
    df["net_after_spend_positive"] = df["net_after_controller_spend"] > 0

    group_cols = ["grid_id", "controller", "kappa", "M_initial_label"]
    grid = df.groupby(group_cols, dropna=False).agg(
        n_seed=("seed", "count"),
        mean_resource_attributable_W=("resource_attributable_W", "mean"),
        median_resource_attributable_W=("resource_attributable_W", "median"),
        n_resource_attr_positive=("resource_attr_positive", "sum"),
        all_resource_attr_positive=("resource_attributable_W", all_seed_positive),
        mean_controller_energy_spent=("controller_energy_spent", "mean"),
        mean_M_energy_final=("M_energy_final", "mean"),
        mean_controller_starved_cycles=("controller_starved_cycles", "mean"),
        max_emitted_when_starved_cycles=("emitted_when_starved_cycles", "max"),
        mean_angle_budget=("angle_budget", "mean"),
        mean_net_after_controller_spend=("net_after_controller_spend", "mean"),
        n_net_after_spend_positive=("net_after_spend_positive", "sum"),
        all_net_after_spend_positive=("net_after_controller_spend", all_seed_positive),
        max_residual=("energy_balance_residual_max_abs", "max"),
    ).reset_index()
    grid.to_csv(out / f"{EXPERIMENT}_grid_summary.csv", index=False)

    evolved = grid[grid["controller"] == "evolved"].copy()
    thresholds = []
    for grid_id, sub in evolved.groupby("grid_id"):
        positive = sub[sub["all_resource_attr_positive"]]
        net_positive = sub[sub["all_net_after_spend_positive"]]
        finite = sub[sub["M_initial_label"] != "unlimited"].copy()
        finite["M_initial_float"] = finite["M_initial_label"].astype(float)
        finite_pos = finite[finite["all_resource_attr_positive"]]
        finite_net_pos = finite[finite["all_net_after_spend_positive"]]
        thresholds.append(
            {
                "grid_id": grid_id,
                "max_kappa_all_seed_attr_positive": positive["kappa"].max() if len(positive) else None,
                "max_kappa_all_seed_net_after_spend_positive": net_positive["kappa"].max() if len(net_positive) else None,
                "min_finite_M_attr_positive_any_kappa": finite_pos["M_initial_float"].min() if len(finite_pos) else None,
                "min_finite_M_net_after_spend_positive_any_kappa": finite_net_pos["M_initial_float"].min() if len(finite_net_pos) else None,
                "zero_battery_max_angle_budget": float(
                    df[
                        (df["grid_id"] == grid_id)
                        & (df["controller"] == "evolved")
                        & (df["M_initial_label"] == "0.0")
                    ]["angle_budget"].max()
                ),
                "zero_battery_max_resource_attr": float(
                    df[
                        (df["grid_id"] == grid_id)
                        & (df["controller"] == "evolved")
                        & (df["M_initial_label"] == "0.0")
                    ]["resource_attributable_W"].max()
                ),
            }
        )
    threshold_df = pd.DataFrame(thresholds)
    threshold_df.to_csv(out / f"{EXPERIMENT}_threshold_summary.csv", index=False)

    compact_manifest = {
        **manifest,
        "input_seed_summary": args.input,
        "postprocess_outputs": [
            f"{EXPERIMENT}_grid_summary.csv",
            f"{EXPERIMENT}_threshold_summary.csv",
            f"{EXPERIMENT}_manifest.json",
        ],
        "n_seed_rows": int(len(df)),
        "max_residual": float(df["energy_balance_residual_max_abs"].max()),
        "max_emitted_when_starved_cycles": float(df["emitted_when_starved_cycles"].max()),
        "zero_battery_dynamic_angle_max": float(
            df[(df["M_initial_label"] == "0.0") & (df["controller"] != "fixed")]["angle_budget"].max()
        ),
        "note": "seed-level summary remains local; committed outputs are compact postprocessed summaries",
    }
    (out / f"{EXPERIMENT}_manifest.json").write_text(
        json.dumps(compact_manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    report = out / f"{EXPERIMENT}_report_2026-07-10.md"
    q0988 = grid[(grid.grid_id == "QFCBM_0988") & (grid.controller == "evolved")]
    q0496 = grid[(grid.grid_id == "QFCBM_0496") & (grid.controller == "evolved")]
    q0399 = grid[(grid.grid_id == "QFCBM_0399") & (grid.controller == "evolved")]

    def row_text(frame: pd.DataFrame, kappa: float, m_label: str) -> str:
        row = frame[(frame.kappa == kappa) & (frame.M_initial_label == m_label)].iloc[0]
        return (
            f"mean W_attr `{row.mean_resource_attributable_W:.6f}`, "
            f"spent `{row.mean_controller_energy_spent:.6f}`, "
            f"positive `{int(row.n_resource_attr_positive)}/{int(row.n_seed)}`"
        )

    report.write_text(
        "\n".join(
            [
                "# Q-cell battery-powered controller v0",
                "",
                "Date: 2026-07-10 JST",
                "",
                "## Scope",
                "",
                "Finite actuator-budget test for the evolved local controller. This replaces post-hoc cost subtraction with an explicit monotone-depleting controller reservoir `M` during the simulation.",
                "",
                "This is not a physical thermodynamic actuator model. Signal acquisition, controller computation, and coupling-switching costs remain unmodeled.",
                "",
                "## Run Facts",
                "",
                f"- grids: {', '.join(manifest['grids'])}",
                f"- seeds per grid: {manifest['n_seeds']}",
                f"- rows: {len(df)}",
                f"- wall seconds: {manifest['wall_seconds']:.3f}",
                f"- maximum energy-balance residual: `{df['energy_balance_residual_max_abs'].max():.3e}`",
                f"- zero-battery dynamic angle maximum: `{compact_manifest['zero_battery_dynamic_angle_max']:.6f}`",
                f"- starved-cycle emitted-action maximum: `{compact_manifest['max_emitted_when_starved_cycles']:.6f}`",
                "",
                "## Readout",
                "",
                "- `QFCBM_0988` is the robust result. The evolved controller remains positive under finite controller reservoirs; at `kappa=0.03`, `M=1.0` gives "
                + row_text(q0988, 0.03, "1.0")
                + " and `M=5.0` gives "
                + row_text(q0988, 0.03, "5.0")
                + ".",
                "- `QFCBM_0496` is weaker but still survives finite reservoirs in selected settings; at `kappa=0.03`, `M=1.0` gives "
                + row_text(q0496, 0.03, "1.0")
                + ".",
                "- `QFCBM_0399` remains fragile; at `kappa=0.03`, `M=0.2` is not mean-positive, while `M=1.0` gives "
                + row_text(q0399, 0.03, "1.0")
                + ".",
                "- `M=0` correctly shuts off dynamic controller action. This supports that the result is not a free-action artifact.",
                "",
                "## Claim Ceiling",
                "",
                "Allowed:",
                "",
                "```text",
                "Under an explicit finite controller-reservoir accounting model, the evolved local controller remains resource-attributable-output positive in selected regions, especially QFCBM_0988.",
                "```",
                "",
                "Not allowed:",
                "",
                "```text",
                "real thermodynamic work",
                "complete actuator physics",
                "metabolism/homeostasis/life/agency",
                "quantum advantage",
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(json.dumps(compact_manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
