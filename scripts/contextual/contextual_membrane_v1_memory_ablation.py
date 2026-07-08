#!/usr/bin/env python3
"""
contextual_membrane_v1_memory_ablation

Layer: CONTEXTUAL_COMPONENT

Tests whether contextual membrane decisions require dynamic memory, including
observed-path residue, unchosen-alternative residue, and context-order history.

This is a component-level memory ablation test, not a quantum-specific claim.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Dict, List, Any, Tuple

import numpy as np

CONTEXTS = ["identity", "path", "boundary", "history"]
OBJECTS = ["A", "B", "P", "Q"]

BASE = {"A": 0.60, "B": 0.24, "P": 0.48, "Q": 0.36}
BIAS = {
    "identity": {"A": 0.16, "B": -0.08, "P": 0.14, "Q": -0.02},
    "path": {"A": -0.10, "B": 0.20, "P": -0.04, "Q": 0.04},
    "boundary": {"A": -0.06, "B": -0.18, "P": 0.02, "Q": 0.18},
    "history": {"A": 0.04, "B": 0.00, "P": 0.12, "Q": 0.16},
}

DEFAULT_CONFIG = {
    "seed": 20260708,
    "steps": 512,
    "burn": 64,
    "memory_decay": 0.965,
    "memory_gain": 0.52,
    "alternative_gain": 0.30,
    "transition_memory_gain": 0.20,
    "incompatibility_penalty": 0.20,
    "quality_leak": 0.018,
    "quality_repair": 0.026,
    "release_rate": 0.085,
    "reservoir_decay": 0.012,
    "min_score": 0.02,
    "max_score": 0.98,
}


def compat_graph() -> Dict[Tuple[str, str], bool]:
    g = {(a, b): a == b for a in CONTEXTS for b in CONTEXTS}
    for pair in [("identity", "history"), ("history", "identity"), ("path", "boundary"), ("boundary", "path")]:
        g[pair] = True
    return g


def clip(x: float, cfg: Dict[str, Any]) -> float:
    return float(np.clip(x, cfg["min_score"], cfg["max_score"]))


def mean(xs) -> float:
    xs = list(xs)
    return float(sum(xs) / len(xs)) if xs else 0.0


def mae(xs, ys) -> float:
    return mean(abs(float(a) - float(b)) for a, b in zip(xs, ys))


def generate_events(cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate a sequence with repeated motifs so memory can matter."""
    rng = np.random.default_rng(cfg["seed"])
    events: List[Dict[str, Any]] = []
    ctx = CONTEXTS[int(rng.integers(0, len(CONTEXTS)))]
    obj = OBJECTS[int(rng.integers(0, len(OBJECTS)))]
    compatible_neighbors = {
        "identity": ["identity", "history"],
        "history": ["history", "identity"],
        "path": ["path", "boundary"],
        "boundary": ["boundary", "path"],
    }
    incompatible_neighbors = {
        "identity": ["path", "boundary"],
        "history": ["path", "boundary"],
        "path": ["identity", "history"],
        "boundary": ["identity", "history"],
    }
    object_transitions = {
        "A": [0.38, 0.07, 0.43, 0.12],
        "B": [0.18, 0.42, 0.08, 0.32],
        "P": [0.30, 0.05, 0.48, 0.17],
        "Q": [0.22, 0.22, 0.18, 0.38],
    }
    for t in range(cfg["steps"]):
        if t > 0:
            if rng.random() < 0.73:
                choices = compatible_neighbors[ctx]
            else:
                choices = incompatible_neighbors[ctx]
            ctx = choices[int(rng.integers(0, len(choices)))]
            obj = OBJECTS[int(rng.choice(len(OBJECTS), p=object_transitions[obj]))]
        events.append({"t": t, "context": ctx, "object": obj, "u": float(rng.random())})
    return events


def same_context_replay(events: List[Dict[str, Any]], seed: int) -> List[Dict[str, Any]]:
    """Keep context sequence and u timing fixed; shuffle objects within each context."""
    rng = np.random.default_rng(seed)
    out = [dict(e) for e in events]
    for ctx in CONTEXTS:
        idx = [i for i, e in enumerate(events) if e["context"] == ctx]
        objs = [events[i]["object"] for i in idx]
        rng.shuffle(objs)
        for i, obj in zip(idx, objs):
            out[i]["object"] = obj
    return out


def same_transition_replay(events: List[Dict[str, Any]], seed: int) -> List[Dict[str, Any]]:
    """Preserve compatible/incompatible transition mask and object multiset, but alter concrete context order."""
    rng = np.random.default_rng(seed)
    compat = compat_graph()
    mask = []
    prev = None
    for e in events:
        c = e["context"]
        mask.append(True if prev is None else compat[(prev, c)])
        prev = c

    compatible_neighbors = {
        "identity": ["identity", "history"],
        "history": ["history", "identity"],
        "path": ["path", "boundary"],
        "boundary": ["boundary", "path"],
    }
    incompatible_neighbors = {
        "identity": ["path", "boundary"],
        "history": ["path", "boundary"],
        "path": ["identity", "history"],
        "boundary": ["identity", "history"],
    }

    out = [dict(e) for e in events]
    ctx = CONTEXTS[int(rng.integers(0, len(CONTEXTS)))]
    contexts = []
    for i, keep_compatible in enumerate(mask):
        if i == 0:
            contexts.append(ctx)
            continue
        choices = compatible_neighbors[ctx] if keep_compatible else incompatible_neighbors[ctx]
        ctx = choices[int(rng.integers(0, len(choices)))]
        contexts.append(ctx)

    objs = [e["object"] for e in events]
    rng.shuffle(objs)
    for e, c, o in zip(out, contexts, objs):
        e["context"] = c
        e["object"] = o
    return out


def variant_config(cfg: Dict[str, Any], variant: str) -> Dict[str, Any]:
    vcfg = dict(cfg)
    if variant == "full":
        pass
    elif variant == "no_memory":
        vcfg["memory_gain"] = 0.0
        vcfg["alternative_gain"] = 0.0
        vcfg["transition_memory_gain"] = 0.0
    elif variant == "low_memory_decay":
        vcfg["memory_decay"] = 0.35
    elif variant == "high_memory_decay":
        vcfg["memory_decay"] = 0.992
    elif variant in {"same_context_replay", "same_transition_replay"}:
        pass
    else:
        raise ValueError(variant)
    return vcfg


def memory_terms(memory: Dict[str, float], ctx: str, obj: str, prev: str | None, cfg: Dict[str, Any]) -> float:
    seen_pass = memory.get(f"seen:{ctx}:{obj}:PASS", 0.0)
    seen_block = memory.get(f"seen:{ctx}:{obj}:BLOCK", 0.0)
    alt_pass = memory.get(f"alt:{ctx}:{obj}:PASS", 0.0)
    alt_block = memory.get(f"alt:{ctx}:{obj}:BLOCK", 0.0)
    transition = 0.0 if prev is None else memory.get(f"trans:{prev}->{ctx}", 0.0)
    return (
        cfg["memory_gain"] * math.tanh((seen_pass - 0.65 * seen_block) / 3.0)
        + cfg["alternative_gain"] * math.tanh((0.85 * alt_pass - alt_block) / 3.0)
        + cfg["transition_memory_gain"] * math.tanh(transition / 3.0)
    )


def run_variant(variant: str, cfg: Dict[str, Any], base_events: List[Dict[str, Any]]) -> Dict[str, Any]:
    vcfg = variant_config(cfg, variant)
    if variant == "same_context_replay":
        events = same_context_replay(base_events, cfg["seed"] + 1101)
    elif variant == "same_transition_replay":
        events = same_transition_replay(base_events, cfg["seed"] + 2202)
    else:
        events = [dict(e) for e in base_events]

    compat = compat_graph()
    memory: Dict[str, float] = {}
    rows: List[Dict[str, Any]] = []
    prev = None
    reservoir = 0.0
    quality = 1.0
    cumulative_release = 0.0

    for ev in events:
        ctx, obj = ev["context"], ev["object"]
        compatible = True if prev is None else compat[(prev, ctx)]
        memory = {k: v * vcfg["memory_decay"] for k, v in memory.items() if abs(v * vcfg["memory_decay"]) > 1e-9}

        score = BASE[obj] + BIAS.get(ctx, {}).get(obj, 0.0)
        score += memory_terms(memory, ctx, obj, prev, vcfg)
        if not compatible:
            score -= vcfg["incompatibility_penalty"]
        score = clip(score, vcfg)
        passed = bool(ev["u"] < score)

        if passed:
            reservoir += (0.65 + 0.25 * score) * quality
            quality = min(1.4, quality + vcfg["quality_repair"] * (1.0 - quality + 0.15))
            memory[f"seen:{ctx}:{obj}:PASS"] = memory.get(f"seen:{ctx}:{obj}:PASS", 0.0) + 1.0
            memory[f"alt:{ctx}:{obj}:BLOCK"] = memory.get(f"alt:{ctx}:{obj}:BLOCK", 0.0) + 0.45
        else:
            quality = max(0.25, quality - vcfg["quality_leak"] * (1.0 + (0.5 if not compatible else 0.0)))
            memory[f"seen:{ctx}:{obj}:BLOCK"] = memory.get(f"seen:{ctx}:{obj}:BLOCK", 0.0) + 1.0
            memory[f"alt:{ctx}:{obj}:PASS"] = memory.get(f"alt:{ctx}:{obj}:PASS", 0.0) + 0.45

        if prev is not None:
            memory[f"trans:{prev}->{ctx}"] = memory.get(f"trans:{prev}->{ctx}", 0.0) + 1.0
        if not compatible and prev is not None:
            memory[f"incompat:{prev}->{ctx}"] = memory.get(f"incompat:{prev}->{ctx}", 0.0) + 1.0

        release = reservoir * vcfg["release_rate"] * quality
        reservoir = max(0.0, reservoir - release - vcfg["reservoir_decay"] * reservoir)
        cumulative_release += release

        rows.append({
            "t": ev["t"],
            "variant": variant,
            "context": ctx,
            "object": obj,
            "previous_context": prev or "NONE",
            "compatible_with_previous": compatible,
            "u": round(ev["u"], 12),
            "passage_score": round(score, 9),
            "passed": passed,
            "quality": round(quality, 9),
            "release": round(release, 9),
            "reservoir": round(reservoir, 9),
            "cumulative_release": round(cumulative_release, 9),
            "memory_size": len(memory),
        })
        prev = ctx
    return {"variant": variant, "rows": rows}


def summarize(run: Dict[str, Any], full_rows: List[Dict[str, Any]] | None, cfg: Dict[str, Any]) -> Dict[str, Any]:
    rows = run["rows"][cfg["burn"]:]
    if full_rows is not None:
        full_post = full_rows[cfg["burn"]:]
        event_match = mean(1.0 if r["passed"] == f["passed"] else 0.0 for r, f in zip(rows, full_post))
        timing_flip_rate = 1.0 - event_match
        score_mae = mae([r["passage_score"] for r in rows], [f["passage_score"] for f in full_post])
        quality_mae = mae([r["quality"] for r in rows], [f["quality"] for f in full_post])
        release_mae = mae([r["release"] for r in rows], [f["release"] for f in full_post])
        reservoir_mae = mae([r["reservoir"] for r in rows], [f["reservoir"] for f in full_post])
        cumulative_release_delta = rows[-1]["cumulative_release"] - full_post[-1]["cumulative_release"]
    else:
        event_match = None
        timing_flip_rate = None
        score_mae = None
        quality_mae = None
        release_mae = None
        reservoir_mae = None
        cumulative_release_delta = None

    compatible = [r for r in rows if r["compatible_with_previous"]]
    incompatible = [r for r in rows if not r["compatible_with_previous"]]
    pass_rate = mean(1.0 if r["passed"] else 0.0 for r in rows)
    pass_times = [r["t"] for r in rows if r["passed"]]
    inter_pass = [b - a for a, b in zip(pass_times, pass_times[1:])]
    return {
        "variant": run["variant"],
        "n_post_burn": len(rows),
        "pass_rate": round(pass_rate, 9),
        "mean_score": round(mean(r["passage_score"] for r in rows), 9),
        "compatible_pass_rate": round(mean(1.0 if r["passed"] else 0.0 for r in compatible), 9),
        "incompatible_pass_rate": round(mean(1.0 if r["passed"] else 0.0 for r in incompatible), 9),
        "compatibility_pass_gap": round(mean(1.0 if r["passed"] else 0.0 for r in compatible) - mean(1.0 if r["passed"] else 0.0 for r in incompatible), 9),
        "mean_quality": round(mean(r["quality"] for r in rows), 9),
        "mean_release": round(mean(r["release"] for r in rows), 9),
        "final_reservoir": round(rows[-1]["reservoir"], 9),
        "final_cumulative_release": round(rows[-1]["cumulative_release"], 9),
        "mean_inter_pass_interval": round(mean(inter_pass), 9),
        "event_match_to_full": None if event_match is None else round(event_match, 9),
        "timing_flip_rate_vs_full": None if timing_flip_rate is None else round(timing_flip_rate, 9),
        "score_mae_to_full": None if score_mae is None else round(score_mae, 9),
        "quality_mae_to_full": None if quality_mae is None else round(quality_mae, 9),
        "release_mae_to_full": None if release_mae is None else round(release_mae, 9),
        "reservoir_mae_to_full": None if reservoir_mae is None else round(reservoir_mae, 9),
        "cumulative_release_delta_vs_full": None if cumulative_release_delta is None else round(cumulative_release_delta, 9),
        "final_memory_size": rows[-1]["memory_size"],
    }


def run(cfg: Dict[str, Any]) -> Dict[str, Any]:
    base_events = generate_events(cfg)
    variants = ["full", "no_memory", "low_memory_decay", "high_memory_decay", "same_context_replay", "same_transition_replay"]
    runs = {v: run_variant(v, cfg, base_events) for v in variants}
    full_rows = runs["full"]["rows"]
    summaries = [summarize(runs[v], None if v == "full" else full_rows, cfg) for v in variants]
    lookup = {s["variant"]: s for s in summaries}

    criteria = {
        "no_memory_event_match_to_full_le_0_90": lookup["no_memory"]["event_match_to_full"] <= 0.90,
        "no_memory_score_mae_to_full_ge_0_05": lookup["no_memory"]["score_mae_to_full"] >= 0.05,
        "no_memory_release_mae_to_full_ge_0_01": lookup["no_memory"]["release_mae_to_full"] >= 0.01,
        "low_memory_differs_from_full_score_mae_ge_0_02": lookup["low_memory_decay"]["score_mae_to_full"] >= 0.02,
        "same_context_replay_event_match_to_full_le_0_92": lookup["same_context_replay"]["event_match_to_full"] <= 0.92,
        "same_transition_replay_event_match_to_full_le_0_92": lookup["same_transition_replay"]["event_match_to_full"] <= 0.92,
    }
    verdict = "PASS_MEMORY_DEPENDENT_BOUNDARY" if all(criteria.values()) else "FAIL_OR_MIXED_MEMORY_CLAIM"

    return {
        "experiment": "contextual_membrane_v1_memory_ablation",
        "date": "2026-07-08",
        "layer": "CONTEXTUAL_COMPONENT",
        "seed": cfg["seed"],
        "config": cfg,
        "model": "contextual membrane with memory ablation and downstream quality/release trajectory metrics",
        "variants": variants,
        "summaries": summaries,
        "criteria": criteria,
        "verdict": verdict,
        "base_event_count": len(base_events),
        "base_event_sample_first_32": base_events[:32],
        "row_sample_by_variant_first_16": {v: runs[v]["rows"][:16] for v in variants},
        "claim_boundary": [
            "This is a component-level memory ablation test.",
            "PASS means the implemented membrane's decisions and downstream trajectory depend on dynamic memory under the stated controls.",
            "This is not a quantum-specific claim and not a formal contextuality witness.",
            "No biological, consciousness, metabolism, self-repair, or physical matter synthesis claim is made."
        ],
    }


def write_summary_csv(result: Dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    summaries = result["summaries"]
    fields = list(summaries[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(summaries)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20260708)
    ap.add_argument("--steps", type=int, default=512)
    ap.add_argument("--out", type=Path, default=Path("data/contextual/contextual_membrane_v1_memory_ablation_seed20260708.json"))
    ap.add_argument("--csv", type=Path, default=Path("data/contextual/contextual_membrane_v1_memory_ablation_seed20260708_summary.csv"))
    args = ap.parse_args()

    cfg = dict(DEFAULT_CONFIG)
    cfg["seed"] = args.seed
    cfg["steps"] = args.steps
    result = run(cfg)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_summary_csv(result, args.csv)
    print(json.dumps({
        "experiment": result["experiment"],
        "verdict": result["verdict"],
        "summaries": result["summaries"],
        "criteria": result["criteria"],
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
