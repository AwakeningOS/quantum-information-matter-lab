# Agent Handoff

Updated: 2026-07-08

## Repository role

This repository is a clean lab for contextual information-matter components.

The operating rule remains:

```text
No code + no raw log = no result.
```

## Research positioning

The user's intended research direction is not merely to run contextuality as an external witness.

The target line is:

```text
put contextuality into the component decision boundary
```

More precisely, the intended question is:

```text
Does contextuality change a membrane decision?
Does that change depend on memory, unchosen alternatives, context order, joint boundaries, and downstream propagation?
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
quantum anchor = connection to real contextuality witness
```

## Completed experiments

### contextual_membrane_v0

```text
Verdict: PASS_COMPONENT_BEHAVIOR
Layer: CONTEXTUAL_COMPONENT
```

Main lesson:

```text
The membrane decision can depend on context/question structure.
Memory necessity was not established in v0.
```

### contextual_membrane_v1_memory_ablation

```text
Verdict: PASS_MEMORY_DEPENDENT_BOUNDARY
Layer: CONTEXTUAL_COMPONENT
```

Main lesson:

```text
Dynamic memory changes membrane decisions and downstream quality/release trajectory under the tested ablations.
```

### contextual_membrane_v2_counterfactual_residue

```text
Verdict: PASS_COUNTERFACTUAL_RESIDUE
Layer: CONTEXTUAL_COMPONENT
```

Main lesson:

```text
Later membrane decisions depend on unchosen-alternative residue under the tested ablations.
```

### contextual_membrane_v3_order_effect

```text
Verdict: PASS_ORDER_EFFECT
Layer: CONTEXTUAL_COMPONENT
```

Main lesson:

```text
The same context/object/u event multiset produces different membrane trajectories when order is changed.
```

### contextual_membrane_v4_joint_boundary

```text
Verdict: PASS_JOINT_BOUNDARY
Layer: CONTEXTUAL_COMPONENT
```

Main lesson:

```text
The implemented membrane decisions require full object/context joint state under the tested controls.
```

### contextual_reactor_v0_membrane_to_flow

```text
Verdict: PASS_MEMBRANE_TO_FLOW_PROPAGATION
Layer: CLASSICAL_COMPONENT
```

Main lesson:

```text
The membrane structure propagates into downstream reactor release, quality, reservoir, and persistence under the tested controls.
```

### contextual_reactor_v1_flow_controls

```text
Verdict: PASS_HARDENED_MEMBRANE_TO_FLOW_CONTROLS
Layer: CLASSICAL_COMPONENT
Seeds: 20260708, 20260709, 20260710, 20260711, 20260712
```

Main lesson:

```text
The membrane-to-flow result survives stronger classical controls.
Full wins final quality, final persistence, and final cumulative release against every control in all 5 seeds.
```

Key aggregate comparison:

```text
full_membrane_to_reactor final_persistence_mean = 20.400910610
matched_pass_rate_random_membrane final_persistence_mean = 5.114475169
matched_signal_shuffle_replay final_persistence_mean = 9.438825659
matched_signal_lag_replay final_persistence_mean = 11.981202902
strong_reactor_without_membrane final_persistence_mean = 10.167187854

full_membrane_to_reactor final_cumulative_release_mean = 100.992143180
matched_pass_rate_random_membrane final_cumulative_release_mean = 45.316304998
matched_signal_shuffle_replay final_cumulative_release_mean = 76.914353974
matched_signal_lag_replay final_cumulative_release_mean = 79.115226502
strong_reactor_without_membrane final_cumulative_release_mean = 52.936920966
```

Control lesson:

```text
same pass rate is not enough
same signal distribution is not enough
lagged signal replay is not enough
additive object/context boundary is not enough
strong non-contextual reactor dynamics are not enough
```

## Recommended next experiment

```text
contextual_membrane_quantum_anchor_probe
```

Core rule:

```text
Keep the quantum-anchor probe separate from the component propagation claim.
Use PM/KCBS-like witness logic only as a separate audit bridge.
Do not promote quantum-specific claims unless witness-level controls pass.
```

## Claim boundary

The current results are contextual/classical component results only.

They do not establish quantum-specific behavior, formal measurement contextuality, life, metabolism, self-repair, consciousness, or physical matter synthesis.
