#!/usr/bin/env python3
"""contextual_membrane_v4_joint_boundary

Layer: CONTEXTUAL_COMPONENT

Tests whether membrane decisions require a full object/context joint boundary
rather than object-only, context-only, additive, or static pairwise controls.
This is not a quantum-specific claim and not a formal contextuality witness.
"""
from __future__ import annotations

import argparse, csv, json, math
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
    "seed": 20260708, "steps": 512, "burn": 64, "memory_decay": 0.962,
    "joint_memory_gain": 0.42, "joint_counterfactual_gain": 0.34,
    "object_memory_gain": 0.12, "context_memory_gain": 0.12,
    "transition_gain": 0.16, "joint_transition_gain": 0.22,
    "incompatibility_penalty": 0.12, "quality_leak": 0.014,
    "quality_repair": 0.021, "release_rate": 0.080, "reservoir_decay": 0.012,
    "min_score": 0.02, "max_score": 0.98,
}


def compat_graph():
    g = {(a, b): a == b for a in CONTEXTS for b in CONTEXTS}
    for p in [("identity", "history"), ("history", "identity"), ("path", "boundary"), ("boundary", "path")]:
        g[p] = True
    return g


def mean(xs):
    xs = list(xs)
    return float(sum(xs) / len(xs)) if xs else 0.0


def mae(xs, ys):
    return mean(abs(float(a) - float(b)) for a, b in zip(xs, ys))


def clip(x, cfg):
    return float(np.clip(x, cfg["min_score"], cfg["max_score"]))


def generate_events(cfg):
    rng = np.random.default_rng(cfg["seed"])
    events = []
    ctx = CONTEXTS[int(rng.integers(0, len(CONTEXTS)))]
    obj = OBJECTS[int(rng.integers(0, len(OBJECTS)))]
    compat_n = {"identity": ["identity", "history"], "history": ["history", "identity"], "path": ["path", "boundary"], "boundary": ["boundary", "path"]}
    incompat_n = {"identity": ["path", "boundary"], "history": ["path", "boundary"], "path": ["identity", "history"], "boundary": ["identity", "history"]}
    obj_t = {"A": [0.34, 0.07, 0.44, 0.15], "B": [0.16, 0.42, 0.10, 0.32], "P": [0.33, 0.06, 0.45, 0.16], "Q": [0.21, 0.20, 0.18, 0.41]}
    scheduled = {}
    for t in range(cfg["steps"]):
        if t in scheduled:
            ctx, obj = scheduled.pop(t)
        elif t > 0:
            choices = compat_n[ctx] if rng.random() < 0.70 else incompat_n[ctx]
            ctx = choices[int(rng.integers(0, len(choices)))]
            obj = OBJECTS[int(rng.choice(len(OBJECTS), p=obj_t[obj]))]
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
    if variant == "full_joint_boundary":
        static = OBJ_BASE[obj] + CTX_BASE[ctx] + JOINT[ctx][obj]
        obj_term = cfg["object_memory_gain"] * math.tanh(obj_obs / 4.0)
        ctx_term = cfg["context_memory_gain"] * math.tanh(ctx_obs / 4.0)
        joint_term = cfg["joint_memory_gain"] * math.tanh(joint_obs / 3.0)
        cf_term = cfg["joint_counterfactual_gain"] * math.tanh(joint_cf / 3.0)
        trans_term = cfg["transition_gain"] * math.tanh(trans / 3.0) + cfg["joint_transition_gain"] * math.tanh(jtrans / 2.0)
    elif variant == "object_only_replay":
        static, obj_term, ctx_term, joint_term, cf_term, trans_term = OBJ_BASE[obj], 0.22 * math.tanh(obj_obs / 4.0), 0.0, 0.0, 0.0, 0.0
    elif variant == "context_only_replay":
        static, obj_term, ctx_term, joint_term, cf_term, trans_term = 0.44 + CTX_BASE[ctx], 0.0, 0.22 * math.tanh(ctx_obs / 4.0), 0.0, 0.0, 0.0
    elif variant == "additive_object_context_model":
        static = OBJ_BASE[obj] + CTX_BASE[ctx]
        obj_term = 0.16 * math.tanh(obj_obs / 4.0)
        ctx_term = 0.16 * math.tanh(ctx_obs / 4.0)
        joint_term = cf_term = 0.0
        trans_term = 0.08 * math.tanh(trans / 3.0)
    elif variant == "static_pairwise_replay":
        static = OBJ_BASE[obj] + CTX_BASE[ctx] + JOINT[ctx][obj]
        obj_term = 0.10 * math.tanh(obj_obs / 4.0)
        ctx_term = 0.10 * math.tanh(ctx_obs / 4.0)
        joint_term = cf_term = 0.0
        trans_term = 0.05 * math.tanh(trans / 3.0)
    elif variant == "joint_shuffle_control":
        wrong = OBJECTS[(OBJECTS.index(obj) + 1) % len(OBJECTS)]
        wrong_joint_obs = memory.get(f"joint:{ctx}:{wrong}:PASS", 0.0) - memory.get(f"joint:{ctx}:{wrong}:BLOCK", 0.0)
        wrong_cf = memory.get(f"cf:{ctx}:{wrong}:PASS", 0.0) - memory.get(f"cf:{ctx}:{wrong}:BLOCK", 0.0)
        static = OBJ_BASE[obj] + CTX_BASE[ctx] + JOINT[ctx][wrong]
        obj_term = 0.10 * math.tanh(obj_obs / 4.0)
        ctx_term = 0.10 * math.tanh(ctx_obs / 4.0)
        joint_term = 0.20 * math.tanh(wrong_joint_obs / 3.0)
        cf_term = 0.16 * math.tanh(wrong_cf / 3.0)
        trans_term = 0.04 * math.tanh(trans / 3.0)
    else:
        raise ValueError(variant)
    return static + obj_term + ctx_term + joint_term + cf_term + trans_term, {
        "static": static, "obj_term": obj_term, "ctx_term": ctx_term,
        "joint_term": joint_term, "cf_term": cf_term, "trans_term": trans_term,
    }


def run_variant(variant, cfg, events):
    compat = compat_graph()
    memory = {}
    rows = []
    prev_ctx = prev_obj = None
    quality, reservoir, cumulative_release = 1.0, 0.0, 0.0
    for ev in events:
        ctx, obj, u = ev["context"], ev["object"], ev["u"]
        compatible = True if prev_ctx is None else compat[(prev_ctx, ctx)]
        memory = {k: v * cfg["memory_decay"] for k, v in memory.items() if abs(v * cfg["memory_decay"]) > 1e-9}
        raw, terms = score_terms(memory, ctx, obj, prev_ctx, prev_obj, cfg, variant)
        score = clip(raw - (0.0 if compatible else cfg["incompatibility_penalty"]), cfg)
        passed = bool(u < score)
        if passed:
            reservoir += (0.60 + 0.25 * score) * quality
            quality = min(1.35, quality + cfg["quality_repair"] * (1.0 - quality + 0.12))
            for key in [f"obj:{obj}:PASS", f"ctx:{ctx}:PASS", f"joint:{ctx}:{obj}:PASS", f"cf:{ctx}:{obj}:BLOCK"]:
                memory[key] = memory.get(key, 0.0) + 1.0
            outcome = "PASS"
        else:
            quality = max(0.20, quality - cfg["quality_leak"] * (1.0 + (0.4 if not compatible else 0.0)))
            for key in [f"obj:{obj}:BLOCK", f"ctx:{ctx}:BLOCK", f"joint:{ctx}:{obj}:BLOCK", f"cf:{ctx}:{obj}:PASS"]:
                memory[key] = memory.get(key, 0.0) + 1.0
            outcome = "BLOCK"
        if prev_ctx is not None:
            memory[f"trans:{prev_ctx}->{ctx}"] = memory.get(f"trans:{prev_ctx}->{ctx}", 0.0) + 1.0
            memory[f"jtrans:{prev_ctx}:{prev_obj}->{ctx}:{obj}"] = memory.get(f"jtrans:{prev_ctx}:{prev_obj}->{ctx}:{obj}", 0.0) + 1.0
        release = reservoir * cfg["release_rate"] * quality
        reservoir = max(0.0, reservoir - release - cfg["reservoir_decay"] * reservoir)
        cumulative_release += release
        rows.append({
            "t": ev["t"], "variant": variant, "context": ctx, "object": obj,
            "previous_context": prev_ctx or "NONE", "previous_object": prev_obj or "NONE",
            "compatible_with_previous": compatible, "u": round(u, 12),
            "passage_score": round(score, 9), "static_term": round(terms["static"], 9),
            "object_term": round(terms["obj_term"], 9), "context_term": round(terms["ctx_term"], 9),
            "joint_term": round(terms["joint_term"], 9), "counterfactual_term": round(terms["cf_term"], 9),
            "transition_term": round(terms["trans_term"], 9), "passed": passed,
            "observed_output": outcome, "quality": round(quality, 9), "release": round(release, 9),
            "reservoir": round(reservoir, 9), "cumulative_release": round(cumulative_release, 9),
            "memory_size": len(memory),
        })
        prev_ctx, prev_obj = ctx, obj
    final_memory = {k: round(v, 9) for k, v in sorted(memory.items()) if k.startswith(("obj:", "ctx:", "joint:", "cf:", "trans:", "jtrans:"))}
    return {"variant": variant, "rows": rows, "final_memory": final_memory}


def l1_dict(a, b):
    keys = set(a) | set(b)
    return sum(abs(a.get(k, 0.0) - b.get(k, 0.0)) for k in keys) / max(1, len(keys))


def summarize(run, full, cfg):
    rows = run["rows"][cfg["burn"]:]
    full_rows = full["rows"][cfg["burn"]:] if full else None
    if full_rows:
        event_match = mean(1.0 if r["passed"] == f["passed"] else 0.0 for r, f in zip(rows, full_rows))
        score_mae = mae([r["passage_score"] for r in rows], [f["passage_score"] for f in full_rows])
        release_mae = mae([r["release"] for r in rows], [f["release"] for f in full_rows])
        quality_mae = mae([r["quality"] for r in rows], [f["quality"] for f in full_rows])
        cumulative_delta = rows[-1]["cumulative_release"] - full_rows[-1]["cumulative_release"]
        residue_l1 = l1_dict(run["final_memory"], full["final_memory"])
        final_state_distance = math.sqrt(
            (rows[-1]["quality"] - full_rows[-1]["quality"]) ** 2
            + ((rows[-1]["reservoir"] - full_rows[-1]["reservoir"]) ** 2) / 25.0
            + ((rows[-1]["cumulative_release"] - full_rows[-1]["cumulative_release"]) ** 2) / 10000.0
            + (residue_l1 ** 2) / 100.0
        )
    else:
        event_match = score_mae = release_mae = quality_mae = cumulative_delta = residue_l1 = final_state_distance = None
    return {
        "variant": run["variant"], "n_post_burn": len(rows),
        "pass_rate": round(mean(1.0 if r["passed"] else 0.0 for r in rows), 9),
        "mean_score": round(mean(r["passage_score"] for r in rows), 9),
        "mean_joint_term": round(mean(r["joint_term"] for r in rows), 9),
        "mean_counterfactual_term": round(mean(r["counterfactual_term"] for r in rows), 9),
        "mean_release": round(mean(r["release"] for r in rows), 9),
        "final_quality": round(rows[-1]["quality"], 9),
        "final_reservoir": round(rows[-1]["reservoir"], 9),
        "final_cumulative_release": round(rows[-1]["cumulative_release"], 9),
        "event_match_to_full": None if event_match is None else round(event_match, 9),
        "score_mae_to_full": None if score_mae is None else round(score_mae, 9),
        "release_mae_to_full": None if release_mae is None else round(release_mae, 9),
        "quality_mae_to_full": None if quality_mae is None else round(quality_mae, 9),
        "cumulative_release_delta_vs_full": None if cumulative_delta is None else round(cumulative_delta, 9),
        "final_residue_l1_to_full": None if residue_l1 is None else round(residue_l1, 9),
        "final_state_distance_to_full": None if final_state_distance is None else round(final_state_distance, 9),
        "final_memory_size": len(run["final_memory"]),
    }


def run(cfg):
    events = generate_events(cfg)
    variants = ["full_joint_boundary", "object_only_replay", "context_only_replay", "additive_object_context_model", "static_pairwise_replay", "joint_shuffle_control"]
    runs = {v: run_variant(v, cfg, events) for v in variants}
    full = runs["full_joint_boundary"]
    summaries = [summarize(runs[v], None if v == "full_joint_boundary" else full, cfg) for v in variants]
    lookup = {s["variant"]: s for s in summaries}
    criteria = {
        "object_only_event_match_to_full_le_0_88": lookup["object_only_replay"]["event_match_to_full"] <= 0.88,
        "context_only_event_match_to_full_le_0_88": lookup["context_only_replay"]["event_match_to_full"] <= 0.88,
        "additive_event_match_to_full_le_0_90": lookup["additive_object_context_model"]["event_match_to_full"] <= 0.90,
        "pairwise_event_match_to_full_le_0_92": lookup["static_pairwise_replay"]["event_match_to_full"] <= 0.92,
        "joint_shuffle_event_match_to_full_le_0_88": lookup["joint_shuffle_control"]["event_match_to_full"] <= 0.88,
        "additive_score_mae_to_full_ge_0_05": lookup["additive_object_context_model"]["score_mae_to_full"] >= 0.05,
        "pairwise_release_mae_to_full_ge_0_02": lookup["static_pairwise_replay"]["release_mae_to_full"] >= 0.02,
    }
    return {
        "experiment": "contextual_membrane_v4_joint_boundary",
        "date": "2026-07-08", "layer": "CONTEXTUAL_COMPONENT", "seed": cfg["seed"],
        "config": cfg, "variants": variants, "summaries": summaries, "criteria": criteria,
        "verdict": "PASS_JOINT_BOUNDARY" if all(criteria.values()) else "FAIL_OR_MIXED_JOINT_BOUNDARY",
        "base_event_count": len(events), "base_event_sample_first_16": events[:16],
        "row_sample_by_variant_first_8": {v: runs[v]["rows"][:8] for v in variants},
        "claim_boundary": [
            "This is a component-level joint-boundary test.",
            "PASS means the implemented membrane's decisions require full object/context joint state under the stated controls.",
            "This is not a quantum-specific claim and not a formal contextuality witness.",
            "No biological, consciousness, metabolism, self-repair, or physical matter synthesis claim is made.",
        ],
    }


def write_summary_csv(result, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(result["summaries"][0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(result["summaries"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260708)
    parser.add_argument("--steps", type=int, default=512)
    parser.add_argument("--out", type=Path, default=Path("data/contextual/contextual_membrane_v4_joint_boundary_seed20260708.json"))
    parser.add_argument("--csv", type=Path, default=Path("data/contextual/contextual_membrane_v4_joint_boundary_seed20260708_summary.csv"))
    args = parser.parse_args()
    cfg = dict(DEFAULT_CONFIG)
    cfg["seed"] = args.seed
    cfg["steps"] = args.steps
    result = run(cfg)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_summary_csv(result, args.csv)
    print(json.dumps({"experiment": result["experiment"], "verdict": result["verdict"], "summaries": result["summaries"], "criteria": result["criteria"]}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
