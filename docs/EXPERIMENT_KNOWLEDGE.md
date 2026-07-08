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

Staged program:

```text
v0 = context-looking membrane
v1 = memory-bearing boundary
v2 = counterfactual-residue boundary
v3 = order-sensitive boundary
v4 = joint/non-additive boundary
reactor v0 = downstream propagation
reactor v1 = hardened propagation controls
quantum anchor = separate audit bridge to witness logic
quantum anchor v1 = explicit witness-table audit candidate
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
```

## Core component lesson

```text
A contextual membrane can control the flow of a downstream reaction field in this designed component.
This result survived multi-seed, matched pass-rate, matched signal, additive-boundary, and strong no-membrane controls.
```

## contextual_membrane_quantum_anchor_probe_v1 knowledge

### What was tested

Explicit witness-table audit candidate:

```text
KCBS-style directed-transition probability table
PM-style 3x3 parity table
no-disturbance / marginal-consistency checks
exhaustive deterministic assignment bound checks
```

Variants:

```text
full_witness_table_anchor
additive_boundary_table
same_marginals_independent_table
shuffled_context_table
noncontextual_hidden_assignment_fit
strong_classical_table_baseline
```

### Computed bounds

```text
KCBS-style directed-transition bound = 2
PM-style parity accuracy bound = 5/6 = 0.8333333333333334
```

### Result snapshot

```text
Verdict = PASS_STRICT_WITNESS_TABLE_AUDIT_CANDIDATE_NOT_QUANTUM

full_witness_table_anchor kcbs_witness_sum_mean = 2.256568549
additive_boundary_table kcbs_witness_sum_mean = 1.601132037
same_marginals_independent_table kcbs_witness_sum_mean = 1.241136885
shuffled_context_table kcbs_witness_sum_mean = 1.986193805
noncontextual_hidden_assignment_fit kcbs_witness_sum_mean = 1.735531896
strong_classical_table_baseline kcbs_witness_sum_mean = 1.873890389

full_witness_table_anchor pm_parity_accuracy_mean = 0.921974446
additive_boundary_table pm_parity_accuracy_mean = 0.628229114
same_marginals_independent_table pm_parity_accuracy_mean = 0.608851602
shuffled_context_table pm_parity_accuracy_mean = 0.696225106
noncontextual_hidden_assignment_fit pm_parity_accuracy_mean = 0.804391588
strong_classical_table_baseline pm_parity_accuracy_mean = 0.813065892
```

### No-disturbance snapshot

```text
full_witness_table_anchor kcbs_no_disturbance_max_abs_mean = 0.000000000000
full_witness_table_anchor pm_no_disturbance_max_abs_mean = 0.000000000000
```

### Lesson

The simulated membrane anchor can be represented by explicit PM/KCBS-shaped probability tables that pass deterministic-bound and no-disturbance checks under the stated controls.

This is stronger than the previous surrogate audit but remains an audit-candidate result only.

### Do not claim

```text
Do not claim this demonstrates quantum-specific behavior.
Do not claim this is hardware-backed.
Do not claim this proves formal measurement contextuality of a physical implementation.
Do not claim this demonstrates biological organization or consciousness.
Do not claim this demonstrates matter synthesis.
```

## Next experiment option

```text
contextual_membrane_quantum_anchor_probe_v2_hardware_mapping
```

Required improvements:

```text
map the explicit witness-table anchor to existing PM/KCBS hardware-backed result formats
separate simulated table values from real QPU witness values
add finite-shot noise model and compare with hardware witness margins
keep quantum-specific claim promotion gated by hardware-backed witness controls
```
