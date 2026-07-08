# Agent Handoff

Updated: 2026-07-08

## Repository role

This repository is a clean lab for contextual information-matter components and quantum-coupled observation models.

The operating rule remains:

```text
No code + no raw log = no result.
```

## Research positioning

The contextual component line is:

```text
put contextuality into the component decision boundary
```

The new observation line is:

```text
watch several quantum-coupled parts immersed in one whole-field
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
quantum_homeostatic_parts_observation_v0 = OBSERVATION_LOG
```

## quantum_homeostatic_parts_observation_v0 lesson

The model uses a 4-qubit density matrix:

```text
M = membrane
C = conversion / catalyst
R = recycler
W = waste outlet
```

with a shared whole-field:

```text
energy
toxicity
pressure
```

The direct observation variant adds field-modulated partial-iSWAP gates:

```text
M-C
C-R
R-W
```

plus a weak M-W phase thread.

Key observation:

```text
direct_entangling_parts neg_M_C_max = 0.126998385
direct_entangling_parts neg_C_R_max = 0.095496553
direct_entangling_parts neg_R_W_max = 0.043610747

field_only_parts neg_M_C_max = 0
field_only_parts neg_C_R_max = 0
field_only_parts neg_R_W_max = 0
```

Reading:

```text
The field-only model can make parts move together, but it does not create pair negativity.
The direct-entangling model produces actual pair-negativity pulses along M-C / C-R / R-W.
```

Important shape:

```text
Toxicity and pressure increase coupling strengths, but they also increase dephasing.
Visible negativity pulses are therefore a tug-of-war between coupling and dissipation.
In this run, pair negativity correlated more strongly with energy windows than with toxicity/pressure load.
```

## Recommended next experiment

```text
quantum_homeostatic_parts_observation_v1_pulse_map
```

Core rule:

```text
Keep the 4-qubit density matrix.
Sweep pulse shapes and coupling strengths.
Output a compact raster of negativity pulses.
Track whether pulses move from M-C to C-R to R-W as toxicity/pressure waves travel through the system.
```

## Claim boundary

The current quantum-homeostatic result is an observation log.

It records trajectories; it does not try to prove advantage or promote a hardware claim.
