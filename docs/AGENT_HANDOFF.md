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
quantum anchor v2 = hardware-format compatibility audit
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
contextual_membrane_quantum_anchor_probe_v2_hardware_mapping = PASS_HARDWARE_MAPPING_AUDIT_CANDIDATE_NOT_NEW_QPU_RESULT
```

## contextual_membrane_quantum_anchor_probe_v2 lesson

```text
The explicit witness-table anchor can be mapped to existing PM/KCBS hardware-backed witness result formats.
Simulated table values and hardware-backed witness values are compared but not pooled.
```

Key comparison:

```text
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

Main rule:

```text
This is not a new QPU result.
This is not a quantum-specific promotion.
This only shows that the audit formats now line up.
```

## Recommended next experiment

```text
contextual_membrane_quantum_anchor_probe_v3_finite_shot_stress
```

Core rule:

```text
Inject finite-shot sampling into the explicit witness tables.
Vary shots from low to hardware-like regimes.
Compare survival probability against PM/KCBS margins.
Add adversarial no-disturbance drift.
Require witness survival without relying on exact expected tables.
```

## Claim boundary

The current results are contextual/classical component results plus witness-shaped audit-bridge and hardware-format compatibility results.

They do not establish quantum-specific behavior, formal measurement contextuality of a physical implementation, life, metabolism, self-repair, consciousness, or physical matter synthesis.
