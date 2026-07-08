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
Does that change depend on memory, unchosen alternatives, context order, and joint boundaries?
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

### contextual_membrane_v4_joint_boundary

```text
Verdict: PASS_JOINT_BOUNDARY
Layer: CONTEXTUAL_COMPONENT
```

Main lesson:

```text
The implemented membrane's decisions require full object/context joint state under the tested controls.
Object-only, context-only, additive object+context, static pairwise, and joint-shuffle controls fail to reproduce the full membrane.
```

Key v4 comparison:

```text
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
```

## Recommended next experiment

```text
contextual_reactor_v0_membrane_to_flow
```

Core idea:

```text
connect membrane PASS/BLOCK outputs to a downstream reactor
measure release, quality, reservoir, and persistence
test whether membrane structure changes downstream flow without making quantum-specific claims
```

## Claim boundary

The current results are contextual component results only.

They do not establish quantum-specific behavior, formal measurement contextuality, life, metabolism, self-repair, consciousness, or physical matter synthesis.
