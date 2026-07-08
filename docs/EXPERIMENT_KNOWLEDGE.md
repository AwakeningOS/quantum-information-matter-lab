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

## Paper A inheritance

Useful design lesson:

```text
Quantum structure did not survive as ordinary downstream transport.
It survived at the measurement-context boundary.
```

Therefore, build components whose interfaces depend on:

```text
question structure
compatibility / incompatibility
context history
observed outputs
unobserved alternatives
self-reading state
```

## Research positioning: witness to decision boundary

The intended next line of research is not merely:

```text
use contextuality as a witness
```

The intended line is:

```text
put contextuality/context structure into the membrane decision boundary
```

The practical question is:

```text
Can contextuality change a membrane decision?
Can that change depend on memory, unchosen alternatives, context order, joint boundaries, and downstream propagation?
```

Staged program:

```text
v0 = context-looking membrane
v1 = memory-bearing boundary
v2 = counterfactual-residue boundary
v3 = order-sensitive boundary
v4 = joint/non-additive boundary
reactor = downstream propagation
quantum anchor = connection to real contextuality witness
```

## contextual_membrane_v0 knowledge

The component-level contextual behavior passed the v0 criteria, but memory necessity was not established.

```text
full_contextual object_conditioned_context_score_range_mean = 0.333906636
full_contextual compatibility_score_gap = 0.285508247
context_no_memory event_match_to_full = 0.984375
context_no_memory score_mae_to_full = 0.008596154
```

## contextual_membrane_v1_memory_ablation knowledge

v1 supports the component-level claim that dynamic memory changes membrane decisions and downstream quality/release trajectory.

```text
Verdict = PASS_MEMORY_DEPENDENT_BOUNDARY
full pass_rate = 0.633928571
no_memory pass_rate = 0.455357143
full final_cumulative_release = 153.963406058
no_memory final_cumulative_release = 52.369918094
no_memory event_match_to_full = 0.8125
no_memory score_mae_to_full = 0.199107556
no_memory release_mae_to_full = 0.21448549
```

## contextual_membrane_v2_counterfactual_residue knowledge

v2 supports the component-level claim that later membrane decisions depend on residue from unchosen alternatives.

```text
Verdict = PASS_COUNTERFACTUAL_RESIDUE
full pass_rate = 0.479910714
observed_only pass_rate = 0.531250000
full final_cumulative_release = 52.388208985
observed_only final_cumulative_release = 75.770977236
observed_only event_match_to_full = 0.814732143
observed_only score_mae_to_full = 0.164462842
observed_only release_mae_to_full = 0.074669816
full counterfactual_polarity_probe = 0.170622487
counterfactual_sign_flip counterfactual_polarity_probe = -0.407708026
counterfactual_shuffle counterfactual_polarity_probe = -0.216989363
```

The key directional result:

```text
previous BLOCK leaves unchosen PASS residue, which raises later score relative to observed_only.
previous PASS leaves unchosen BLOCK residue, which lowers later score relative to observed_only.
```

## contextual_membrane_v3_order_effect knowledge

v3 supports the component-level claim that order alone can alter event timing, downstream release trajectory, final membrane state, and residue distribution.

```text
Verdict = PASS_ORDER_EFFECT
original_order final_cumulative_release = 145.156796757
reverse_order final_cumulative_release = 132.740948410
random_order_same_multiset final_cumulative_release = 115.454200271
context_sorted_order final_cumulative_release = 293.695236578
reverse_order event_match_to_original = 0.535714286
random_order_same_multiset event_match_to_original = 0.540178571
context_sorted_order final_residue_l1_to_original = 2.306517995
```

The effect is not explained by object frequency or context frequency, because the event multiset is preserved.

## contextual_membrane_v4_joint_boundary knowledge

v4 supports the component-level claim that the implemented membrane decisions require full object/context joint state under the tested controls.

```text
Verdict = PASS_JOINT_BOUNDARY
full_joint_boundary final_cumulative_release = 103.696477783
object_only_replay final_cumulative_release = 17.522951078
context_only_replay final_cumulative_release = 12.540111148
additive_object_context_model final_cumulative_release = 13.964177586
static_pairwise_replay final_cumulative_release = 36.327646821
joint_shuffle_control final_cumulative_release = 41.956207828
object_only_replay event_match_to_full = 0.685267857
context_only_replay event_match_to_full = 0.609375000
additive_object_context_model event_match_to_full = 0.665178571
static_pairwise_replay event_match_to_full = 0.805803571
joint_shuffle_control event_match_to_full = 0.714285714
additive_object_context_model score_mae_to_full = 0.306924220
static_pairwise_replay release_mae_to_full = 0.139480465
```

The important distinction:

```text
object alone is not enough
context alone is not enough
object + context as additive factors is not enough
static pair identity is not enough
wrong joint key is not enough
```

## contextual_reactor_v0_membrane_to_flow knowledge

### What was tested

A downstream reactor driven by membrane outputs:

```text
full_membrane_to_reactor
no_memory_membrane_to_reactor
no_counterfactual_membrane_to_reactor
order_scrambled_membrane_to_reactor
additive_boundary_membrane_to_reactor
reactor_without_membrane
```

### Result snapshot

```text
Verdict = PASS_MEMBRANE_TO_FLOW_PROPAGATION

full_membrane_to_reactor final_persistence = 5.769240129
no_memory_membrane_to_reactor final_persistence = 1.090516857
no_counterfactual_membrane_to_reactor final_persistence = 3.376836905
order_scrambled_membrane_to_reactor final_persistence = 2.944674958
additive_boundary_membrane_to_reactor final_persistence = 0.784523923
reactor_without_membrane final_persistence = 0.894988371

full_membrane_to_reactor final_cumulative_release = 38.849451729
no_memory_membrane_to_reactor final_cumulative_release = 8.940490852
no_counterfactual_membrane_to_reactor final_cumulative_release = 31.869441381
order_scrambled_membrane_to_reactor final_cumulative_release = 30.472556495
additive_boundary_membrane_to_reactor final_cumulative_release = 2.583046640
reactor_without_membrane final_cumulative_release = 10.431454452
```

### Lesson

reactor v0 supports the component-level claim that the implemented membrane structure propagates into downstream release, quality, reservoir, and persistence under the tested controls.

The important distinction:

```text
memory removal weakens downstream release
counterfactual-residue removal changes downstream release and persistence
order scrambling changes the final reactor state
additive boundary replacement strongly suppresses release
removing membrane coupling changes the reactor trajectory
```

### Do not claim

```text
Do not claim reactor v0 demonstrates quantum-specific behavior.
Do not claim reactor v0 demonstrates formal measurement contextuality.
Do not claim reactor v0 demonstrates biological organization or consciousness.
Do not claim reactor v0 demonstrates matter synthesis.
```

## Next experiment options

Two possible routes:

```text
contextual_reactor_v1_flow_controls
contextual_membrane_quantum_anchor_probe
```

Recommended order if hardening the component line:

```text
contextual_reactor_v1_flow_controls first
quantum anchor later and separately
```
