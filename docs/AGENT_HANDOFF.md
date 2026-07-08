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

Important v0 metrics:

```text
full_contextual object_conditioned_context_score_range_mean = 0.333906636
full_contextual compatibility_score_gap = 0.285508247
context_no_memory event_match_to_full = 0.984375
context_no_memory score_mae_to_full = 0.008596154
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

Key full vs no_memory comparison:

```text
full pass_rate = 0.633928571
no_memory pass_rate = 0.455357143

full mean_quality = 0.680546428
no_memory mean_quality = 0.341839146

full mean_release = 0.299855464
no_memory mean_release = 0.085369974

full final_cumulative_release = 153.963406058
no_memory final_cumulative_release = 52.369918094

no_memory event_match_to_full = 0.8125
no_memory score_mae_to_full = 0.199107556
no_memory release_mae_to_full = 0.21448549
```

## Recommended next experiment

```text
contextual_membrane_v2_counterfactual_residue
```

Core idea:

```text
isolate unchosen alternatives
compare observed residue vs unobserved-alternative residue
ablate only counterfactual residue
measure next-pass bias
test whether output-not-chosen changes later membrane decisions
```

## Claim boundary

The current results are contextual component results only.

They do not establish quantum-specific behavior, formal measurement contextuality, life, metabolism, self-repair, consciousness, or physical matter synthesis.
