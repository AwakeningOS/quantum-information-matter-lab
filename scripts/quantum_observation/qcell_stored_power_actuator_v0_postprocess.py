#!/usr/bin/env python3
"""Compact postprocess for stored-power actuator traces."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


EXPERIMENT = "qcell_stored_power_actuator_v0"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed-summary", required=True)
    ap.add_argument("--cycle-trace", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()

    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    seed = pd.read_csv(args.seed_summary)
    cycle = pd.read_csv(args.cycle_trace)
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))

    condition = seed.groupby("condition", dropna=False).agg(
        n_seed=("seed", "count"),
        mean_W_resource=("W_resource", "mean"),
        mean_W_no_resource=("W_no_resource", "mean"),
        mean_resource_attributable_W=("resource_attributable_W", "mean"),
        min_resource_attributable_W=("resource_attributable_W", "min"),
        mean_action_allowed_cycles=("controller_action_allowed_cycles", "mean"),
        mean_starved_cycles=("controller_starved_cycles", "mean"),
        mean_controller_energy_spent=("controller_energy_spent", "mean"),
        mean_S_min=("S_min", "mean"),
        mean_S_max=("S_max", "mean"),
        mean_S_final=("S_final", "mean"),
        max_zero_store_action_violations=("zero_store_action_violations", "max"),
        max_action_without_spend_violations=("action_without_spend_violations", "max"),
        max_empty_store_action_violations=("empty_store_action_violations", "max"),
        max_accounting_residual_abs=("max_accounting_residual_abs", "max"),
    ).reset_index()
    condition.to_csv(out / f"{EXPERIMENT}_condition_summary.csv", index=False)

    windows = []
    for condition_name, sub in cycle.groupby("condition", dropna=False):
        for label, lo, hi in [
            ("early", 0, 59),
            ("middle", 60, 119),
            ("late", 120, 199),
        ]:
            w = sub[(sub.t >= lo) & (sub.t <= hi)]
            windows.append(
                {
                    "condition": condition_name,
                    "window": label,
                    "t0": lo,
                    "t1": hi,
                    "mean_store_before_action": w["store_before_action"].mean(),
                    "mean_action_allowed": w["controller_action_allowed"].mean(),
                    "mean_starved": w["controller_starved"].mean(),
                    "mean_resource_attributable_W_cycle": w["resource_attributable_W_cycle"].mean(),
                    "mean_cumulative_resource_attributable_W": w["resource_attributable_W"].mean(),
                }
            )
    pd.DataFrame(windows).to_csv(out / f"{EXPERIMENT}_window_summary.csv", index=False)

    compact_manifest = {
        **manifest,
        "input_seed_summary": args.seed_summary,
        "input_cycle_trace": args.cycle_trace,
        "postprocess_outputs": [
            f"{EXPERIMENT}_condition_summary.csv",
            f"{EXPERIMENT}_window_summary.csv",
            f"{EXPERIMENT}_manifest.json",
            f"{EXPERIMENT}_report_2026-07-10.md",
        ],
        "n_seed_rows": int(len(seed)),
        "n_cycle_rows": int(len(cycle)),
        "max_zero_store_action_violations": int(seed["zero_store_action_violations"].max()),
        "max_action_without_spend_violations": int(seed["action_without_spend_violations"].max()),
        "max_empty_store_action_violations": int(seed["empty_store_action_violations"].max()),
        "max_accounting_residual_abs": float(seed["max_accounting_residual_abs"].max()),
        "note": "full cycle trace remains local; committed outputs are compact summaries and manifest",
    }
    (out / f"{EXPERIMENT}_manifest.json").write_text(
        json.dumps(compact_manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    def pick(name: str) -> pd.Series:
        return condition[condition.condition == name].iloc[0]

    never0 = pick("supply_never_on_initial_zero")
    always = pick("supply_always_on_initial_zero")
    stop = pick("supply_stop_midway_initial_zero")
    restart = pick("supply_restart_after_stop_initial_zero")
    initial = pick("supply_never_on_initial_positive")
    report = out / f"{EXPERIMENT}_report_2026-07-10.md"
    report.write_text(
        "\n".join(
            [
                "# Q-cell stored-power actuator v0",
                "",
                "Date: 2026-07-10 JST",
                "",
                "## Scope",
                "",
                "QFCBM_0988-only causal trace test for a model-level finite internal store. The store is updated before controller action and `store_before_action` strictly gates dynamic action.",
                "",
                "This is not a physical energy reservoir or thermodynamic work claim.",
                "",
                "## Run Facts",
                "",
                f"- seeds: {compact_manifest['n_seed_rows'] // len(manifest['conditions'])}",
                f"- cycle rows: {compact_manifest['n_cycle_rows']}",
                f"- kappa: `{manifest['kappa']}`",
                f"- store capacity: `{manifest['store_capacity']}`",
                f"- supply gain: `{manifest['supply_gain']}`",
                f"- max zero-store action violations: `{compact_manifest['max_zero_store_action_violations']}`",
                f"- max action-without-spend violations: `{compact_manifest['max_action_without_spend_violations']}`",
                f"- max insufficient-store action violations: `{compact_manifest['max_empty_store_action_violations']}`",
                f"- max accounting residual: `{compact_manifest['max_accounting_residual_abs']:.3e}`",
                "",
                "## Readout",
                "",
                f"- `supply_never_on_initial_zero`: allowed cycles `{never0.mean_action_allowed_cycles:.2f}`, starved `{never0.mean_starved_cycles:.2f}`, mean W_attr `{never0.mean_resource_attributable_W:.6f}`.",
                f"- `supply_always_on_initial_zero`: allowed cycles `{always.mean_action_allowed_cycles:.2f}`, starved `{always.mean_starved_cycles:.2f}`, mean W_attr `{always.mean_resource_attributable_W:.6f}`.",
                f"- `supply_stop_midway_initial_zero`: allowed cycles `{stop.mean_action_allowed_cycles:.2f}`, starved `{stop.mean_starved_cycles:.2f}`, final store `{stop.mean_S_final:.6f}`, mean W_attr `{stop.mean_resource_attributable_W:.6f}`.",
                f"- `supply_restart_after_stop_initial_zero`: allowed cycles `{restart.mean_action_allowed_cycles:.2f}`, starved `{restart.mean_starved_cycles:.2f}`, final store `{restart.mean_S_final:.6f}`, mean W_attr `{restart.mean_resource_attributable_W:.6f}`.",
                f"- `supply_never_on_initial_positive`: allowed cycles `{initial.mean_action_allowed_cycles:.2f}`, starved `{initial.mean_starved_cycles:.2f}`, final store `{initial.mean_S_final:.6f}`, mean W_attr `{initial.mean_resource_attributable_W:.6f}`.",
                "",
                "## Claim Ceiling",
                "",
                "Allowed: model-level finite internal store gating of controller action.",
                "",
                "Not allowed: metabolism, homeostasis, life, agency, quantum advantage, or real thermodynamic work.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(compact_manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
