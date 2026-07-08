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
quantum_boundary_homeostasis_v0_internal_feedback = OBSERVATION_LOG
```

## quantum homeostatic parts line

```text
v0: direct entangling creates M-C / C-R / R-W pair-negativity pulses; field-only keeps pair negativity at zero.
v1: spatial attenuation and temporal propagation are separated by peak/onset lags.
v2: local touch response spreads through neighboring links; global field pulse lights all links together.
v3: repeated touch exposes cross-touch state variables: coherence, bias, baseline negativity, fatigue.
v4: recovery strength separates stable repair, damped oscillation, overdrive, and exhausted repair through predeclared mechanical labels.
```

## quantum_boundary_homeostasis_v0_internal_feedback knowledge

### What was added

A new inside/outside boundary line.

Main rule:

```text
boundary behavior is driven by internal negative feedback, not external toxicity alone
```

Balance metric:

```text
homeostasis_balance = target_range_fraction * resource_intake_fraction * efficiency_factor
```

### Key observations

```text
coherent_internal_feedback:
  target_range_fraction = 0.843750000
  resource_intake_fraction = 0.695312500
  homeostasis_balance = 0.487672421
  internal_state_sensitivity = 0.362000000
  fatigue_final = 0.084000000
  bias_final = 0.032000000

measurement_internal_feedback:
  target_range_fraction = 0.859375000
  resource_intake_fraction = 0.546875000
  homeostasis_balance = 0.364177221
  fatigue_final = 0.336000000
  bias_final = 0.246000000

external_reactive_boundary:
  target_range_fraction = 0.671875000
  internal_state_sensitivity = 0.052000000
  homeostasis_balance = 0.339046807

open_boundary:
  target_range_fraction = 0.382812500
  resource_intake_fraction = 0.953125000
  homeostasis_balance = 0.343243804

overclosed_boundary:
  target_range_fraction = 0.914062500
  resource_intake_fraction = 0.101562500
  unnecessary_closure_rate = 0.742187500
  homeostasis_balance = 0.085640657

wrong_target_boundary:
  target_range_fraction = 0.453125000
  resource_intake_fraction = 0.765625000
  homeostasis_balance = 0.285064772
```

### Interpretation

```text
Coherent internal feedback best balances protection, exchange, and efficiency.
Measurement internal feedback protects, but leaves higher bias/fatigue and lowers intake.
External reactive boundary behaves more like an external mirror than a self-boundary.
Open boundary exchanges but does not protect.
Overclosed boundary protects but starves exchange.
Wrong target boundary regulates around the wrong internal range.
```

### Quantum-coupled response trace

```text
coherent_internal_feedback:
  M-C peak time/value = 42 / 0.044800000000
  C-R peak time/value = 55 / 0.028700000000
  R-W peak time/value = 69 / 0.017900000000
  lags = +13, +14

measurement_internal_feedback:
  M-C peak time/value = 43 / 0.026600000000
  C-R peak time/value = 57 / 0.014400000000
  R-W peak time/value = 71 / 0.007200000000
  lags = +14, +14
```

## Next experiment option

```text
quantum_boundary_homeostasis_v1_adaptive_boundary_controller
```

Required improvements:

```text
let the boundary tune feedback gain from internal error, fatigue, and resource deficit
compare fixed internal feedback against adaptive internal feedback
watch whether adaptive feedback keeps balance high under changing stress without drifting into closure or exhaustion
```
