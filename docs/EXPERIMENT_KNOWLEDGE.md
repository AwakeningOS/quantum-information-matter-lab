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
Can that change depend on memory, unchosen alternatives, and context order?
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

Do not claim v1 isolates counterfactual residue alone or pure order effects alone.

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

Do not claim v2 isolates pure order effects alone.

## contextual_membrane_v3_order_effect knowledge

### What was tested

The same `(context, object, u)` event multiset under order-only permutations:

```text
original_order
reverse_order
block_shuffle_order
compatible_cluster_order
random_order_same_multiset
context_sorted_order
```

All variants preserved the event multiset.

### Result snapshot

```text
Verdict = PASS_ORDER_EFFECT

original_order final_cumulative_release = 145.156796757
reverse_order final_cumulative_release = 132.740948410
random_order_same_multiset final_cumulative_release = 115.454200271
context_sorted_order final_cumulative_release = 293.695236578

reverse_order event_match_to_original = 0.535714286
block_shuffle_order event_match_to_original = 0.593750000
compatible_cluster_order event_match_to_original = 0.526785714
random_order_same_multiset event_match_to_original = 0.540178571
context_sorted_order event_match_to_original = 0.582589286

reverse_order final_residue_l1_to_original = 1.395097921
block_shuffle_order final_residue_l1_to_original = 1.042309054
compatible_cluster_order final_residue_l1_to_original = 1.092896097
random_order_same_multiset final_residue_l1_to_original = 0.856036973
context_sorted_order final_residue_l1_to_original = 2.306517995
```

### Lesson

v3 supports the component-level claim that order alone can alter the implemented membrane's event timing, downstream release trajectory, final membrane state, and residue distribution.

The effect is not explained by object frequency or context frequency, because the event multiset is preserved.

### Do not claim

```text
Do not claim v3 demonstrates quantum-specific behavior.
Do not claim v3 demonstrates formal measurement contextuality.
Do not claim v3 demonstrates biological organization or consciousness.
Do not claim v3 isolates joint/non-additive object-context boundary effects.
```

## Next experiment: contextual_membrane_v4_joint_boundary

The next experiment should isolate full joint boundary effects.

Use variants such as:

```text
full_joint_boundary
object_only_replay
context_only_replay
additive_object_context_model
pairwise_replay
joint_shuffle_control
```

Primary success should require the full joint boundary to reproduce membrane decisions while object-only, context-only, additive, or pairwise controls fail.
