#!/usr/bin/env python3
"""
contextual_membrane_v0

Layer: CONTEXTUAL_COMPONENT

Designed contextual membrane component. The result is a component-level
context/replay test only, not a quantum-specific claim.
"""
from __future__ import annotations

import argparse, csv, json, math
from pathlib import Path
import numpy as np

CONTEXTS = ["identity", "path", "boundary", "history"]
OBJECTS = ["A", "B", "P", "Q"]
BASE = {"A": 0.62, "B": 0.24, "P": 0.50, "Q": 0.38}
BIAS = {
    "identity": {"A": 0.18, "B": -0.06, "P": 0.16, "Q": -0.02},
    "path": {"A": -0.12, "B": 0.20, "P": -0.03, "Q": 0.04},
    "boundary": {"A": -0.04, "B": -0.16, "P": 0.02, "Q": 0.18},
    "history": {"A": 0.04, "B": 0.02, "P": 0.12, "Q": 0.14},
}

DEFAULT_CONFIG = {
    "seed": 20260708,
    "steps": 64,
    "memory_decay": 0.94,
    "memory_gain": 0.18,
    "alternative_gain": 0.06,
    "incompatibility_penalty": 0.22,
    "min_score": 0.02,
    "max_score": 0.98,
}


def compat_graph():
    g = {(a, b): a == b for a in CONTEXTS for b in CONTEXTS}
    for p in [("identity", "history"), ("history", "identity"), ("path", "boundary"), ("boundary", "path")]:
        g[p] = True
    return g


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else 0.0


def clip(x, cfg):
    return float(np.clip(x, cfg["min_score"], cfg["max_score"]))


def mem_term(mem, ctx, obj, cfg):
    observed = mem.get(f"seen:{ctx}:{obj}:PASS", 0.0)
    blocked_alt = mem.get(f"alt:{ctx}:{obj}:BLOCK", 0.0)
    passed_alt = mem.get(f"alt:{ctx}:{obj}:PASS", 0.0)
    return (
        cfg["memory_gain"] * math.tanh(observed / 4.0)
        - cfg["alternative_gain"] * math.tanh(blocked_alt / 4.0)
        + 0.5 * cfg["alternative_gain"] * math.tanh(passed_alt / 4.0)
    )


def make_events(cfg):
    rng = np.random.default_rng(cfg["seed"])
    return [
        {
            "t": t,
            "context": CONTEXTS[int(rng.integers(0, len(CONTEXTS)))],
            "object": OBJECTS[int(rng.integers(0, len(OBJECTS)))],
            "u": float(rng.random()),
        }
        for t in range(cfg["steps"])
    ]


def score_event(variant, ctx, obj, prev, mem, cfg, replay=None):
    compatible = True if prev is None else compat_graph()[(prev, ctx)]
    if variant == "object_only":
        score = BASE[obj]
    elif variant == "context_no_memory":
        score = BASE[obj] + BIAS.get(ctx, {}).get(obj, 0.0)
        if not compatible:
            score -= cfg["incompatibility_penalty"]
    elif variant == "object_marginal_replay":
        score = replay[obj]
    elif variant in {"full_contextual", "shuffled_context_full"}:
        score = BASE[obj] + BIAS.get(ctx, {}).get(obj, 0.0) + mem_term(mem, ctx, obj, cfg)
        if not compatible:
            score -= cfg["incompatibility_penalty"]
    else:
        raise ValueError(variant)
    return clip(score, cfg), compatible


def update_mem(mem, ctx, obj, passed, compatible, prev, cfg):
    out = {k: v * cfg["memory_decay"] for k, v in mem.items() if abs(v * cfg["memory_decay"]) > 1e-12}
    if passed:
        out[f"seen:{ctx}:{obj}:PASS"] = out.get(f"seen:{ctx}:{obj}:PASS", 0.0) + 1.0
        out[f"alt:{ctx}:{obj}:BLOCK"] = out.get(f"alt:{ctx}:{obj}:BLOCK", 0.0) + 0.35
    else:
        out[f"seen:{ctx}:{obj}:BLOCK"] = out.get(f"seen:{ctx}:{obj}:BLOCK", 0.0) + 1.0
        out[f"alt:{ctx}:{obj}:PASS"] = out.get(f"alt:{ctx}:{obj}:PASS", 0.0) + 0.35
    if prev is not None and not compatible:
        out[f"incompat:{prev}->{ctx}"] = out.get(f"incompat:{prev}->{ctx}", 0.0) + 1.0
    return out


def run_variant(variant, cfg, events, replay=None, shuffled=None):
    mem, rows, prev = {}, [], None
    for i, ev in enumerate(events):
        ctx = shuffled[i] if shuffled is not None else ev["context"]
        obj = ev["object"]
        score, compatible = score_event(variant, ctx, obj, prev, mem, cfg, replay)
        passed = bool(ev["u"] < score)
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
            "observed_output": "PASS" if passed else "BLOCK",
            "unobserved_alternative": "BLOCK" if passed else "PASS",
            "memory_size_before_update": len(mem),
        })
        mem = update_mem(mem, ctx, obj, passed, compatible, prev, cfg)
        prev = ctx
    return rows


def summarize(rows, full=None):
    by_ctx = {}
    for c in CONTEXTS:
        sub = [r for r in rows if r["context"] == c]
        by_ctx[c] = {
            "n": len(sub),
            "mean_score": round(mean(float(r["passage_score"]) for r in sub), 9),
            "pass_rate": round(mean(1.0 if r["passed"] else 0.0 for r in sub), 9),
        }

    by_co, ranges = [], []
    for o in OBJECTS:
        vals = []
        for c in CONTEXTS:
            sub = [r for r in rows if r["context"] == c and r["object"] == o]
            m = mean(float(r["passage_score"]) for r in sub)
            vals.append(m)
            by_co.append({
                "object": o,
                "context": c,
                "n": len(sub),
                "mean_score": round(m, 9),
                "pass_rate": round(mean(1.0 if r["passed"] else 0.0 for r in sub), 9),
            })
        ranges.append(max(vals) - min(vals))

    comp = [float(r["passage_score"]) for r in rows if r["compatible_with_previous"]]
    inc = [float(r["passage_score"]) for r in rows if not r["compatible_with_previous"]]
    match = mae = None
    if full is not None:
        match = mean(1.0 if r["passed"] == f["passed"] else 0.0 for r, f in zip(rows, full))
        mae = mean(abs(float(r["passage_score"]) - float(f["passage_score"])) for r, f in zip(rows, full))

    return {
        "variant": rows[0]["variant"],
        "n": len(rows),
        "pass_rate": round(mean(1.0 if r["passed"] else 0.0 for r in rows), 9),
        "mean_score": round(mean(float(r["passage_score"]) for r in rows), 9),
        "context_mean_score_range": round(max(v["mean_score"] for v in by_ctx.values()) - min(v["mean_score"] for v in by_ctx.values()), 9),
        "object_conditioned_context_score_range_mean": round(mean(ranges), 9),
        "compatibility_score_gap": round(mean(comp) - mean(inc), 9),
        "final_memory_size": int(rows[-1]["memory_size_before_update"]),
        "event_match_to_full": None if match is None else round(match, 9),
        "score_mae_to_full": None if mae is None else round(mae, 9),
        "by_context": by_ctx,
        "by_context_object": by_co,
    }


def run(cfg):
    events = make_events(cfg)
    full = run_variant("full_contextual", cfg, events)
    replay = {o: mean(float(r["passage_score"]) for r in full if r["object"] == o) for o in OBJECTS}
    shuffled = [e["context"] for e in events]
    np.random.default_rng(cfg["seed"] + 991).shuffle(shuffled)

    variants = {
        "full_contextual": full,
        "context_no_memory": run_variant("context_no_memory", cfg, events),
        "object_only": run_variant("object_only", cfg, events),
        "object_marginal_replay": run_variant("object_marginal_replay", cfg, events, replay=replay),
        "shuffled_context_full": run_variant("shuffled_context_full", cfg, events, shuffled=shuffled),
    }
    summaries = [summarize(v, None if k == "full_contextual" else full) for k, v in variants.items()]
    lookup = {s["variant"]: s for s in summaries}
    criteria = {
        "full_object_conditioned_context_range_ge_0_15": lookup["full_contextual"]["object_conditioned_context_score_range_mean"] >= 0.15,
        "full_compatibility_gap_ge_0_10": lookup["full_contextual"]["compatibility_score_gap"] >= 0.10,
        "object_only_context_range_le_0_05": lookup["object_only"]["object_conditioned_context_score_range_mean"] <= 0.05,
        "object_replay_event_match_below_0_90": lookup["object_marginal_replay"]["event_match_to_full"] < 0.90,
    }
    rows = [r for vs in variants.values() for r in vs]
    return {
        "experiment": "contextual_membrane_v0",
        "date": "2026-07-08",
        "layer": "CONTEXTUAL_COMPONENT",
        "seed": cfg["seed"],
        "config": cfg,
        "contexts": CONTEXTS,
        "objects": OBJECTS,
        "compatibility_relation": [{"a": a, "b": b, "compatible": v} for (a, b), v in sorted(compat_graph().items())],
        "base_score": BASE,
        "context_bias": BIAS,
        "object_replay_score_from_full": {k: round(v, 9) for k, v in replay.items()},
        "summaries": summaries,
        "criteria": criteria,
        "verdict": "PASS_COMPONENT_BEHAVIOR" if all(criteria.values()) else "MIXED_OR_FAIL",
        "claim_boundary": [
            "Designed contextual component result, not a quantum-specific claim.",
            "PASS means the implemented component expresses context-conditioned membrane behavior against object-only/replay controls.",
            "Quantum/contextuality promotion requires a separate audit witness and controls.",
        ],
        "rows": rows,
    }


def write_csv(result, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = result["rows"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20260708)
    ap.add_argument("--steps", type=int, default=64)
    ap.add_argument("--out", type=Path, default=Path("data/contextual/contextual_membrane_v0_seed20260708.json"))
    ap.add_argument("--csv", type=Path, default=Path("data/contextual/contextual_membrane_v0_seed20260708_rows.csv"))
    args = ap.parse_args()
    cfg = dict(DEFAULT_CONFIG)
    cfg["seed"] = args.seed
    cfg["steps"] = args.steps
    result = run(cfg)
    summary = {k: v for k, v in result.items() if k != "rows"}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(result, args.csv)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
