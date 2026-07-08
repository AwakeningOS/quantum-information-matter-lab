#!/usr/bin/env python3
"""
Contextual component skeleton.

Layer: CONTEXTUAL_COMPONENT

Purpose:
    Start the next phase after the measurement-boundary audit: components whose
    response depends on question/context structure, not only scalar flow.

This is a design scaffold for building contextual information-matter parts.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np


Context = str
Object = str


@dataclass(frozen=True)
class Config:
    seed: int = 20260708
    steps: int = 64
    memory_decay: float = 0.92
    context_gain: float = 0.35
    incompatibility_penalty: float = 0.25


def compatibility_graph() -> Dict[Tuple[Context, Context], bool]:
    """Toy compatibility graph for questions/contexts.

    Compatible contexts can be jointly read without resetting the component.
    Incompatible contexts write tension into contextual memory.
    """
    contexts = ["identity", "path", "boundary", "history"]
    graph: Dict[Tuple[Context, Context], bool] = {}
    for a in contexts:
        for b in contexts:
            graph[(a, b)] = a == b
    compatible_pairs = {
        ("identity", "history"),
        ("history", "identity"),
        ("path", "boundary"),
        ("boundary", "path"),
    }
    for pair in compatible_pairs:
        graph[pair] = True
    return graph


def contextual_membrane_score(obj: Object, context: Context, memory: Dict[str, float], cfg: Config) -> float:
    """Return passage score for a toy contextual membrane.

    This deliberately uses a context-dependent rule. It is a component
    interface to be audited and improved in later experiments.
    """
    base = {
        "A": 0.70,
        "B": 0.25,
        "P": 0.55,
        "Q": 0.40,
    }.get(obj, 0.10)

    context_bias = {
        "identity": {"A": 0.15, "P": 0.20},
        "path": {"A": -0.10, "B": 0.20},
        "boundary": {"B": -0.15, "Q": 0.15},
        "history": {"P": 0.10, "Q": 0.10},
    }.get(context, {}).get(obj, 0.0)

    memory_bias = cfg.context_gain * memory.get(f"seen:{context}:{obj}", 0.0)
    score = base + context_bias + memory_bias
    return float(np.clip(score, 0.0, 1.0))


def run(cfg: Config) -> Dict[str, object]:
    rng = np.random.default_rng(cfg.seed)
    contexts: List[Context] = ["identity", "path", "boundary", "history"]
    objects: List[Object] = ["A", "B", "P", "Q"]
    compat = compatibility_graph()
    memory: Dict[str, float] = {}
    rows = []
    previous_context: Context | None = None

    for t in range(cfg.steps):
        context = contexts[int(rng.integers(0, len(contexts)))]
        obj = objects[int(rng.integers(0, len(objects)))]
        compatible_with_previous = True if previous_context is None else compat[(previous_context, context)]

        # Decay memory.
        memory = {k: v * cfg.memory_decay for k, v in memory.items() if abs(v * cfg.memory_decay) > 1e-9}

        score = contextual_membrane_score(obj, context, memory, cfg)
        if not compatible_with_previous:
            score = max(0.0, score - cfg.incompatibility_penalty)
            memory[f"incompat:{previous_context}->{context}"] = memory.get(f"incompat:{previous_context}->{context}", 0.0) + 1.0

        passed = bool(rng.random() < score)
        memory[f"seen:{context}:{obj}"] = memory.get(f"seen:{context}:{obj}", 0.0) + (1.0 if passed else 0.25)

        rows.append(
            {
                "t": t,
                "context": context,
                "object": obj,
                "previous_context": previous_context or "NONE",
                "compatible_with_previous": compatible_with_previous,
                "passage_score": round(score, 6),
                "passed": passed,
                "memory_size": len(memory),
            }
        )
        previous_context = context

    pass_rate = sum(1 for r in rows if r["passed"]) / len(rows)
    incompatible_rate = sum(1 for r in rows if not r["compatible_with_previous"]) / len(rows)

    return {
        "experiment": "contextual_component_skeleton",
        "layer": "CONTEXTUAL_COMPONENT",
        "seed": cfg.seed,
        "config": asdict(cfg),
        "contexts": contexts,
        "objects": objects,
        "summary": {
            "pass_rate": round(pass_rate, 6),
            "incompatible_transition_rate": round(incompatible_rate, 6),
            "final_memory_size": len(memory),
        },
        "rows": rows,
        "claim_boundary": [
            "Starter component scaffold.",
            "Designed contextual behavior; audit controls come in later experiments.",
            "Promote only after protocol, raw log, report, STATUS entry, and check.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260708)
    parser.add_argument("--steps", type=int, default=64)
    parser.add_argument("--out", type=Path, default=Path("data/contextual/contextual_component_seed20260708.json"))
    args = parser.parse_args()

    result = run(Config(seed=args.seed, steps=args.steps))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
