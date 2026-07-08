#!/usr/bin/env python3
"""
contextual_membrane_v2_counterfactual_residue

Layer: CONTEXTUAL_COMPONENT

Tests whether unchosen alternatives leave residue that changes later contextual
membrane decisions.

This is a component-level counterfactual-residue test, not a quantum-specific
claim and not a formal contextuality witness.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

CONTEXTS = ["identity", "path", "boundary", "history"]
OBJECTS = ["A", "B", "P", "Q"]

BASE = {"A": 0.56, "B": 0.26, "P": 0.48, "Q": 0.40}
BIAS = {
    "identity": {"A": 0.14, "B": -0.08, "P": 0.12, "Q": -0.02},
    "path": {"A": -0.10, "B": 0.18, "P": -0.03, "Q": 0.04},
    "boundary": {"A": -0.06, "B": -0.14, "P": 0.02, "Q": 0.16},
    "history": {"A": 0.02, "B": 0.00, "P": 0.12, "Q": 0.14},
}

DEFAULT_CONFIG: Dict[str, Any] = {
    "seed": 20260708,
    "steps": 512,
    "burn": 64,
    "memory_decay": 0.96,
    "observed_gain": 0.24,
    "counterfactual_gain": 0.46,
    "transition_gain": 0.06,
    "incompatibility_penalty": 0.12,
    "quality_leak": 0.014,
    "quality_repair": 0.020,
    "release_rate": 0.080,
    "reservoir_decay": 0.012,
    "min_score": 0.02,
    "max_score": 0.98,
}


def compat_graph() -> Dict[Tuple[str, str], bool]:
    graph = {(a, b): a == b for a in CONTEXTS for b in CONTEXTS}
    for pair in [("identity", "history"), ("history", "identity"), ("path", "boundary"), ("boundary", "path")]:
        graph[pair] = True
    return graph


def mean(xs) -> float:
    xs = list(xs)
    return float(sum(xs) / len(xs)) if xs else 0.0


def mae(xs, ys) -> float:
    return mean(abs(float(a) - float(b)) for a, b in zip(xs, ys))


def clip(x: float, cfg: Dict[str, Any]) -> float:
    return float(np.clip(x, cfg["min_score"], cfg["max_score"]))


def generate_events(cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate repeated context/object probes so counterfactual residue can matter."""
    rng = np.random.default_rng(cfg["seed"])
    events: List[Dict[str, Any]] = []
    context = CONTEXTS[int(rng.integers(0, len(CONTEXTS)))]
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
        "A": [0.32, 0.07, 0.46, 0.15],
        "B": [0.15, 0.43, 0.10, 0.32],
        "P": [0.32, 0.05, 0.46, 0.17],
        "Q": [0.20, 0.22, 0.18, 0.40],
    }
    scheduled: Dict[int, Tuple[str, str]] = {}
    t = 0
    while t < cfg["steps"]:
        if t in scheduled:
            context, obj = scheduled.pop(t)
        else:
            if t > 0:
                choices = compatible_neighbors[context] if rng.random() < 0.70 else incompatible_neighbors[context]
                context = choices[int(rng.integers(0, len(choices)))]
                obj = OBJECTS[int(rng.choice(len(OBJECTS), p=object_transitions[obj]))]
        u = float(rng.beta(2.2, 2.2)) if rng.random() < 0.75 else float(rng.random())
        events.append({"t": t, "context": context, "object": obj, "u": u})
        if rng.random() < 0.42:
            lag = int(rng.integers(2, 6))
            if t + lag < cfg["steps"]:
                scheduled[t + lag] = (context, obj)
        t += 1
    return events[: cfg["steps"]]


def variant_config(cfg: Dict[str, Any], variant: str) -> Dict[str, Any]:
    vcfg = dict(cfg)
    if variant == "full_observed_and_counterfactual":
        pass
    elif variant == "observed_only":
        vcfg["counterfactual_gain"] = 0.0
    elif variant == "counterfactual_only":
        vcfg["observed_gain"] = 0.0
    elif variant == "no_residue":
        vcfg["observed_gain"] = 0.0
        vcfg["counterfactual_gain"] = 0.0
        vcfg["transition_gain"] = 0.0
    elif variant == "counterfactual_sign_flip":
        vcfg["counterfactual_gain"] = -abs(vcfg["counterfactual_gain"])
    elif variant == "counterfactual_shuffle":
        pass
    else:
        raise ValueError(variant)
    return vcfg


def memory_terms(memory: Dict[str, float], context: str, obj: str, previous_context: str | None, cfg: Dict[str, Any], variant: str) -> Tuple[float, float, float, float]:
    obs_pass = memory.get(f"obs:{context}:{obj}:PASS", 0.0)
    obs_block = memory.get(f"obs:{context}:{obj}:BLOCK", 0.0)
    if variant == "counterfactual_shuffle":
        wrong_obj = OBJECTS[(OBJECTS.index(obj) + 1) % len(OBJECTS)]
        cf_pass = memory.get(f"cf:{context}:{wrong_obj}:PASS", 0.0)
        cf_block = memory.get(f"cf:{context}:{wrong_obj}:BLOCK", 0.0)
    else:
        cf_pass = memory.get(f"cf:{context}:{obj}:PASS", 0.0)
        cf_block = memory.get(f"cf:{context}:{obj}:BLOCK", 0.0)
    transition = 0.0 if previous_context is None else memory.get(f"trans:{previous_context}->{context}", 0.0)
    observed_term = cfg["observed_gain"] * math.tanh((obs_pass - obs_block) / 2.5)
    counterfactual_term = cfg["counterfactual_gain"] * math.tanh((cf_pass - cf_block) / 2.5)
    transition_term = cfg["transition_gain"] * math.tanh(transition / 3.0)
    return observed_term + counterfactual_term + transition_term, observed_term, counterfactual_term, transition_term


def run_variant(variant: str, cfg: Dict[str, Any], events: List[Dict[str, Any]]) -> Dict[str, Any]:
    vcfg = variant_config(cfg, variant)
    compatibility = compat_graph()
    memory: Dict[str, float] = {}
    rows: List[Dict[str, Any]] = []
    previous_context: str | None = None
    quality = 1.0
    reservoir = 0.0
    cumulative_release = 0.0
    last_same_outcome: Dict[Tuple[str, str], str] = {}
    last_same_t: Dict[Tuple[str, str], int] = {}

    for event in events:
        context, obj, u = event["context"], event["object"], event["u"]
        compatible = True if previous_context is None else compatibility[(previous_context, context)]
        memory = {k: v * vcfg["memory_decay"] for k, v in memory.items() if abs(v * vcfg["memory_decay"]) > 1e-9}
        mem_total, observed_term, counterfactual_term, transition_term = memory_terms(memory, context, obj, previous_context, vcfg, variant)
        score = BASE[obj] + BIAS.get(context, {}).get(obj, 0.0) + mem_total
        if not compatible:
            score -= vcfg["incompatibility_penalty"]
        score = clip(score, vcfg)
        passed = bool(u < score)
        key = (context, obj)
        previous_same_key_outcome = last_same_outcome.get(key, "NONE")
        previous_same_key_lag = -1 if key not in last_same_t else event["t"] - last_same_t[key]

        if passed:
            reservoir += (0.60 + 0.25 * score) * quality
            quality = min(1.35, quality + vcfg["quality_repair"] * (1.0 - quality + 0.12))
            memory[f"obs:{context}:{obj}:PASS"] = memory.get(f"obs:{context}:{obj}:PASS", 0.0) + 1.0
            memory[f"cf:{context}:{obj}:BLOCK"] = memory.get(f"cf:{context}:{obj}:BLOCK", 0.0) + 1.0
            outcome = "PASS"
        else:
            quality = max(0.20, quality - vcfg["quality_leak"] * (1.0 + (0.4 if not compatible else 0.0)))
            memory[f"obs:{context}:{obj}:BLOCK"] = memory.get(f"obs:{context}:{obj}:BLOCK", 0.0) + 1.0
            memory[f"cf:{context}:{obj}:PASS"] = memory.get(f"cf:{context}:{obj}:PASS", 0.0) + 1.0
            outcome = "BLOCK"

        if previous_context is not None:
            memory[f"trans:{previous_context}->{context}"] = memory.get(f"trans:{previous_context}->{context}", 0.0) + 1.0

        release = reservoir * vcfg["release_rate"] * quality
        reservoir = max(0.0, reservoir - release - vcfg["reservoir_decay"] * reservoir)
        cumulative_release += release

        rows.append({
            "t": event["t"],
            "variant": variant,
            "context": context,
            "object": obj,
            "previous_context": previous_context or "NONE",
            "compatible_with_previous": compatible,
            "u": round(u, 12),
            "passage_score": round(score, 9),
            "observed_term": round(observed_term, 9),
            "counterfactual_term": round(counterfactual_term, 9),
            "transition_term": round(transition_term, 9),
            "passed": passed,
            "observed_output": outcome,
            "unobserved_alternative": "BLOCK" if passed else "PASS",
            "previous_same_key_outcome": previous_same_key_outcome,
            "previous_same_key_lag": previous_same_key_lag,
            "quality": round(quality, 9),
            "release": round(release, 9),
            "reservoir": round(reservoir, 9),
            "cumulative_release": round(cumulative_release, 9),
            "memory_size": len(memory),
        })
        last_same_outcome[key] = outcome
        last_same_t[key] = event["t"]
        previous_context = context
    return {"variant": variant, "rows": rows}


def summarize(run: Dict[str, Any], full_rows: List[Dict[str, Any]] | None, observed_only_rows: List[Dict[str, Any]] | None, cfg: Dict[str, Any]) -> Dict[str, Any]:
    rows = run["rows"][cfg["burn"] :]
    if full_rows is not None:
        full_post = full_rows[cfg["burn"] :]
        event_match = mean(1.0 if r["passed"] == f["passed"] else 0.0 for r, f in zip(rows, full_post))
        score_mae = mae([r["passage_score"] for r in rows], [f["passage_score"] for f in full_post])
        release_mae = mae([r["release"] for r in rows], [f["release"] for f in full_post])
        quality_mae = mae([r["quality"] for r in rows], [f["quality"] for f in full_post])
        cumulative_release_delta = rows[-1]["cumulative_release"] - full_post[-1]["cumulative_release"]
    else:
        event_match = score_mae = release_mae = quality_mae = cumulative_release_delta = None

    if observed_only_rows is not None:
        observed_post = observed_only_rows[cfg["burn"] :]
        deltas = [r["passage_score"] - o["passage_score"] for r, o in zip(rows, observed_post)]
        after_block = [d for d, r in zip(deltas, rows) if r["previous_same_key_outcome"] == "BLOCK"]
        after_pass = [d for d, r in zip(deltas, rows) if r["previous_same_key_outcome"] == "PASS"]
        after_block_delta = mean(after_block)
        after_pass_delta = mean(after_pass)
        polarity_probe = after_block_delta - after_pass_delta
    else:
        after_block_delta = after_pass_delta = polarity_probe = None

    return {
        "variant": run["variant"],
        "n_post_burn": len(rows),
        "pass_rate": round(mean(1.0 if r["passed"] else 0.0 for r in rows), 9),
        "mean_score": round(mean(r["passage_score"] for r in rows), 9),
        "mean_counterfactual_term": round(mean(r["counterfactual_term"] for r in rows), 9),
        "mean_quality": round(mean(r["quality"] for r in rows), 9),
        "mean_release": round(mean(r["release"] for r in rows), 9),
        "final_cumulative_release": round(rows[-1]["cumulative_release"], 9),
        "event_match_to_full": None if event_match is None else round(event_match, 9),
        "score_mae_to_full": None if score_mae is None else round(score_mae, 9),
        "release_mae_to_full": None if release_mae is None else round(release_mae, 9),
        "quality_mae_to_full": None if quality_mae is None else round(quality_mae, 9),
        "cumulative_release_delta_vs_full": None if cumulative_release_delta is None else round(cumulative_release_delta, 9),
        "cf_delta_after_prior_block_vs_observed_only": None if after_block_delta is None else round(after_block_delta, 9),
        "cf_delta_after_prior_pass_vs_observed_only": None if after_pass_delta is None else round(after_pass_delta, 9),
        "counterfactual_polarity_probe": None if polarity_probe is None else round(polarity_probe, 9),
        "final_memory_size": rows[-1]["memory_size"],
    }


def run(cfg: Dict[str, Any]) -> Dict[str, Any]:
    events = generate_events(cfg)
    variants = [
        "full_observed_and_counterfactual",
        "observed_only",
        "counterfactual_only",
        "no_residue",
        "counterfactual_sign_flip",
        "counterfactual_shuffle",
    ]
    runs = {variant: run_variant(variant, cfg, events) for variant in variants}
    full_rows = runs["full_observed_and_counterfactual"]["rows"]
    observed_only_rows = runs["observed_only"]["rows"]
    summaries = [summarize(runs[v], None if v == "full_observed_and_counterfactual" else full_rows, observed_only_rows, cfg) for v in variants]
    lookup = {s["variant"]: s for s in summaries}
    criteria = {
        "observed_only_event_match_to_full_le_0_92": lookup["observed_only"]["event_match_to_full"] <= 0.92,
        "observed_only_score_mae_to_full_ge_0_03": lookup["observed_only"]["score_mae_to_full"] >= 0.03,
        "observed_only_release_mae_to_full_ge_0_01": lookup["observed_only"]["release_mae_to_full"] >= 0.01,
        "full_counterfactual_polarity_probe_ge_0_08": lookup["full_observed_and_counterfactual"]["counterfactual_polarity_probe"] >= 0.08,
        "counterfactual_sign_flip_event_match_to_full_le_0_85": lookup["counterfactual_sign_flip"]["event_match_to_full"] <= 0.85,
        "counterfactual_shuffle_event_match_to_full_le_0_92": lookup["counterfactual_shuffle"]["event_match_to_full"] <= 0.92,
    }
    return {
        "experiment": "contextual_membrane_v2_counterfactual_residue",
        "date": "2026-07-08",
        "layer": "CONTEXTUAL_COMPONENT",
        "seed": cfg["seed"],
        "config": cfg,
        "variants": variants,
        "summaries": summaries,
        "criteria": criteria,
        "verdict": "PASS_COUNTERFACTUAL_RESIDUE" if all(criteria.values()) else "FAIL_OR_MIXED_COUNTERFACTUAL_RESIDUE",
        "base_event_count": len(events),
        "base_event_sample_first_32": events[:32],
        "row_sample_by_variant_first_12": {v: runs[v]["rows"][:12] for v in variants},
        "claim_boundary": [
            "This is a component-level counterfactual-residue test.",
            "PASS means the implemented membrane's later decisions depend on unchosen-alternative residue under the stated ablations.",
            "This is not a quantum-specific claim and not a formal contextuality witness.",
            "No biological, consciousness, metabolism, self-repair, or physical matter synthesis claim is made.",
        ],
    }


def write_summary_csv(result: Dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    summaries = result["summaries"]
    fields = list(summaries[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(summaries)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260708)
    parser.add_argument("--steps", type=int, default=512)
    parser.add_argument("--out", type=Path, default=Path("data/contextual/contextual_membrane_v2_counterfactual_residue_seed20260708.json"))
    parser.add_argument("--csv", type=Path, default=Path("data/contextual/contextual_membrane_v2_counterfactual_residue_seed20260708_summary.csv"))
    args = parser.parse_args()

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
