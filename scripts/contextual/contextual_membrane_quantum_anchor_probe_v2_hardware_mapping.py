#!/usr/bin/env python3
"""contextual_membrane_quantum_anchor_probe_v2_hardware_mapping

Layer: QUANTUM_AUDIT

Maps the explicit witness-table anchor from v1 to existing PM/KCBS hardware-backed
witness result formats. This is a compatibility audit only. It does not produce
new QPU evidence and does not promote a quantum-specific claim.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np

SIMULATED_V1 = {
    "kcbs_table_s": 2.256568549,
    "kcbs_bound": 2.0,
    "pm_parity_accuracy": 0.921974446,
    "pm_parity_bound": 5.0 / 6.0,
}

HARDWARE = {
    "kcbs_kingston": {
        "family": "KCBS",
        "statistic": "S_KCBS",
        "value": 2.2232666015625,
        "bound": 2.0,
        "violation": 0.2232666015625,
        "se": 0.008678203935971344,
        "z": 25.727,
        "source_note": "existing IBM Kingston KCBS hardware-backed witness result",
    },
    "pm_xplus_kingston": {
        "family": "PM",
        "statistic": "chi_PM",
        "value": 5.049805,
        "bound": 4.0,
        "violation": 1.049805,
        "se": 0.028808,
        "z": 36.44,
        "source_note": "existing IBM Kingston PM hardware-backed witness result, xplus",
    },
    "pm_yplus_kingston": {
        "family": "PM",
        "statistic": "chi_PM",
        "value": 4.857422,
        "bound": 4.0,
        "violation": 0.857422,
        "se": 0.031218,
        "z": 27.47,
        "source_note": "existing IBM Kingston PM hardware-backed witness result, yplus",
    },
    "pm_z0_kingston": {
        "family": "PM",
        "statistic": "chi_PM",
        "value": 4.644531,
        "bound": 4.0,
        "violation": 0.644531,
        "se": 0.034165,
        "z": 18.87,
        "source_note": "existing IBM Kingston PM hardware-backed witness result, z0",
    },
}


def normal_survival_probability(margin: float, se: float) -> float:
    # Probability that a normal estimate with mean=margin and std=se remains positive.
    z = margin / se
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def monte_carlo_survival(seed: int, margin: float, se: float, draws: int = 20000) -> float:
    rng = np.random.default_rng(seed)
    samples = rng.normal(loc=margin, scale=se, size=draws)
    return float(np.mean(samples > 0.0))


def run(seed: int) -> dict:
    pm_chi_equiv = 12.0 * SIMULATED_V1["pm_parity_accuracy"] - 6.0
    pm_chi_violation = pm_chi_equiv - 4.0
    kcbs_violation = SIMULATED_V1["kcbs_table_s"] - SIMULATED_V1["kcbs_bound"]

    simulated = {
        "kcbs_table": {
            "family": "KCBS",
            "statistic": "S_KCBS",
            "value": SIMULATED_V1["kcbs_table_s"],
            "bound": SIMULATED_V1["kcbs_bound"],
            "violation": kcbs_violation,
            "source_note": "simulated explicit witness-table audit value from contextual_membrane_quantum_anchor_probe_v1",
        },
        "pm_table_chi_equivalent": {
            "family": "PM",
            "statistic": "chi_PM_equivalent",
            "value": pm_chi_equiv,
            "bound": 4.0,
            "violation": pm_chi_violation,
            "source_note": "simulated PM parity accuracy mapped by chi = 12 * accuracy - 6",
        },
    }

    comparisons = []
    for name, hw in HARDWARE.items():
        sim_key = "kcbs_table" if hw["family"] == "KCBS" else "pm_table_chi_equivalent"
        sim = simulated[sim_key]
        ratio = sim["violation"] / hw["violation"]
        delta = sim["violation"] - hw["violation"]
        sim_survival_normal = normal_survival_probability(sim["violation"], hw["se"])
        hw_survival_normal = normal_survival_probability(hw["violation"], hw["se"])
        comparisons.append({
            "hardware_result": name,
            "family": hw["family"],
            "simulated_statistic": sim["statistic"],
            "simulated_value": round(sim["value"], 12),
            "simulated_bound": sim["bound"],
            "simulated_violation": round(sim["violation"], 12),
            "hardware_statistic": hw["statistic"],
            "hardware_value": round(hw["value"], 12),
            "hardware_bound": hw["bound"],
            "hardware_violation": round(hw["violation"], 12),
            "hardware_se": round(hw["se"], 12),
            "hardware_z": hw["z"],
            "sim_to_hardware_margin_ratio": round(ratio, 9),
            "margin_delta_sim_minus_hardware": round(delta, 12),
            "same_margin_sign": bool(sim["violation"] > 0 and hw["violation"] > 0),
            "sim_finite_shot_survival_normal": round(sim_survival_normal, 12),
            "hardware_finite_shot_survival_normal": round(hw_survival_normal, 12),
            "sim_finite_shot_survival_mc": round(monte_carlo_survival(seed + len(comparisons), sim["violation"], hw["se"]), 12),
            "hardware_finite_shot_survival_mc": round(monte_carlo_survival(seed + 100 + len(comparisons), hw["violation"], hw["se"]), 12),
            "evidence_relation": "compared_not_pooled",
        })

    kcbs_ratios = [r["sim_to_hardware_margin_ratio"] for r in comparisons if r["family"] == "KCBS"]
    pm_ratios = [r["sim_to_hardware_margin_ratio"] for r in comparisons if r["family"] == "PM"]
    sim_survivals = [r["sim_finite_shot_survival_normal"] for r in comparisons]
    hw_survivals = [r["hardware_finite_shot_survival_normal"] for r in comparisons]

    criteria = {
        "kcbs_sim_and_hardware_margins_same_sign": all(r["same_margin_sign"] for r in comparisons if r["family"] == "KCBS"),
        "pm_sim_and_all_hardware_margins_same_sign": all(r["same_margin_sign"] for r in comparisons if r["family"] == "PM"),
        "kcbs_margin_ratio_between_0_5_and_2_0": all(0.5 <= r <= 2.0 for r in kcbs_ratios),
        "pm_margin_ratios_between_0_5_and_2_0": all(0.5 <= r <= 2.0 for r in pm_ratios),
        "kcbs_sim_finite_shot_survival_ge_0_999": min(r["sim_finite_shot_survival_normal"] for r in comparisons if r["family"] == "KCBS") >= 0.999,
        "kcbs_hardware_finite_shot_survival_ge_0_999": min(r["hardware_finite_shot_survival_normal"] for r in comparisons if r["family"] == "KCBS") >= 0.999,
        "pm_sim_finite_shot_survival_min_ge_0_999": min(r["sim_finite_shot_survival_normal"] for r in comparisons if r["family"] == "PM") >= 0.999,
        "pm_hardware_finite_shot_survival_min_ge_0_999": min(r["hardware_finite_shot_survival_normal"] for r in comparisons if r["family"] == "PM") >= 0.999,
        "simulated_and_hardware_evidence_not_pooled": all(r["evidence_relation"] == "compared_not_pooled" for r in comparisons),
        "no_quantum_specific_claim_promoted": True,
    }

    return {
        "experiment": "contextual_membrane_quantum_anchor_probe_v2_hardware_mapping",
        "date": "2026-07-08",
        "layer": "QUANTUM_AUDIT",
        "seed": seed,
        "inputs": {
            "simulated_v1": SIMULATED_V1,
            "hardware_backed_witnesses": HARDWARE,
        },
        "mapped_simulated_values": simulated,
        "comparisons": comparisons,
        "summary": {
            "kcbs_simulated_violation": round(kcbs_violation, 12),
            "kcbs_hardware_violation": HARDWARE["kcbs_kingston"]["violation"],
            "kcbs_margin_ratio_sim_to_hardware": kcbs_ratios[0],
            "pm_simulated_chi_equivalent": round(pm_chi_equiv, 12),
            "pm_simulated_chi_violation": round(pm_chi_violation, 12),
            "pm_margin_ratio_min": min(pm_ratios),
            "pm_margin_ratio_max": max(pm_ratios),
            "finite_shot_survival_min_simulated": min(sim_survivals),
            "finite_shot_survival_min_hardware": min(hw_survivals),
        },
        "criteria": criteria,
        "verdict": "PASS_HARDWARE_MAPPING_AUDIT_CANDIDATE_NOT_NEW_QPU_RESULT" if all(criteria.values()) else "FAIL_OR_MIXED_HARDWARE_MAPPING_AUDIT",
        "claim_boundary": [
            "This is a hardware-format compatibility audit only.",
            "Simulated table values and hardware-backed witness values are compared but not pooled.",
            "This does not create a new QPU result and does not promote a quantum-specific claim for the component.",
            "Any quantum-specific claim still requires a separate real quantum witness or hardware-backed audit of the component itself.",
        ],
    }


def write_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260708)
    parser.add_argument("--out", type=Path, default=Path("data/contextual/contextual_membrane_quantum_anchor_probe_v2_hardware_mapping_seed20260708.json"))
    parser.add_argument("--csv", type=Path, default=Path("data/contextual/contextual_membrane_quantum_anchor_probe_v2_hardware_mapping_seed20260708_summary.csv"))
    args = parser.parse_args()

    result = run(args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(result["comparisons"], args.csv)

    print(json.dumps({
        "experiment": result["experiment"],
        "verdict": result["verdict"],
        "summary": result["summary"],
        "criteria": result["criteria"],
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
