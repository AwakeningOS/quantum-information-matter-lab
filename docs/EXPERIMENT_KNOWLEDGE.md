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
reproducibility check or documented observation output
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
quantum_homeostatic_parts_observation_v0 = OBSERVATION_LOG
```

## Core component lesson

```text
A contextual membrane can control the flow of a downstream reaction field in this designed component.
This result survived multi-seed, matched pass-rate, matched signal, additive-boundary, and strong no-membrane controls.
```

## quantum_homeostatic_parts_observation_v0 knowledge

### What was built

A 4-qubit density-matrix observation model:

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

and direct field-modulated entangling links:

```text
M-C
C-R
R-W
```

plus a weak M-W phase thread.

### Variants

```text
direct_entangling_parts
field_only_parts
constant_entangling_parts
```

### Result snapshot

```text
direct_entangling_parts neg_M_C_max = 0.126998385
direct_entangling_parts neg_C_R_max = 0.095496553
direct_entangling_parts neg_R_W_max = 0.043610747

field_only_parts neg_M_C_max = 0
field_only_parts neg_C_R_max = 0
field_only_parts neg_R_W_max = 0

constant_entangling_parts neg_M_C_max = 0.216683639
constant_entangling_parts neg_C_R_max = 0.021194988
constant_entangling_parts neg_R_W_max = 0.058936607
```

### Interpretation

```text
The field-only model can coordinate local part activations through a shared classical field, but it does not create pair negativity.
The direct-entangling model creates actual pair-negativity pulses along M-C / C-R / R-W.
The constant-entangling model shows a different pulse shape, separating fixed quantum threading from whole-field-modulated threading.
```

### Important shape

```text
Toxicity and pressure increase coupling strengths, but they also increase dephasing.
Visible negativity is therefore a pulse left by coupling and dissipation pulling against each other.
In this run, negativity tracked energy windows more clearly than raw toxicity/pressure load.
```

## Next experiment option

```text
quantum_homeostatic_parts_observation_v1_pulse_map
```

Required improvements:

```text
sweep pulse shapes and coupling strengths
output a compact raster of negativity pulses
track whether pulses move from M-C to C-R to R-W as toxicity/pressure waves travel through the system
save pulse onset, peak, decay, and field values together
```
