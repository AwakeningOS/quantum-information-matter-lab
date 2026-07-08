# Agent Handoff

Updated: 2026-07-08

## Repository role

This repository is a clean lab for contextual information-matter components.

The operating rule remains:

```text
No code + no raw log = no result.
```

## Research positioning

The target line is:

```text
put contextuality into the component decision boundary
```

Short form:

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

## Completed experiments

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

## contextual_reactor_v1_flow_controls lesson

```text
The membrane-to-flow result survives stronger classical controls.
Same pass rate is not enough.
Same signal distribution is not enough.
Lagged signal replay is not enough.
Additive object/context boundary is not enough.
Strong non-contextual reactor dynamics are not enough.
```

## contextual_membrane_quantum_anchor_probe_v1 lesson

```text
The previous surrogate audit has been replaced by explicit PM/KCBS-shaped probability tables.
The script computes deterministic assignment bounds by exhaustive enumeration:
  KCBS-style directed-transition bound = 2
  PM-style parity accuracy bound = 5/6
```

Key aggregate comparison:

```text
full_witness_table_anchor kcbs_witness_sum_mean = 2.256568549
same_marginals_independent_table kcbs_witness_sum_mean = 1.241136885
shuffled_context_table kcbs_witness_sum_mean = 1.986193805
strong_classical_table_baseline kcbs_witness_sum_mean = 1.873890389

full_witness_table_anchor pm_parity_accuracy_mean = 0.921974446
noncontextual_hidden_assignment_fit pm_parity_accuracy_mean = 0.804391588
strong_classical_table_baseline pm_parity_accuracy_mean = 0.813065892
```

No-disturbance in full expected tables:

```text
full_witness_table_anchor kcbs_no_disturbance_max_abs_mean = 0.000000000000
full_witness_table_anchor pm_no_disturbance_max_abs_mean = 0.000000000000
```

## Recommended next experiment

```text
contextual_membrane_quantum_anchor_probe_v2_hardware_mapping
```

Core rule:

```text
Map the explicit witness-table anchor to existing PM/KCBS hardware-backed result formats.
Separate simulated table values from real QPU witness values.
Add finite-shot noise model and compare with hardware witness margins.
Do not promote quantum-specific claims unless hardware-backed witness controls pass.
```

## Claim boundary

The current results are contextual/classical component results plus witness-shaped audit-bridge results.

They do not establish quantum-specific behavior, formal measurement contextuality of a physical implementation, life, metabolism, self-repair, consciousness, or physical matter synthesis.
