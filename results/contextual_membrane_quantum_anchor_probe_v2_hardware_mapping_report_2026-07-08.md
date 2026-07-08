# Result: contextual_membrane_quantum_anchor_probe_v2_hardware_mapping

Status: RAW_LOG_BACKED  
Generator script: `scripts/contextual/contextual_membrane_quantum_anchor_probe_v2_hardware_mapping.py`  
Raw log: `data/contextual/contextual_membrane_quantum_anchor_probe_v2_hardware_mapping_seed20260708.json`  
Summary CSV: `data/contextual/contextual_membrane_quantum_anchor_probe_v2_hardware_mapping_seed20260708_summary.csv`  
Run command: `python scripts/contextual/contextual_membrane_quantum_anchor_probe_v2_hardware_mapping.py --seed 20260708 --out data/contextual/contextual_membrane_quantum_anchor_probe_v2_hardware_mapping_seed20260708.json --csv data/contextual/contextual_membrane_quantum_anchor_probe_v2_hardware_mapping_seed20260708_summary.csv`  
Layer: QUANTUM_AUDIT  
Verdict: PASS_HARDWARE_MAPPING_AUDIT_CANDIDATE_NOT_NEW_QPU_RESULT  
Claim boundary: hardware-format compatibility audit only; no new QPU result and no quantum-specific promotion.

## Summary

`contextual_membrane_quantum_anchor_probe_v2_hardware_mapping` maps the explicit witness-table anchor from v1 to existing PM/KCBS hardware-backed witness result formats.

The result is:

```text
PASS_HARDWARE_MAPPING_AUDIT_CANDIDATE_NOT_NEW_QPU_RESULT
```

This is not a new hardware experiment. It is not a new quantum result. It is a format-compatibility audit that compares simulated witness-table margins with existing hardware-backed witness margins without pooling them.

## Simulated table inputs

```text
KCBS table S = 2.256568549
KCBS bound = 2
KCBS table violation = 0.256568549

PM table parity accuracy = 0.921974446
PM parity bound = 5/6
PM chi-equivalent = 12 * accuracy - 6 = 5.063693352
PM chi bound = 4
PM chi-equivalent violation = 1.063693352
```

## Existing hardware-backed witness inputs

```text
KCBS hardware S = 2.2232666015625
KCBS hardware violation = 0.2232666015625
KCBS hardware SE = 0.008678203935971344
KCBS hardware z = 25.727

PM hardware xplus chi = 5.049805
PM hardware xplus violation = 1.049805
PM hardware xplus SE = 0.028808
PM hardware xplus z = 36.44

PM hardware yplus chi = 4.857422
PM hardware yplus violation = 0.857422
PM hardware yplus SE = 0.031218
PM hardware yplus z = 27.47

PM hardware z0 chi = 4.644531
PM hardware z0 violation = 0.644531
PM hardware z0 SE = 0.034165
PM hardware z0 z = 18.87
```

## Main comparison table

| Hardware result | Family | Sim value | Sim violation | Hardware value | Hardware violation | Hardware SE | Ratio sim/hardware | Delta sim-hardware | Evidence relation |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| kcbs_kingston | KCBS | 2.256568549 | 0.256568549 | 2.223266601562 | 0.223266601562 | 0.008678203936 | 1.149157766 | 0.033301947437 | compared_not_pooled |
| pm_xplus_kingston | PM | 5.063693352 | 1.063693352 | 5.049805000000 | 1.049805000000 | 0.028808000000 | 1.013229459 | 0.013888352000 | compared_not_pooled |
| pm_yplus_kingston | PM | 5.063693352 | 1.063693352 | 4.857422000000 | 0.857422000000 | 0.031218000000 | 1.240571565 | 0.206271352000 | compared_not_pooled |
| pm_z0_kingston | PM | 5.063693352 | 1.063693352 | 4.644531000000 | 0.644531000000 | 0.034165000000 | 1.650336992 | 0.419162352000 | compared_not_pooled |

## Criteria

| Criterion | Result |
|---|---|
| kcbs_sim_and_hardware_margins_same_sign | True |
| pm_sim_and_all_hardware_margins_same_sign | True |
| kcbs_margin_ratio_between_0_5_and_2_0 | True |
| pm_margin_ratios_between_0_5_and_2_0 | True |
| kcbs_sim_finite_shot_survival_ge_0_999 | True |
| kcbs_hardware_finite_shot_survival_ge_0_999 | True |
| pm_sim_finite_shot_survival_min_ge_0_999 | True |
| pm_hardware_finite_shot_survival_min_ge_0_999 | True |
| simulated_and_hardware_evidence_not_pooled | True |
| no_quantum_specific_claim_promoted | True |

## Interpretation

This result supports only the following cautious claim:

```text
The explicit simulated witness-table anchor can be mapped into the existing PM/KCBS hardware-backed witness result formats with same-sign, comparable-scale margins and finite-shot survival under the hardware SE scale.
```

The result does not say the simulated component is quantum. It does not say the component was run on hardware. It does not combine simulated and hardware evidence into one statistic.

The useful outcome is narrower:

```text
The audit formats now line up.
```

## Why this matters

Before this step, the anchor line had only internal table evidence.

After this step, the simulated witness-table margins and the existing hardware-backed witness margins can be compared in the same reporting convention:

```text
KCBS: S value, bound, violation, SE, z
PM: chi value, bound, violation, SE, z
```

That makes the next step possible: a real hardware-backed component-specific anchor audit, or a finite-shot table-to-hardware stress test.

## Limitations

```text
1. This is not a new QPU run.
2. This is not new hardware evidence.
3. Simulated table margins and hardware witness margins are compared, not pooled.
4. The component itself has not been implemented as a hardware witness.
5. No quantum-specific behavior is promoted from this result alone.
6. No biological, consciousness, metabolism, self-repair, or physical matter synthesis claim is made.
```

## Next local lesson

The next experiment should be a stress test before any new hardware claim:

```text
contextual_membrane_quantum_anchor_probe_v3_finite_shot_stress:
  inject finite-shot sampling into the explicit witness tables
  vary shots from low to hardware-like regimes
  compare survival probability against PM/KCBS margins
  add adversarial no-disturbance drift
  require witness survival without relying on exact expected tables
```

Only after that should a component-specific hardware-backed anchor run be considered.
