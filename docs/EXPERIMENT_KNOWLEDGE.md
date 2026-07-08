# Experiment Knowledge Base

Updated: 2026-07-08

## General operating knowledge

A result should be promoted only when the repository contains:

```text
protocol
generator script
raw log
report
STATUS entry
reproducibility check
```

## Research positioning

The intended line is:

```text
put contextuality/context structure into the component decision boundary
```

## Completed result index

```text
contextual_membrane_v0 = PASS_COMPONENT_BEHAVIOR
contextual_membrane_v1_memory_ablation = PASS_MEMORY_DEPENDENT_BOUNDARY
contextual_membrane_v2_counterfactual_residue = PASS_COUNTERFACTUAL_RESIDUE
contextual_membrane_v3_order_effect = PASS_ORDER_EFFECT
contextual_membrane_v4_joint_boundary = PASS_JOINT_BOUNDARY
contextual_reactor_v0_membrane_to_flow = PASS_MEMBRANE_TO_FLOW_PROPAGATION
contextual_reactor_v1_flow_controls = PASS_HARDENED_MEMBRANE_TO_FLOW_CONTROLS
contextual_membrane_quantum_anchor_probe = PASS_ANCHOR_CANDIDATE_SURROGATE_NOT_QUANTUM
contextual_membrane_quantum_anchor_probe_v1 = PASS_STRICT_WITNESS_TABLE_AUDIT_CANDIDATE_NOT_QUANTUM
contextual_membrane_quantum_anchor_probe_v2_hardware_mapping = PASS_HARDWARE_MAPPING_AUDIT_CANDIDATE_NOT_NEW_QPU_RESULT
```

## Core component lesson

```text
A contextual membrane can control the flow of a downstream reaction field in this designed component.
This result survived multi-seed, matched pass-rate, matched signal, additive-boundary, and strong no-membrane controls.
```

## contextual_membrane_quantum_anchor_probe_v1 knowledge

```text
Verdict = PASS_STRICT_WITNESS_TABLE_AUDIT_CANDIDATE_NOT_QUANTUM
KCBS-style directed-transition bound = 2
PM-style parity accuracy bound = 5/6 = 0.8333333333333334
full_witness_table_anchor kcbs_witness_sum_mean = 2.256568549
full_witness_table_anchor pm_parity_accuracy_mean = 0.921974446
full_witness_table_anchor kcbs_no_disturbance_max_abs_mean = 0.000000000000
full_witness_table_anchor pm_no_disturbance_max_abs_mean = 0.000000000000
```

Lesson:

```text
The simulated membrane anchor can be represented by explicit PM/KCBS-shaped probability tables that pass deterministic-bound and no-disturbance checks under the stated controls.
```

## contextual_membrane_quantum_anchor_probe_v2_hardware_mapping knowledge

### What was tested

Hardware-format compatibility audit:

```text
Map v1 simulated witness-table values to existing PM/KCBS hardware-backed witness reporting formats.
Keep simulated table values and hardware-backed witness values separate.
Compare margins, margin ratios, and finite-shot survival under hardware SE scale.
```

### Result snapshot

```text
Verdict = PASS_HARDWARE_MAPPING_AUDIT_CANDIDATE_NOT_NEW_QPU_RESULT

KCBS simulated S = 2.256568549
KCBS simulated violation = 0.256568549
KCBS hardware S = 2.2232666015625
KCBS hardware violation = 0.2232666015625
KCBS sim/hardware margin ratio = 1.149157766

PM simulated chi-equivalent = 5.063693352
PM simulated violation = 1.063693352
PM hardware xplus violation = 1.049805
PM hardware yplus violation = 0.857422
PM hardware z0 violation = 0.644531
PM sim/hardware margin ratio range = 1.013229459 to 1.650336992
```

### Lesson

The audit formats now line up:

```text
KCBS: S value, bound, violation, SE, z
PM: chi value, bound, violation, SE, z
```

This makes a finite-shot stress test and a future component-specific hardware-backed audit easier to design.

### Do not claim

```text
Do not claim this is a new QPU result.
Do not claim this is new hardware evidence.
Do not claim simulated table margins and hardware margins were pooled.
Do not claim this proves formal measurement contextuality of the component.
Do not claim this demonstrates biological organization or consciousness.
Do not claim this demonstrates matter synthesis.
```

## Next experiment option

```text
contextual_membrane_quantum_anchor_probe_v3_finite_shot_stress
```

Required improvements:

```text
inject finite-shot sampling into the explicit witness tables
vary shots from low to hardware-like regimes
compare survival probability against PM/KCBS margins
add adversarial no-disturbance drift
require witness survival without relying on exact expected tables
```
