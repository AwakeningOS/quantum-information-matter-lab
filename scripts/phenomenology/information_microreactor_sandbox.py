#!/usr/bin/env python3
"""
Classical-effective information microreactor sandbox.

Layer: CLASSICAL_COMPONENT / classical-effective phenomenology

Purpose:
    Assemble source, road/channel, selective membrane, converter, reservoir,
    sink/release, terrain writing, stress, stabilizer, and contaminant into one
    small deterministic sandbox.

This is not a quantum-witness experiment and makes no quantum-specific claim.
Migrated from AwakeningOS/AwakeningOS-Quantum-lattice as a reusable baseline.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np


@dataclass(frozen=True)
class Params:
    A_rate: float = 2.0
    B_rate: float = 0.15
    D_rate: float = 0.02
    C_rate: float = 0.02
    pore_A: float = 0.08
    pore_B: float = 0.005
    capacity: float = 120.0
    release_rate: float = 0.035
    sink_cap: float = 999.0
    k_conv: float = 0.65
    damage_coeff: float = 0.015
    repair_coeff: float = 0.006
    stabilizer_protect: float = 0.80
    poison_coeff: float = 1.2
    quality_coeff: float = 2.0
    backpressure_strength: float = 0.65
    road_source_gain: float = 0.0
    terrain_write: float = 0.04
    terrain_decay: float = 0.985
    pulse_amp: float = 0.25


@dataclass(frozen=True)
class Config:
    seed: int = 20260708
    steps: int = 800
    burn: int = 200


def rf(x: float) -> float:
    y = round(float(x), 12)
    return 0.0 if abs(y) < 5e-13 else y


def scenarios() -> Dict[str, Params]:
    return {
        "normal": Params(),
        "high_load": Params(A_rate=5.0),
        "stress": Params(D_rate=0.45, C_rate=0.0),
        "stabilizer": Params(D_rate=0.45, C_rate=2.0),
        "leaky_membrane": Params(pore_B=0.05, B_rate=0.4),
        "road_fed": Params(road_source_gain=2.0, terrain_write=0.08),
        "storage_heavy": Params(capacity=40.0, release_rate=0.003, backpressure_strength=0.9),
    }


def simulate(name: str, p: Params, cfg: Config) -> Tuple[Dict[str, Any], List[Dict[str, float]]]:
    inside_A = 0.0
    inside_B = 0.0
    reservoir = 0.0
    integrity = 1.0
    terrain = 0.0
    rows: List[Dict[str, float]] = []

    for t in range(cfg.steps):
        pulse = 1.0 + p.pulse_amp * math.sin(2.0 * math.pi * t / 64.0)
        road_boost = 1.0 + p.road_source_gain * (terrain / (1.0 + terrain))
        source_A = p.A_rate * pulse * road_boost
        source_B = p.B_rate
        D = p.D_rate
        C = p.C_rate

        protect = p.stabilizer_protect * (C / (1.0 + C))
        damage = p.damage_coeff * D * (1.0 - protect)
        repair = p.repair_coeff * C * (1.0 - integrity)
        integrity = min(1.0, max(0.0, integrity - damage + repair))

        fill_frac_pre = reservoir / max(p.capacity, 1e-9)
        backpressure = max(0.02, 1.0 - p.backpressure_strength * fill_frac_pre)

        perm_A = p.pore_A * integrity * backpressure
        perm_B = p.pore_B * integrity * (1.0 + 0.5 * (1.0 - integrity))
        A_in = source_A * perm_A
        B_in = source_B * perm_B

        inside_A += A_in
        inside_B += B_in

        poison = 1.0 / (1.0 + p.poison_coeff * inside_B)
        conv_rate = p.k_conv * poison * backpressure
        P_generated = min(inside_A, conv_rate * inside_A)
        inside_A -= P_generated

        quality = 1.0 / (1.0 + p.quality_coeff * inside_B)
        inside_B *= 0.985

        available = max(0.0, p.capacity - reservoir)
        P_accept = min(P_generated, available)
        overflow = max(0.0, P_generated - available)
        reservoir += P_accept

        release = min(reservoir, reservoir * p.release_rate, p.sink_cap)
        reservoir -= release

        terrain = terrain * p.terrain_decay + release * p.terrain_write * quality

        rows.append(
            {
                "t": float(t),
                "source_A": source_A,
                "source_B": source_B,
                "A_in": A_in,
                "B_in": B_in,
                "P_generated": P_generated,
                "P_accept": P_accept,
                "release": release,
                "overflow": overflow,
                "reservoir": reservoir,
                "fill_frac": fill_frac_pre,
                "integrity": integrity,
                "terrain": terrain,
                "quality": quality,
                "poison": poison,
                "backpressure": backpressure,
                "damage": damage,
                "repair": repair,
            }
        )

    post = rows[cfg.burn :]

    def total(key: str) -> float:
        return sum(row[key] for row in post)

    def mean(key: str) -> float:
        return total(key) / len(post)

    def std(key: str) -> float:
        m = mean(key)
        return math.sqrt(sum((row[key] - m) ** 2 for row in post) / max(1, len(post) - 1))

    source_A_total = total("source_A")
    source_B_total = total("source_B")
    A_in_total = total("A_in")
    B_in_total = total("B_in")
    P_generated_total = total("P_generated")
    P_release_total = total("release")
    P_overflow_total = total("overflow")

    permeability_A = A_in_total / source_A_total if source_A_total > 0 else 0.0
    permeability_B = B_in_total / source_B_total if source_B_total > 0 else 0.0
    selectivity = permeability_A / (permeability_B + 1e-12)
    release_fraction = P_release_total / (P_generated_total + 1e-9) if P_generated_total > 1e-9 else 0.0
    overflow_fraction = P_overflow_total / (P_generated_total + 1e-9) if P_generated_total > 1e-9 else 0.0
    source_cv = std("source_A") / (mean("source_A") + 1e-9)
    release_cv = std("release") / (mean("release") + 1e-9)

    summary = {
        "scenario": name,
        "source_A_total": source_A_total,
        "A_in_total": A_in_total,
        "B_in_total": B_in_total,
        "permeability_A": permeability_A,
        "permeability_B": permeability_B,
        "selectivity": selectivity,
        "P_generated": P_generated_total,
        "P_release": P_release_total,
        "P_overflow": P_overflow_total,
        "release_fraction": release_fraction,
        "overflow_fraction": overflow_fraction,
        "mean_reservoir": mean("reservoir"),
        "final_reservoir": rows[-1]["reservoir"],
        "mean_fill_fraction": mean("reservoir") / p.capacity,
        "mean_backpressure": mean("backpressure"),
        "final_integrity": rows[-1]["integrity"],
        "mean_integrity": mean("integrity"),
        "mean_quality": mean("quality"),
        "terrain_written": rows[-1]["terrain"],
        "efficiency_release_per_A": P_release_total / (source_A_total + 1e-9),
        "stability_window": mean("integrity") * (1.0 - overflow_fraction) * mean("quality"),
        "release_cv": release_cv,
        "source_cv": source_cv,
        "smoothing_ratio": release_cv / (source_cv + 1e-9),
    }
    return summary, rows


def run(seed: int = 20260708) -> Dict[str, Any]:
    # Seed retained for interface consistency. This sandbox is deterministic.
    _ = np.random.default_rng(seed)
    cfg = Config(seed=seed)
    summaries = []
    params = scenarios()
    for name, p in params.items():
        summary, _rows = simulate(name, p, cfg)
        summaries.append({k: (rf(v) if isinstance(v, float) else v) for k, v in summary.items()})

    return {
        "experiment": "information_microreactor_sandbox",
        "date": "2026-07-08",
        "layer": "CLASSICAL_COMPONENT",
        "model": "source-road-membrane-converter-reservoir-sink terrain sandbox",
        "seed": seed,
        "config": asdict(cfg),
        "scenario_params": {name: asdict(p) for name, p in params.items()},
        "summaries": summaries,
        "limitations": [
            "Classical-effective deterministic sandbox, not a quantum-witness experiment.",
            "No quantum advantage or quantum-specific claim.",
            "Not a biological metabolism, self-repair, or life-like system.",
            "Component boundaries are modular so future contextual/quantum audits can target substructures separately.",
        ],
    }


def write_csv(result: Dict[str, Any], path: Path) -> None:
    rows = result["summaries"]
    fields = list(rows[0].keys())
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260708)
    parser.add_argument("--out", type=Path, default=Path("data/microreactor/information_microreactor_sandbox_seed20260708.json"))
    parser.add_argument("--csv", type=Path, default=Path("data/microreactor/information_microreactor_sandbox_seed20260708_summary.csv"))
    args = parser.parse_args()

    result = run(seed=args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(result, args.csv)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
