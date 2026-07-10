#!/usr/bin/env python3
"""Train/test downstream branch utility from delayed phase-key residuals."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


EXPERIMENT = "qcell_phase_key_controller_utility_v0"


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def load_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        row["seed"] = int(row["seed"])
        row["angle_multiplier"] = float(row["angle_multiplier"])
        row["coherence_attributable_readout_W"] = float(row["coherence_attributable_readout_W"])
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed-summary", required=True)
    ap.add_argument("--outdir", default=f"{EXPERIMENT}_outputs")
    args = ap.parse_args()
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    rows = load_rows(Path(args.seed_summary))
    seeds = sorted({r["seed"] for r in rows})
    split = seeds[len(seeds) // 2]
    train_seeds = {s for s in seeds if s < split}
    test_seeds = {s for s in seeds if s >= split}

    summaries: list[dict] = []
    for source in sorted({r["source_arm"] for r in rows}):
        for key in sorted({r["key"] for r in rows}):
            for angle in sorted({r["angle_multiplier"] for r in rows}):
                sub = [r for r in rows if r["source_arm"] == source and r["key"] == key and r["angle_multiplier"] == angle]
                by = {(r["seed"], r["label"]): r for r in sub}
                train_margins = []
                test_margins = []
                for seed in seeds:
                    margin = by[(seed, "plus")]["coherence_attributable_readout_W"] - by[(seed, "minus")]["coherence_attributable_readout_W"]
                    (train_margins if seed in train_seeds else test_margins).append(margin)
                train_mean = sum(train_margins) / len(train_margins)
                if abs(train_mean) <= 1e-12:
                    orientation = "no_signal"
                    test_correct = 0
                    test_tie = len(test_margins)
                    accuracy = 0.5
                else:
                    orientation = "plus_gt_minus" if train_mean > 0 else "minus_gt_plus"
                    test_correct = 0
                    test_tie = 0
                    for margin in test_margins:
                        if abs(margin) <= 1e-12:
                            test_tie += 1
                        elif (margin > 0 and orientation == "plus_gt_minus") or (margin < 0 and orientation == "minus_gt_plus"):
                            test_correct += 1
                    accuracy = test_correct / max(1, len(test_margins) - test_tie)
                summaries.append({
                    "source_arm": source,
                    "key": key,
                    "angle_multiplier": angle,
                    "train_seed_count": len(train_margins),
                    "test_seed_count": len(test_margins),
                    "train_mean_plus_minus_margin": train_mean,
                    "test_mean_plus_minus_margin": sum(test_margins) / len(test_margins),
                    "test_mean_abs_margin": sum(abs(x) for x in test_margins) / len(test_margins),
                    "learned_orientation": orientation,
                    "test_correct_count": test_correct,
                    "test_tie_count": test_tie,
                    "test_accuracy": accuracy,
                    "oracle_accuracy": 1.0,
                    "random_accuracy": 0.5,
                })

    write_csv(out / f"{EXPERIMENT}_summary.csv", summaries)
    manifest = {
        "experiment": EXPERIMENT,
        "status": "completed",
        "input": str(Path(args.seed_summary)),
        "train_seed_count": len(train_seeds),
        "test_seed_count": len(test_seeds),
        "claim_ceiling": "model-level downstream branch utility from delayed phase-key residuals; no quantum advantage claim",
    }
    (out / f"{EXPERIMENT}_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# Q-cell phase-key controller utility v0", "", "Date: 2026-07-10 JST", "", "## Summary", ""]
    for row in summaries:
        lines.append(
            f"- {row['source_arm']} / {row['key']} / angle `{row['angle_multiplier']:.1f}`: test accuracy `{row['test_accuracy']:.6f}`, orientation `{row['learned_orientation']}`, test abs margin `{row['test_mean_abs_margin']:.9f}`, correct/tie `{row['test_correct_count']}/{row['test_tie_count']}`."
        )
    lines += ["", "## Claim Ceiling", "", manifest["claim_ceiling"], ""]
    (out / f"{EXPERIMENT}_report_2026-07-10.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
