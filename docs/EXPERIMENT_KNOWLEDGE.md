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
reproducibility check
```

## Research positioning

The intended line is:

```text
put contextuality/context structure into the component decision boundary
```

Staged program:

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

## contextual_membrane_v0 knowledge

```text
Verdict = PASS_COMPONENT_BEHAVIOR
full_contextual object_conditioned_context_score_range_mean = 0.333906636
full_contextual compatibility_score_gap = 0.285508247
context_no_memory event_match_to_full = 0.984375
```

Lesson:

```text
The membrane decision can depend on context/question structure.
Memory necessity was not established in v0.
```

## contextual_membrane_v1_memory_ablation knowledge

```text
Verdict = PASS_MEMORY_DEPENDENT_BOUNDARY
full pass_rate = 0.633928571
no_memory pass_rate = 0.455357143
full final_cumulative_release = 153.963406058
no_memory final_cumulative_release = 52.369918094
no_memory event_match_to_full = 0.8125
```

Lesson:

```text
Dynamic memory changes membrane decisions and downstream quality/release trajectory.
```

## contextual_membrane_v2_counterfactual_residue knowledge

```text
Verdict = PASS_COUNTERFACTUAL_RESIDUE
full counterfactual_polarity_probe = 0.170622487
counterfactual_sign_flip counterfactual_polarity_probe = -0.407708026
counterfactual_shuffle counterfactual_polarity_probe = -0.216989363
```

Lesson:

```text
Unchosen alternatives leave directional residue that changes later membrane decisions.
```

## contextual_membrane_v3_order_effect knowledge

```text
Verdict = PASS_ORDER_EFFECT
original_order final_cumulative_release = 145.156796757
random_order_same_multiset final_cumulative_release = 115.454200271
context_sorted_order final_cumulative_release = 293.695236578
```

Lesson:

```text
Order alone can alter event timing, downstream release trajectory, final membrane state, and residue distribution.
```

## contextual_membrane_v4_joint_boundary knowledge

```text
Verdict = PASS_JOINT_BOUNDARY
full_joint_boundary final_cumulative_release = 103.696477783
object_only_replay final_cumulative_release = 17.522951078
context_only_replay final_cumulative_release = 12.540111148
additive_object_context_model final_cumulative_release = 13.964177586
static_pairwise_replay final_cumulative_release = 36.327646821
joint_shuffle_control final_cumulative_release = 41.956207828
```

Lesson:

```text
object alone is not enough
context alone is not enough
object + context as additive factors is not enough
static pair identity is not enough
wrong joint key is not enough
```

## contextual_reactor_v0_membrane_to_flow knowledge

```text
Verdict = PASS_MEMBRANE_TO_FLOW_PROPAGATION
full_membrane_to_reactor final_persistence = 5.769240129
reactor_without_membrane final_persistence = 0.894988371
full_membrane_to_reactor final_cumulative_release = 38.849451729
reactor_without_membrane final_cumulative_release = 10.431454452
```

Lesson:

```text
The implemented membrane structure propagates into downstream release, quality, reservoir, and persistence under the tested controls.
```

## contextual_reactor_v1_flow_controls knowledge

### What was tested

Hardened propagation controls:

```text
full_membrane_to_reactor
no_memory_membrane_to_reactor
no_counterfactual_membrane_to_reactor
matched_pass_rate_random_membrane
matched_signal_shuffle_replay
matched_signal_lag_replay
additive_boundary_membrane_to_reactor
strong_reactor_without_membrane
```

Multi-seed panel:

```text
20260708
20260709
20260710
20260711
20260712
```

### Result snapshot

```text
Verdict = PASS_HARDENED_MEMBRANE_TO_FLOW_CONTROLS

full_membrane_to_reactor final_quality_mean = 1.308064781
full_membrane_to_reactor final_persistence_mean = 20.400910610
full_membrane_to_reactor final_cumulative_release_mean = 100.992143180

matched_pass_rate_random_membrane final_persistence_mean = 5.114475169
matched_signal_shuffle_replay final_persistence_mean = 9.438825659
matched_signal_lag_replay final_persistence_mean = 11.981202902
strong_reactor_without_membrane final_persistence_mean = 10.167187854

matched_pass_rate_random_membrane final_cumulative_release_mean = 45.316304998
matched_signal_shuffle_replay final_cumulative_release_mean = 76.914353974
matched_signal_lag_replay final_cumulative_release_mean = 79.115226502
strong_reactor_without_membrane final_cumulative_release_mean = 52.936920966
```

### Win counts

```text
full wins final quality against every control in all 5 seeds
full wins final persistence against every control in all 5 seeds
full wins final cumulative release against every control in all 5 seeds
```

### Lesson

reactor v1 supports the component-level claim that membrane-to-flow propagation is not reducible to:

```text
same pass rate
same signal distribution
lagged signal replay
additive object/context boundary
stronger reactor dynamics without membrane state
```

This hardens the classical component claim:

```text
A contextual membrane can control the flow of a downstream reaction field in this designed component.
```

### Do not claim

```text
Do not claim reactor v1 demonstrates quantum-specific behavior.
Do not claim reactor v1 demonstrates formal measurement contextuality.
Do not claim reactor v1 demonstrates biological organization or consciousness.
Do not claim reactor v1 demonstrates matter synthesis.
```

## Next experiment option

```text
contextual_membrane_quantum_anchor_probe
```

Keep this separate from the component propagation claim. Treat it as an audit bridge to PM/KCBS-like witness logic, not as a continuation of the classical component result.
