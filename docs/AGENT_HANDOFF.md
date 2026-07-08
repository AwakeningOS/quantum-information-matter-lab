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
Does that change depend on memory, unchosen alternatives, and context order?
```

Short form:

```text
v0 = context-looking membrane
v1 = memory-bearing boundary
v2 = counterfactual-residue boundary
v3 = order-sensitive boundary
v4 = joint/non-additive boundary
reactor = downstream propagation
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
The implemented membrane is not merely context-looking.
Under the tested ablations, dynamic memory changes membrane decisions and downstream quality/release trajectory.
```

### contextual_membrane_v2_counterfactual_residue

```text
Verdict: PASS_COUNTERFACTUAL_RESIDUE
Layer: CONTEXTUAL_COMPONENT
```

Main lesson:

```text
The implemented membrane's later decisions depend on unchosen-alternative residue under the tested ablations.
```

Counterfactual polarity:

```text
full counterfactual_polarity_probe = 0.170622487
counterfactual_sign_flip counterfactual_polarity_probe = -0.407708026
counterfactual_shuffle counterfactual_polarity_probe = -0.216989363
```

### contextual_membrane_v3_order_effect

```text
Verdict: PASS_ORDER_EFFECT
Layer: CONTEXTUAL_COMPONENT
```

Main lesson:

```text
The same context/object/u event multiset produces different membrane trajectories when order is changed.
Order alone changes event timing, downstream release, final membrane state, and residue distribution in the implemented component.
```

Key order comparison:

```text
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

## Recommended next experiment

```text
contextual_membrane_v4_joint_boundary
```

Core idea:

```text
compare object-only replay
compare context-only replay
compare additive object+context model
compare pairwise replay
require full joint boundary to reproduce membrane decisions
```

## Claim boundary

The current results are contextual component results only.

They do not establish quantum-specific behavior, formal measurement contextuality, life, metabolism, self-repair, consciousness, or physical matter synthesis.
