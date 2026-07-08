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

Interpretation:

```text
The field-only model can coordinate local part activations through a shared classical field, but it does not create pair negativity.
The direct-entangling model creates pair-negativity pulses along M-C / C-R / R-W.
```

## quantum_homeostatic_parts_observation_v1_pulse_map knowledge

### What was added

v1 separates:

```text
spatial attenuation = which pair is stronger
temporal propagation = when each pair peaks
```

Metrics stored per pair:

```text
peak time
peak value
onset time
offset time
duration above threshold
pair-to-pair peak lag
pair-to-pair onset lag
compact negativity raster
```

### Medium-scale observations

```text
left_to_right_wave:
  M-C peak t/value = 32 / 0.069180405344
  C-R peak t/value = 56 / 0.031486878512
  R-W peak t/value = 74 / 0.025019349203
  peak lags = +24, +18
  label = left_to_right_peak_travel

simultaneous_burst:
  M-C peak t/value = 54 / 0.065525157382
  C-R peak t/value = 55 / 0.047518386948
  R-W peak t/value = 54 / 0.031339737403
  peak lags = +1, -1
  label = near_simultaneous_peaks

right_to_left_wave:
  M-C peak t/value = 75 / 0.079669134216
  C-R peak t/value = 58 / 0.048731564142
  R-W peak t/value = 32 / 0.016744293428
  peak lags = -17, -26
  label = right_to_left_peak_travel

double_pulse_wave:
  M-C peak t/value = 29 / 0.071762802615
  C-R peak t/value = 52 / 0.030278827516
  R-W peak t/value = 70 / 0.026050997304
  peak lags = +23, +18
  label = left_to_right_peak_travel
```

### Interpretation

```text
Left-to-right input produces delayed M-C -> C-R -> R-W peaks.
Simultaneous input produces near-simultaneous peaks.
Right-to-left input reverses the lag sign.
Field-only keeps pair negativity at zero.
```

This means the v0 max-negativity summary was incomplete. It showed spatial attenuation, but v1 shows whether that attenuation is accompanied by temporal propagation.

## Next experiment option

```text
quantum_homeostatic_parts_observation_v2_causal_touch_response
```

Required improvements:

```text
perturb one part locally while the whole-field is held fixed or slowly varying
watch whether activation and pair negativity spread through neighboring links
compare local-touch response against global-field-only drive
```
