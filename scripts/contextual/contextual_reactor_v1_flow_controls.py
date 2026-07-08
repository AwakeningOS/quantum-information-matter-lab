#!/usr/bin/env python3
"""contextual_reactor_v1_flow_controls

Layer: CLASSICAL_COMPONENT

Hardens contextual_reactor_v0_membrane_to_flow with multi-seed controls:
matched pass-rate random membrane, matched signal shuffle, matched signal lag,
additive-boundary replacement, and strong reactor-without-membrane baseline.

This is a component-level propagation-control test, not a quantum-specific claim
and not a formal contextuality witness.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np

CONTEXTS = ["identity", "path", "boundary", "history"]
OBJECTS = ["A", "B", "P", "Q"]

OBJ_BASE = {"A": 0.56, "B": 0.28, "P": 0.48, "Q": 0.40}
CTX_BASE = {"identity": 0.08, "path": -0.02, "boundary": -0.06, "history": 0.04}
JOINT = {
    "identity": {"A": 0.18, "B": -0.10, "P": 0.14, "Q": -0.06},
    "path": {"A": -0.12, "B": 0.22, "P": -0.08, "Q": 0.03},
    "boundary": {"A": -0.08, "B": -0.16, "P": 0.02, "Q": 0.20},
    "history": {"A": 0.02, "B": -0.03, "P": 0.15, "Q": 0.17},
}

DEFAULT_CONFIG = {
    "seed": 20260708,
    "seeds": [20260708, 20260709, 20260710, 20260711, 20260712],
    "steps": 512,
    "burn": 64,
    "memory_decay": 0.962,
    "joint_memory_gain": 0.42,
    "joint_counterfactual_gain": 0.34,
    "object_memory_gain": 0.12,
    "context_memory_gain": 0.12,
    "transition_gain": 0.16,
    "joint_transition_gain": 0.22,
    "incompatibility_penalty": 0.12,
    "reactor_gain": 0.54,
    "reactor_decay": 0.017,
    "reactor_leak": 0.012,
    "quality_gain": 0.035,
    "quality_loss": 0.021,
    "stability_gain": 0.023,
    "stability_loss": 0.030,
    "release_rate": 0.074,
    "persistence_decay": 0.011,
    "min_score": 0.02,
    "max_score": 0.98,
}


def compat_graph():
    graph = {(a, b): a == b for a in CONTEXTS for b in CONTEXTS}
    for pair in [("identity", "history"), ("history", "identity"), ("path", "boundary"), ("boundary", "path")]:
        graph[pair] = True
    return graph


def mean(xs):
    xs = list(xs)
    return float(sum(xs) / len(xs)) if xs else 0.0


def mae(xs, ys):
    return mean(abs(float(a) - float(b)) for a, b in zip(xs, ys))


def clip(x, cfg):
    return float(np.clip(x, cfg["min_score"], cfg["max_score"]))


def generate_events(cfg, seed):
    rng = np.random.default_rng(seed)
    events = []
    ctx = CONTEXTS[int(rng.integers(0, len(CONTEXTS)))]
    obj = OBJECTS[int(rng.integers(0, len(OBJECTS)))]

    compat_neighbors = {
        "identity": ["identity", "history"],
        "history": ["history", "identity"],
        "path": ["path", "boundary"],
        "boundary": ["boundary", "path"],
    }
    incompat_neighbors = {
        "identity": ["path", "boundary"],
        "history": ["path", "boundary"],
        "path": ["identity", "history"],
        "boundary": ["identity", "history"],
    }
    object_transitions = {
        "A": [0.34, 0.07, 0.44, 0.15],
        "B": [0.16, 0.42, 0.10, 0.32],
        "P": [0.33, 0.06, 0.45, 0.16],
        "Q": [0.21, 0.20, 0.18, 0.41],
    }

    scheduled = {}
    for t in range(cfg["steps"]):
        if t in scheduled:
            ctx, obj = scheduled.pop(t)
        elif t > 0:
            choices = compat_neighbors[ctx] if rng.random() < 0.70 else incompat_neighbors[ctx]
            ctx = choices[int(rng.integers(0, len(choices)))]
            obj = OBJECTS[int(rng.choice(len(OBJECTS), p=object_transitions[obj]))]

        u = float(rng.beta(2.1, 2.1)) if rng.random() < 0.75 else float(rng.random())
        events.append({"t": t, "context": ctx, "object": obj, "u": u})

        if rng.random() < 0.40:
            lag = int(rng.integers(2, 7))
            if t + lag < cfg["steps"]:
                r = rng.random()
                if r < 0.60:
                    scheduled[t + lag] = (ctx, obj)
                elif r < 0.80:
                    scheduled[t + lag] = (ctx, OBJECTS[int(rng.integers(0, len(OBJECTS)))])
                else:
                    scheduled[t + lag] = (CONTEXTS[int(rng.integers(0, len(CONTEXTS)))], obj)
    return events


def score_terms(memory, ctx, obj, prev_ctx, prev_obj, cfg, variant):
    obj_obs = memory.get(f"obj:{obj}:PASS", 0.0) - memory.get(f"obj:{obj}:BLOCK", 0.0)
    ctx_obs = memory.get(f"ctx:{ctx}:PASS", 0.0) - memory.get(f"ctx:{ctx}:BLOCK", 0.0)
    joint_obs = memory.get(f"joint:{ctx}:{obj}:PASS", 0.0) - memory.get(f"joint:{ctx}:{obj}:BLOCK", 0.0)
    joint_cf = memory.get(f"cf:{ctx}:{obj}:PASS", 0.0) - memory.get(f"cf:{ctx}:{obj}:BLOCK", 0.0)
    trans = 0.0 if prev_ctx is None else memory.get(f"trans:{prev_ctx}->{ctx}", 0.0)
    jtrans = 0.0 if prev_ctx is None else memory.get(f"jtrans:{prev_ctx}:{prev_obj}->{ctx}:{obj}", 0.0)

    if variant in {"full_membrane_to_reactor", "matched_signal_shuffle_replay", "matched_signal_lag_replay"}:
        static = OBJ_BASE[obj] + CTX_BASE[ctx] + JOINT[ctx][obj]
        obj_term = cfg["object_memory_gain"] * math.tanh(obj_obs / 4.0)
        ctx_term = cfg["context_memory_gain"] * math.tanh(ctx_obs / 4.0)
        joint_term = cfg["joint_memory_gain"] * math.tanh(joint_obs / 3.0)
        cf_term = cfg["joint_counterfactual_gain"] * math.tanh(joint_cf / 3.0)
        trans_term = cfg["transition_gain"] * math.tanh(trans / 3.0) + cfg["joint_transition_gain"] * math.tanh(jtrans / 2.0)
    elif variant == "no_memory_membrane_to_reactor":
        static = OBJ_BASE[obj] + CTX_BASE[ctx] + JOINT[ctx][obj]
        obj_term = ctx_term = joint_term = cf_term = trans_term = 0.0
    elif variant == "no_counterfactual_membrane_to_reactor":
        static = OBJ_BASE[obj] + CTX_BASE[ctx] + JOINT[ctx][obj]
        obj_term = cfg["object_memory_gain"] * math.tanh(obj_obs / 4.0)
        ctx_term = cfg["context_memory_gain"] * math.tanh(ctx_obs / 4.0)
        joint_term = cfg["joint_memory_gain"] * math.tanh(joint_obs / 3.0)
        cf_term = 0.0
        trans_term = cfg["transition_gain"] * math.tanh(trans / 3.0) + cfg["joint_transition_gain"] * math.tanh(jtrans / 2.0)
    elif variant == "additive_boundary_membrane_to_reactor":
        static = OBJ_BASE[obj] + CTX_BASE[ctx]
        obj_term = 0.16 * math.tanh(obj_obs / 4.0)
        ctx_term = 0.16 * math.tanh(ctx_obs / 4.0)
        joint_term = cf_term = 0.0
        trans_term = 0.08 * math.tanh(trans / 3.0)
    elif variant in {"matched_pass_rate_random_membrane", "strong_reactor_without_membrane"}:
        static = 0.5
        obj_term = ctx_term = joint_term = cf_term = trans_term = 0.0
    else:
        raise ValueError(variant)

    return static + obj_term + ctx_term + joint_term + cf_term + trans_term, {
        "static": static,
        "obj_term": obj_term,
        "ctx_term": ctx_term,
        "joint_term": joint_term,
        "cf_term": cf_term,
        "trans_term": trans_term,
    }


def run_variant(variant, cfg, events, seed, full_rows=None):
    rng = np.random.default_rng(seed + 7777)
    compat = compat_graph()
    memory = {}
    rows = []
    prev_ctx = prev_obj = None
    reactor = 0.0
    quality = 1.0
    stability = 0.55
    persistence = 0.0
    cumulative_release = 0.0

    full_signals = [r["membrane_signal"] for r in full_rows] if full_rows else None
    full_passes = [r["passed"] for r in full_rows] if full_rows else None
    if variant == "matched_signal_shuffle_replay":
        replay = list(full_signals)
        rng.shuffle(replay)
    elif variant == "matched_signal_lag_replay":
        lag = 17 + (seed % 11)
        replay = list(full_signals[-lag:] + full_signals[:-lag])
    else:
        replay = None

    full_pass_rate = mean(1.0 if p else 0.0 for p in full_passes) if full_passes else None
    full_signal_mean = mean(full_signals) if full_signals else 0.0

    for i, event in enumerate(events):
        ctx, obj, u = event["context"], event["object"], event["u"]
        compatible = True if prev_ctx is None else compat[(prev_ctx, ctx)]
        memory = {k: v * cfg["memory_decay"] for k, v in memory.items() if abs(v * cfg["memory_decay"]) > 1e-9}

        raw, terms = score_terms(memory, ctx, obj, prev_ctx, prev_obj, cfg, variant)
        score = clip(raw - (0.0 if compatible else cfg["incompatibility_penalty"]), cfg)
        passed = bool(u < score)
        joint_alignment = clip(OBJ_BASE[obj] + CTX_BASE[ctx] + JOINT[ctx][obj] - (0.0 if compatible else 0.12), cfg)
        cf_strength = min(1.0, abs(terms["cf_term"]) / 0.34)
        cf_boost = 1.0 + 0.55 * cf_strength

        if variant == "matched_pass_rate_random_membrane":
            passed = bool(rng.random() < full_pass_rate)
            membrane_signal = (0.52 + 0.28 * float(rng.beta(2.5, 2.0))) if passed else (-0.12 - 0.25 * float(rng.beta(2.0, 2.3)))
            score = 0.5
        elif variant in {"matched_signal_shuffle_replay", "matched_signal_lag_replay"}:
            membrane_signal = float(replay[i])
            passed = bool(membrane_signal > 0.15)
            score = clip(0.5 + 0.45 * membrane_signal, cfg)
        elif variant == "strong_reactor_without_membrane":
            passed = bool(rng.random() < full_pass_rate)
            membrane_signal = 0.60 * full_signal_mean + (0.10 if passed else -0.08) + 0.04 * (0.55 - stability)
            score = 0.5
        else:
            if passed:
                membrane_signal = (0.55 + 0.45 * score) * (1.10 if compatible else 0.82)
                if variant == "full_membrane_to_reactor":
                    membrane_signal *= cf_boost
            else:
                membrane_signal = (-0.22 - 0.25 * (1.0 - score)) * (1.15 if not compatible else 0.80)
                if variant == "full_membrane_to_reactor":
                    membrane_signal /= cf_boost

        positive = max(0.0, membrane_signal)
        negative = max(0.0, -membrane_signal)
        alignment = 0.48 + 0.52 * joint_alignment
        if compatible:
            alignment += 0.10
        if variant == "strong_reactor_without_membrane":
            alignment = 0.55
        alignment = max(0.18, min(1.15, alignment))

        if positive > 0:
            reactor += cfg["reactor_gain"] * positive * (0.54 + 0.46 * stability) * alignment
            extra_q = 0.018 * cf_strength if variant == "full_membrane_to_reactor" else 0.0
            extra_s = 0.012 * cf_strength if variant == "full_membrane_to_reactor" else 0.0
            quality = min(1.5, quality + cfg["quality_gain"] * (1.0 - quality + 0.20 * alignment + 0.10 * positive) + extra_q)
            stability = min(1.2, stability + cfg["stability_gain"] * (1.0 - stability + 0.16 * alignment) + extra_s)
            outcome = "PASS"
        else:
            reactor += cfg["reactor_gain"] * (-0.35 * negative) * (1.0 - stability * 0.2) * (1.15 if not compatible else 0.85)
            reactor = max(0.0, reactor)
            quality = max(0.18, quality - cfg["quality_loss"] * (1.0 + 0.5 * (not compatible) + 0.5 * negative))
            stability = max(0.12, stability - cfg["stability_loss"] * (1.0 + 0.4 * (not compatible) + 0.4 * negative))
            outcome = "BLOCK"

        if passed:
            if variant != "strong_reactor_without_membrane":
                for key in [f"obj:{obj}:PASS", f"ctx:{ctx}:PASS", f"joint:{ctx}:{obj}:PASS", f"cf:{ctx}:{obj}:BLOCK"]:
                    memory[key] = memory.get(key, 0.0) + 1.0
        else:
            if variant != "strong_reactor_without_membrane":
                for key in [f"obj:{obj}:BLOCK", f"ctx:{ctx}:BLOCK", f"joint:{ctx}:{obj}:BLOCK", f"cf:{ctx}:{obj}:PASS"]:
                    memory[key] = memory.get(key, 0.0) + 1.0

        if prev_ctx is not None and variant != "strong_reactor_without_membrane":
            memory[f"trans:{prev_ctx}->{ctx}"] = memory.get(f"trans:{prev_ctx}->{ctx}", 0.0) + 1.0
            memory[f"jtrans:{prev_ctx}:{prev_obj}->{ctx}:{obj}"] = memory.get(f"jtrans:{prev_ctx}:{prev_obj}->{ctx}:{obj}", 0.0) + 1.0

        release = max(0.0, reactor * cfg["release_rate"] * quality * (0.45 + 0.55 * stability))
        reactor = max(0.0, reactor - release - cfg["reactor_decay"] * reactor - cfg["reactor_leak"] * max(0.0, 0.5 - stability))
        persistence = persistence * (1.0 - cfg["persistence_decay"]) + release * (0.32 + 0.68 * stability)
        cumulative_release += release

        rows.append({
            "t": event["t"],
            "seed": seed,
            "variant": variant,
            "context": ctx,
            "object": obj,
            "previous_context": prev_ctx or "NONE",
            "previous_object": prev_obj or "NONE",
            "compatible_with_previous": compatible,
            "u": round(u, 12),
            "passage_score": round(score, 9),
            "passed": passed,
            "observed_output": outcome,
            "membrane_signal": round(membrane_signal, 9),
            "alignment": round(alignment, 9),
            "joint_alignment": round(joint_alignment, 9),
            "static_term": round(terms["static"], 9),
            "joint_term": round(terms["joint_term"], 9),
            "counterfactual_term": round(terms["cf_term"], 9),
            "transition_term": round(terms["trans_term"], 9),
            "reactor": round(reactor, 9),
            "quality": round(quality, 9),
            "stability": round(stability, 9),
            "release": round(release, 9),
            "persistence": round(persistence, 9),
            "cumulative_release": round(cumulative_release, 9),
            "memory_size": len(memory),
        })
        prev_ctx, prev_obj = ctx, obj

    return {"variant": variant, "seed": seed, "rows": rows}


def summarize_seed(run, full, cfg):
    rows = run["rows"][cfg["burn"]:]
    full_rows = full["rows"][cfg["burn"]:] if full else None

    if full_rows:
        event_match = mean(1.0 if r["passed"] == f["passed"] else 0.0 for r, f in zip(rows, full_rows))
        signal_mae = mae([r["membrane_signal"] for r in rows], [f["membrane_signal"] for f in full_rows])
        release_mae = mae([r["release"] for r in rows], [f["release"] for f in full_rows])
        reactor_mae = mae([r["reactor"] for r in rows], [f["reactor"] for f in full_rows])
        quality_mae = mae([r["quality"] for r in rows], [f["quality"] for f in full_rows])
        persistence_mae = mae([r["persistence"] for r in rows], [f["persistence"] for f in full_rows])
        cumulative_delta = rows[-1]["cumulative_release"] - full_rows[-1]["cumulative_release"]
        final_state_distance = math.sqrt(
            (rows[-1]["quality"] - full_rows[-1]["quality"]) ** 2
            + ((rows[-1]["reactor"] - full_rows[-1]["reactor"]) ** 2) / 25.0
            + ((rows[-1]["persistence"] - full_rows[-1]["persistence"]) ** 2) / 100.0
            + ((rows[-1]["cumulative_release"] - full_rows[-1]["cumulative_release"]) ** 2) / 10000.0
        )
    else:
        event_match = signal_mae = release_mae = reactor_mae = quality_mae = persistence_mae = cumulative_delta = final_state_distance = None

    return {
        "seed": run["seed"],
        "variant": run["variant"],
        "n_post_burn": len(rows),
        "pass_rate": round(mean(1.0 if r["passed"] else 0.0 for r in rows), 9),
        "mean_membrane_signal": round(mean(r["membrane_signal"] for r in rows), 9),
        "mean_reactor": round(mean(r["reactor"] for r in rows), 9),
        "mean_quality": round(mean(r["quality"] for r in rows), 9),
        "mean_stability": round(mean(r["stability"] for r in rows), 9),
        "mean_release": round(mean(r["release"] for r in rows), 9),
        "final_reactor": round(rows[-1]["reactor"], 9),
        "final_quality": round(rows[-1]["quality"], 9),
        "final_stability": round(rows[-1]["stability"], 9),
        "final_persistence": round(rows[-1]["persistence"], 9),
        "final_cumulative_release": round(rows[-1]["cumulative_release"], 9),
        "event_match_to_full": None if event_match is None else round(event_match, 9),
        "membrane_signal_mae_to_full": None if signal_mae is None else round(signal_mae, 9),
        "release_mae_to_full": None if release_mae is None else round(release_mae, 9),
        "reactor_mae_to_full": None if reactor_mae is None else round(reactor_mae, 9),
        "quality_mae_to_full": None if quality_mae is None else round(quality_mae, 9),
        "persistence_mae_to_full": None if persistence_mae is None else round(persistence_mae, 9),
        "cumulative_release_delta_vs_full": None if cumulative_delta is None else round(cumulative_delta, 9),
        "final_state_distance_to_full": None if final_state_distance is None else round(final_state_distance, 9),
    }


def aggregate(seed_summaries):
    variants = []
    for summary in seed_summaries:
        if summary["variant"] not in variants:
            variants.append(summary["variant"])

    fields = [k for k in seed_summaries[0].keys() if k not in ("seed", "variant")]
    aggregate_rows = []
    for variant in variants:
        summaries = [s for s in seed_summaries if s["variant"] == variant]
        row = {"variant": variant, "n_seeds": len(summaries)}
        for field in fields:
            values = [s[field] for s in summaries if s[field] is not None]
            if values:
                row[field + "_mean"] = round(mean(values), 9)
                row[field + "_sd"] = round(float(np.std(values, ddof=0)), 9)
            else:
                row[field + "_mean"] = None
                row[field + "_sd"] = None
        aggregate_rows.append(row)
    return aggregate_rows


def run(cfg):
    variants = [
        "full_membrane_to_reactor",
        "no_memory_membrane_to_reactor",
        "no_counterfactual_membrane_to_reactor",
        "matched_pass_rate_random_membrane",
        "matched_signal_shuffle_replay",
        "matched_signal_lag_replay",
        "additive_boundary_membrane_to_reactor",
        "strong_reactor_without_membrane",
    ]

    seed_summaries = []
    sample = {}

    for seed in cfg["seeds"]:
        events = generate_events(cfg, seed)
        full = run_variant("full_membrane_to_reactor", cfg, events, seed)
        runs = {"full_membrane_to_reactor": full}

        for variant in variants[1:]:
            runs[variant] = run_variant(variant, cfg, events, seed, full_rows=full["rows"])

        for variant in variants:
            seed_summaries.append(summarize_seed(runs[variant], None if variant == "full_membrane_to_reactor" else full, cfg))

        if seed == cfg["seeds"][0]:
            sample = {
                "base_event_sample_first_16": events[:16],
                "row_sample_by_variant_first_6": {variant: runs[variant]["rows"][:6] for variant in variants},
            }

    aggregate_summaries = aggregate(seed_summaries)
    lookup = {row["variant"]: row for row in aggregate_summaries}
    full_summary = lookup["full_membrane_to_reactor"]
    controls = [v for v in variants if v != "full_membrane_to_reactor"]
    full_by_seed = {s["seed"]: s for s in seed_summaries if s["variant"] == "full_membrane_to_reactor"}

    win_counts = {}
    for control in controls:
        control_by_seed = {s["seed"]: s for s in seed_summaries if s["variant"] == control}
        win_counts[control + "_persistence_wins"] = sum(
            1 for seed in cfg["seeds"] if full_by_seed[seed]["final_persistence"] > control_by_seed[seed]["final_persistence"]
        )
        win_counts[control + "_cum_release_wins"] = sum(
            1 for seed in cfg["seeds"] if full_by_seed[seed]["final_cumulative_release"] > control_by_seed[seed]["final_cumulative_release"]
        )
        win_counts[control + "_quality_wins"] = sum(
            1 for seed in cfg["seeds"] if full_by_seed[seed]["final_quality"] > control_by_seed[seed]["final_quality"]
        )

    criteria = {
        "multi_seed_full_persistence_wins_all_controls_5_of_5": all(win_counts[c + "_persistence_wins"] >= 5 for c in controls),
        "multi_seed_full_quality_wins_all_controls_5_of_5": all(win_counts[c + "_quality_wins"] >= 5 for c in controls),
        "matched_pass_rate_release_mae_mean_ge_0_03": lookup["matched_pass_rate_random_membrane"]["release_mae_to_full_mean"] >= 0.03,
        "matched_signal_shuffle_final_state_distance_mean_ge_0_20": lookup["matched_signal_shuffle_replay"]["final_state_distance_to_full_mean"] >= 0.20,
        "matched_signal_lag_persistence_mae_mean_ge_0_75": lookup["matched_signal_lag_replay"]["persistence_mae_to_full_mean"] >= 0.75,
        "strong_reactor_without_membrane_full_persistence_margin_ge_1": (
            full_summary["final_persistence_mean"] - lookup["strong_reactor_without_membrane"]["final_persistence_mean"]
        ) >= 1.0,
        "additive_boundary_cumulative_release_delta_abs_mean_ge_25": abs(
            lookup["additive_boundary_membrane_to_reactor"]["cumulative_release_delta_vs_full_mean"]
        ) >= 25.0,
    }

    return {
        "experiment": "contextual_reactor_v1_flow_controls",
        "date": "2026-07-08",
        "layer": "CLASSICAL_COMPONENT",
        "seed": cfg["seed"],
        "seeds": cfg["seeds"],
        "config": cfg,
        "variants": variants,
        "seed_summaries": seed_summaries,
        "aggregate_summaries": aggregate_summaries,
        "win_counts": win_counts,
        "criteria": criteria,
        "verdict": "PASS_HARDENED_MEMBRANE_TO_FLOW_CONTROLS" if all(criteria.values()) else "FAIL_OR_MIXED_HARDENED_FLOW_CONTROLS",
        "base_event_count_per_seed": cfg["steps"],
        **sample,
        "claim_boundary": [
            "This is a component-level hardened propagation control test.",
            "PASS means full contextual membrane-to-reactor propagation survives multi-seed, matched pass-rate, matched signal, additive-boundary, and strong no-membrane controls under the stated metrics.",
            "This is not a quantum-specific claim and not a formal contextuality witness.",
            "No biological, consciousness, metabolism, self-repair, or physical matter synthesis claim is made.",
        ],
    }


def write_csv(rows, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260708)
    parser.add_argument("--steps", type=int, default=512)
    parser.add_argument("--out", type=Path, default=Path("data/contextual/contextual_reactor_v1_flow_controls_seed20260708.json"))
    parser.add_argument("--csv", type=Path, default=Path("data/contextual/contextual_reactor_v1_flow_controls_seed20260708_aggregate.csv"))
    parser.add_argument("--seed-csv", type=Path, default=Path("data/contextual/contextual_reactor_v1_flow_controls_seed20260708_seed_summary.csv"))
    args = parser.parse_args()

    cfg = dict(DEFAULT_CONFIG)
    cfg["seed"] = args.seed
    cfg["seeds"] = [args.seed + i for i in range(5)]
    cfg["steps"] = args.steps

    result = run(cfg)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(result["aggregate_summaries"], args.csv)
    write_csv(result["seed_summaries"], args.seed_csv)

    print(json.dumps({
        "experiment": result["experiment"],
        "verdict": result["verdict"],
        "aggregate_summaries": result["aggregate_summaries"],
        "win_counts": result["win_counts"],
        "criteria": result["criteria"],
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
