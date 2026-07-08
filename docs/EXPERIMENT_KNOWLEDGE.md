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
quantum_homeostatic_parts_observation_v4_repair_vs_overdrive = OBSERVATION_LOG
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

```text
Full reset removes cross-touch memory and keeps response stable.
Active recovery under high energy mostly preserves unitary-touch response.
Measurement touch leaves more population bias and fatigue than unitary touch.
High toxicity makes recovery harder and turns repeated measurement into strong response decay.
```

## quantum_homeostatic_parts_observation_v4_repair_vs_overdrive knowledge

### What was added

v4 defines repair/overdrive labels before running the observation:

```text
stable_repair
damped_oscillatory_repair
overdrive
collapse_or_exhausted_repair
```

Metrics:

```text
response_ratio_last_over_first
overshoot_max
state_distance_last
oscillation_envelope_ratio
bias_last
fatigue_last
```

### Key observations

```text
high_energy + gentle + unitary:
  response ratio = 0.954003707
  state_distance_last = 0.0758656072
  label = stable_repair

high_energy + strong + unitary:
  response ratio = 1.035908941
  overshoot_max = 0.174949411
  oscillation_envelope_ratio = 0.331310936
  label = damped_oscillatory_repair

high_energy + oscillatory + unitary:
  response ratio = 1.081767736
  overshoot_max = 0.257713327
  oscillation_envelope_ratio = 0.534286226
  label = damped_oscillatory_repair

high_energy + extreme + unitary:
  state_distance_last = 1.0698560591
  oscillation_envelope_ratio = 5.290555134
  bias_last = 0.424455566
  fatigue_last = 0.648256006
  label = overdrive

high_toxicity + weak + measurement:
  response ratio = 0.000000000
  coherence_last = 0.000000000
  fatigue_last = 0.835481525
  label = collapse_or_exhausted_repair

high_toxicity + oscillatory + unitary:
  response ratio = 1.312665687
  overshoot_max = 0.316634425
  oscillation_envelope_ratio = 1.357167475
  label = overdrive
```

### Interpretation

```text
Gentle recovery can repair without overshoot.
Strong/oscillatory recovery can ring and then settle when the envelope decays.
Extreme recovery or toxic oscillatory recovery becomes overdrive when state-distance or envelope grows.
Weak recovery under toxic measurement can collapse into exhausted repair.
```

## Next experiment option

```text
quantum_homeostatic_parts_observation_v5_adaptive_recovery_controller
```

Required improvements:

```text
let recovery gain depend on state-distance and fatigue
compare fixed recovery against adaptive recovery
watch whether adaptive recovery avoids both exhaustion and overdrive
```
