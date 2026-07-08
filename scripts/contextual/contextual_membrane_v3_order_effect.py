#!/usr/bin/env python3
"""
contextual_membrane_v3_order_effect

Layer: CONTEXTUAL_COMPONENT

Tests whether the same context/object/u event multiset changes the contextual
membrane depending only on order.

This is a component-level order-effect test, not a quantum-specific claim and
not a formal contextuality witness.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
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
    "memory_decay": 0.965,
    "observed_gain": 0.22,
    "counterfactual_gain": 0.38,
    "transition_gain": 0.26,
    "order_trace_gain": 0.18,
    "incompatibility_penalty": 0.14,
    "quality_leak": 0.014,
    "quality_repair": 0.021,
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
    """Generate repeated events; order variants reuse the exact same event multiset."""
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
    for t in range(cfg["steps"]):
        if t in scheduled:
            context, obj = scheduled.pop(t)
        else:
            if t > 0:
                choices = compatible_neighbors[context] if rng.random() < 0.70 else incompatible_neighbors[context]
                context = choices[int(rng.integers(0, len(choices)))]
                obj = OBJECTS[int(rng.choice(len(OBJECTS), p=object_transitions[obj]))]

        u = float(rng.beta(2.1, 2.1)) if rng.random() < 0.75 else float(rng.random())
        events.append({"t": t, "context": context, "object": obj, "u": u})

        if rng.random() < 0.38:
            lag = int(rng.integers(2, 7))
            if t + lag < cfg["steps"]:
                scheduled[t + lag] = (context, obj)

    return events[: cfg["steps"]]


def order_variant(events: List[Dict[str, Any]], variant: str, seed: int) -> List[Dict[str, Any]]:
    ev = [dict(e) for e in events]
    rng = np.random.default_rng(seed + 3000)

    if variant == "original_order":
        out = ev
    elif variant == "reverse_order":
        out = list(reversed(ev))
    elif variant == "random_order_same_multiset":
        out = ev[:]
        rng.shuffle(out)
    elif variant == "block_shuffle_order":
        block = 8
        blocks = [ev[i : i + block] for i in range(0, len(ev), block)]
        rng.shuffle(blocks)
        out = [e for block_items in blocks for e in block_items]
    elif variant == "context_sorted_order":
        order = {context: i for i, context in enumerate(CONTEXTS)}
        out = sorted(ev, key=lambda e: (order[e["context"]], e["object"], e["u"]))
    elif variant == "compatible_cluster_order":
        group1 = [e for e in ev if e["context"] in ("identity", "history")]
        group2 = [e for e in ev if e["context"] in ("path", "boundary")]
        rng.shuffle(group1)
        rng.shuffle(group2)
        out = []
        while group1 or group2:
            n1 = min(len(group1), int(rng.integers(3, 8)))
            for _ in range(n1):
                out.append(group1.pop())
            n2 = min(len(group2), int(rng.integers(3, 8)))
            for _ in range(n2):
                out.append(group2.pop())
        out = out[: len(ev)]
    else:
        raise ValueError(variant)

    return [
        {"t": i, "original_t": e["t"], "context": e["context"], "object": e["object"], "u": e["u"]}
        for i, e in enumerate(out)
    ]


def multiset_signature(events: List[Dict[str, Any]]) -> Counter:
    return Counter((e["context"], e["object"], round(e["u"], 12)) for e in events)


def memory_terms(
    memory: Dict[str, float],
    context: str,
    obj: str,
    previous_context: str | None,
    cfg: Dict[str, Any],
) -> Tuple[float, float, float, float, float]:
    obs_pass = memory.get(f"obs:{context}:{obj}:PASS", 0.0)
    obs_block = memory.get(f"obs:{context}:{obj}:BLOCK", 0.0)
    cf_pass = memory.get(f"cf:{context}:{obj}:PASS", 0.0)
    cf_block = memory.get(f"cf:{context}:{obj}:BLOCK", 0.0)
    transition = 0.0 if previous_context is None else memory.get(f"trans:{previous_context}->{context}", 0.0)
    order = memory.get(f"order:{context}", 0.0) - memory.get(f"antiorder:{context}", 0.0)

    observed_term = cfg["observed_gain"] * math.tanh((obs_pass - obs_block) / 2.5)
    counterfactual_term = cfg["counterfactual_gain"] * math.tanh((cf_pass - cf_block) / 2.5)
    transition_term = cfg["transition_gain"] * math.tanh(transition / 3.0)
    order_trace_term = cfg["order_trace_gain"] * math.tanh(order / 4.0)
    total = observed_term + counterfactual_term + transition_term + order_trace_term
    return total, observed_term, counterfactual_term, transition_term, order_trace_term


def run_variant(variant: str, base_events: List[Dict[str, Any]], cfg: Dict[str, Any]) -> Dict[str, Any]:
    events = order_variant(base_events, variant, cfg["seed"])
    compatibility = compat_graph()
    memory: Dict[str, float] = {}
    rows: List[Dict[str, Any]] = []
    previous_context: str | None = None
    quality = 1.0
    reservoir = 0.0
    cumulative_release = 0.0

    for event in events:
        context, obj, u = event["context"], event["object"], event["u"]
        compatible = True if previous_context is None else compatibility[(previous_context, context)]
        memory = {k: v * cfg["memory_decay"] for k, v in memory.items() if abs(v * cfg["memory_decay"]) > 1e-9}

        mem_total, observed_term, counterfactual_term, transition_term, order_trace_term = memory_terms(
            memory, context, obj, previous_context, cfg
        )

        score = BASE[obj] + BIAS.get(context, {}).get(obj, 0.0) + mem_total
        if not compatible:
            score -= cfg["incompatibility_penalty"]
        score = clip(score, cfg)
        passed = bool(u < score)

        if passed:
            reservoir += (0.60 + 0.25 * score) * quality
            quality = min(1.35, quality + cfg["quality_repair"] * (1.0 - quality + 0.12))
            memory[f"obs:{context}:{obj}:PASS"] = memory.get(f"obs:{context}:{obj}:PASS", 0.0) + 1.0
            memory[f"cf:{context}:{obj}:BLOCK"] = memory.get(f"cf:{context}:{obj}:BLOCK", 0.0) + 1.0
            memory[f"order:{context}"] = memory.get(f"order:{context}", 0.0) + 1.0
            outcome = "PASS"
        else:
            quality = max(0.20, quality - cfg["quality_leak"] * (1.0 + (0.4 if not compatible else 0.0)))
            memory[f"obs:{context}:{obj}:BLOCK"] = memory.get(f"obs:{context}:{obj}:BLOCK", 0.0) + 1.0
            memory[f"cf:{context}:{obj}:PASS"] = memory.get(f"cf:{context}:{obj}:PASS", 0.0) + 1.0
            memory[f"antiorder:{context}"] = memory.get(f"antiorder:{context}", 0.0) + 1.0
            outcome = "BLOCK"

        if previous_context is not None:
            memory[f"trans:{previous_context}->{context}"] = memory.get(f"trans:{previous_context}->{context}", 0.0) + 1.0

        release = reservoir * cfg["release_rate"] * quality
        reservoir = max(0.0, reservoir - release - cfg["reservoir_decay"] * reservoir)
        cumulative_release += release

        rows.append({
            "t": event["t"],
            "original_t": event["original_t"],
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
            "order_trace_term": round(order_trace_term, 9),
            "passed": passed,
            "observed_output": outcome,
            "quality": round(quality, 9),
            "release": round(release, 9),
            "reservoir": round(reservoir, 9),
            "cumulative_release": round(cumulative_release, 9),
            "memory_size": len(memory),
        })
        previous_context = context

    final_memory = {
        k: round(v, 9)
        for k, v in sorted(memory.items())
        if k.startswith(("obs:", "cf:", "trans:", "order:", "antiorder:"))
    }
    return {"variant": variant, "rows": rows, "final_memory": final_memory}


def l1_distance_dict(a: Dict[str, float], b: Dict[str, float]) -> float:
    keys = set(a) | set(b)
    return sum(abs(a.get(k, 0.0) - b.get(k, 0.0)) for k in keys) / max(1, len(keys))


def summarize(run: Dict[str, Any], original: Dict[str, Any] | None, cfg: Dict[str, Any]) -> Dict[str, Any]:
    rows = run["rows"][cfg["burn"]:]
    full_rows = original["rows"][cfg["burn"]:] if original else None

    if full_rows is not None:
        event_match = mean(1.0 if r["passed"] == f["passed"] else 0.0 for r, f in zip(rows, full_rows))
        score_mae = mae([r["passage_score"] for r in rows], [f["passage_score"] for f in full_rows])
        release_mae = mae([r["release"] for r in rows], [f["release"] for f in full_rows])
        quality_mae = mae([r["quality"] for r in rows], [f["quality"] for f in full_rows])
        cumulative_delta = rows[-1]["cumulative_release"] - full_rows[-1]["cumulative_release"]
        final_residue_l1 = l1_distance_dict(run["final_memory"], original["final_memory"])
        final_state_distance = math.sqrt(
            (rows[-1]["quality"] - full_rows[-1]["quality"]) ** 2
            + ((rows[-1]["reservoir"] - full_rows[-1]["reservoir"]) ** 2) / 25
            + ((rows[-1]["cumulative_release"] - full_rows[-1]["cumulative_release"]) ** 2) / 10000
            + (final_residue_l1 ** 2) / 100
        )
    else:
        event_match = None
        score_mae = None
        release_mae = None
        quality_mae = None
        cumulative_delta = None
        final_residue_l1 = None
        final_state_distance = None

    return {
        "variant": run["variant"],
        "n_post_burn": len(rows),
        "pass_rate": round(mean(1.0 if r["passed"] else 0.0 for r in rows), 9),
        "mean_score": round(mean(r["passage_score"] for r in rows), 9),
        "mean_order_trace_term": round(mean(r["order_trace_term"] for r in rows), 9),
        "mean_quality": round(mean(r["quality"] for r in rows), 9),
        "mean_release": round(mean(r["release"] for r in rows), 9),
        "final_quality": round(rows[-1]["quality"], 9),
        "final_reservoir": round(rows[-1]["reservoir"], 9),
        "final_cumulative_release": round(rows[-1]["cumulative_release"], 9),
        "event_match_to_original": None if event_match is None else round(event_match, 9),
        "score_mae_to_original": None if score_mae is None else round(score_mae, 9),
        "release_mae_to_original": None if release_mae is None else round(release_mae, 9),
        "quality_mae_to_original": None if quality_mae is None else round(quality_mae, 9),
        "cumulative_release_delta_vs_original": None if cumulative_delta is None else round(cumulative_delta, 9),
        "final_residue_l1_to_original": None if final_residue_l1 is None else round(final_residue_l1, 9),
        "final_state_distance_to_original": None if final_state_distance is None else round(final_state_distance, 9),
        "final_memory_size": len(run["final_memory"]),
    }


def run(cfg: Dict[str, Any]) -> Dict[str, Any]:
    base_events = generate_events(cfg)
    variants = [
        "original_order",
        "reverse_order",
        "block_shuffle_order",
        "compatible_cluster_order",
        "random_order_same_multiset",
        "context_sorted_order",
    ]
    runs = {variant: run_variant(variant, base_events, cfg) for variant in variants}
    original = runs["original_order"]
    summaries = [
        summarize(runs[variant], None if variant == "original_order" else original, cfg)
        for variant in variants
    ]

    original_signature = multiset_signature(order_variant(base_events, "original_order", cfg["seed"]))
    multiset_checks = {
        variant: multiset_signature(order_variant(base_events, variant, cfg["seed"])) == original_signature
        for variant in variants
    }

    lookup = {s["variant"]: s for s in summaries}
    residue_changed = [
        variant
        for variant in variants
        if variant != "original_order" and lookup[variant]["final_residue_l1_to_original"] >= 0.10
    ]

    criteria = {
        "all_variants_preserve_context_object_u_multiset": all(multiset_checks.values()),
        "reverse_event_match_to_original_le_0_90": lookup["reverse_order"]["event_match_to_original"] <= 0.90,
        "random_event_match_to_original_le_0_90": lookup["random_order_same_multiset"]["event_match_to_original"] <= 0.90,
        "block_shuffle_release_mae_to_original_ge_0_02": lookup["block_shuffle_order"]["release_mae_to_original"] >= 0.02,
        "context_sorted_final_state_distance_ge_0_15": lookup["context_sorted_order"]["final_state_distance_to_original"] >= 0.15,
        "at_least_3_order_variants_residue_l1_ge_0_10": len(residue_changed) >= 3,
    }

    return {
        "experiment": "contextual_membrane_v3_order_effect",
        "date": "2026-07-08",
        "layer": "CONTEXTUAL_COMPONENT",
        "seed": cfg["seed"],
        "config": cfg,
        "variants": variants,
        "summaries": summaries,
        "multiset_preservation": multiset_checks,
        "criteria": criteria,
        "verdict": "PASS_ORDER_EFFECT" if all(criteria.values()) else "FAIL_OR_MIXED_ORDER_EFFECT",
        "base_event_count": len(base_events),
        "base_event_sample_first_32": base_events[:32],
        "row_sample_by_variant_first_12": {variant: runs[variant]["rows"][:12] for variant in variants},
        "claim_boundary": [
            "This is a component-level order-effect test.",
            "PASS means order alone changes the implemented membrane's event timing, final state, and residue distribution while preserving the event multiset.",
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
    parser.add_argument("--out", type=Path, default=Path("data/contextual/contextual_membrane_v3_order_effect_seed20260708.json"))
    parser.add_argument("--csv", type=Path, default=Path("data/contextual/contextual_membrane_v3_order_effect_seed20260708_summary.csv"))
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
