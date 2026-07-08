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
quantum_homeostatic_parts_observation_v3_recovery_cycle = OBSERVATION_LOG
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

```text
Touch M: M-C -> C-R -> weak R-W tail
Touch C: M-C and C-R first, then R-W
Touch R: C-R and R-W first, then M-C
Touch W: R-W -> C-R -> weak M-C tail
Field-only local touch: pair negativity stays zero
Global field pulse: all links peak together
```

## quantum_homeostatic_parts_observation_v3_recovery_cycle knowledge

### What was added

v3 introduces repeated touches and records cross-touch state variables:

```text
pre_coherence_residual
pre_population_bias
pre_baseline_negativity
pre_fatigue_index
```

Recovery modes:

```text
passive_recovery
active_recovery
full_reset_baseline
```

Touch types:

```text
unitary_touch
measurement_touch
```

Conditions:

```text
high_energy
high_toxicity
```

### Key ratios

```text
high_energy + full_reset + unitary: last/first = 1.000000000
high_energy + full_reset + measurement: last/first = 1.000000000
high_energy + active_recovery + unitary: last/first = 0.882453216
high_energy + active_recovery + measurement: last/first = 0.728685139
high_energy + passive_recovery + measurement: last/first = 0.126848576

high_toxicity + full_reset + unitary: last/first = 1.000000000
high_toxicity + full_reset + measurement: last/first = 1.000000000
high_toxicity + active_recovery + unitary: last/first = 0.683273682
high_toxicity + active_recovery + measurement: last/first = 0.403944250
high_toxicity + passive_recovery + measurement: last/first = 0.000000000
```

### State traces

```text
high_energy active unitary:
  coherence 0.860000000 -> 0.774896250
  fatigue 0.020000000 -> 0.060639219

high_energy active measurement:
  population bias 0.020000000 -> 0.085963248
  fatigue 0.020000000 -> 0.125592500

high_toxicity passive measurement:
  coherence 0.700000000 -> 0.000000000
  population bias 0.020000000 -> 0.639302544
  fatigue 0.020000000 -> 0.645545760
```

### Interpretation

```text
Full reset removes cross-touch memory and keeps response stable.
Active recovery under high energy mostly preserves unitary-touch response.
Measurement touch leaves more population bias and fatigue than unitary touch.
High toxicity makes recovery harder and turns repeated measurement into strong response decay.
```

## Next experiment option

```text
quantum_homeostatic_parts_observation_v4_repair_vs_overdrive
```

Required improvements:

```text
test whether too-strong active recovery becomes overdrive
compare gentle recovery, strong recovery, and oscillatory recovery
watch whether repeated touches produce stable adaptation or runaway rebound
```
