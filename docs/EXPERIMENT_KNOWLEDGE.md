# Experiment Knowledge Base

Updated: 2026-07-08

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
quantum_homeostatic_parts_observation_v1_pulse_map = OBSERVATION_LOG
quantum_homeostatic_parts_observation_v2_causal_touch_response = OBSERVATION_LOG
```

## quantum_homeostatic_parts_observation_v0 knowledge

```text
direct_entangling_parts neg_M_C_max = 0.126998385
direct_entangling_parts neg_C_R_max = 0.095496553
direct_entangling_parts neg_R_W_max = 0.043610747

field_only_parts neg_M_C_max = 0
field_only_parts neg_C_R_max = 0
field_only_parts neg_R_W_max = 0
```

## quantum_homeostatic_parts_observation_v1_pulse_map knowledge

```text
spatial attenuation = which pair is stronger
temporal propagation = when each pair peaks

left_to_right_wave peak lags = +24, +18
simultaneous_burst peak lags = +1, -1
right_to_left_wave peak lags = -17, -26
```

## quantum_homeostatic_parts_observation_v2_causal_touch_response knowledge

### What was added

v2 stops relying on pre-shaped field waves and touches one part locally.

Modes:

```text
local_touch_direct
field_only_local_touch
global_field_pulse
```

Regimes:

```text
fixed_field
slow_field
```

### Fixed-field observations

```text
Touch M:
  M-C peak t/value = 35 / 0.0811
  C-R peak t/value = 48 / 0.0346
  R-W peak t/value = 61 / 0.0135

Touch C:
  M-C peak t/value = 35 / 0.0811
  C-R peak t/value = 35 / 0.0665
  R-W peak t/value = 48 / 0.0271

Touch R:
  C-R peak t/value = 35 / 0.0665
  R-W peak t/value = 35 / 0.0519
  M-C peak t/value = 48 / 0.0422

Touch W:
  R-W peak t/value = 35 / 0.0519
  C-R peak t/value = 48 / 0.0346
  M-C peak t/value = 61 / 0.0211
```

### Controls

```text
field_only_local_touch:
  activation can move, but M-C / C-R / R-W negativity stays zero

global_field_pulse:
  M-C / C-R / R-W all peak at t=39
```

### Interpretation

```text
Touch an edge part: response moves inward along the chain.
Touch a middle part: both neighboring links light first, then the farther link follows.
Move the whole field: all links light together.
Remove direct links: activations can move, but pair negativity does not appear.
```

## Next experiment option

```text
quantum_homeostatic_parts_observation_v3_recovery_cycle
```

Required improvements:

```text
touch a part repeatedly
let the system recover between touches
watch whether the negativity response adapts, saturates, or habituates
compare recovery under high-energy and high-toxicity conditions
```
