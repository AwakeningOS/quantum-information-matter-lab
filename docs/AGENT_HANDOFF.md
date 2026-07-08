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

Key full vs no_memory comparison:

```text
full pass_rate = 0.633928571
no_memory pass_rate = 0.455357143
full final_cumulative_release = 153.963406058
no_memory final_cumulative_release = 52.369918094
no_memory event_match_to_full = 0.8125
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

Key full vs observed_only comparison:

```text
full pass_rate = 0.479910714
observed_only pass_rate = 0.531250000

full final_cumulative_release = 52.388208985
observed_only final_cumulative_release = 75.770977236

observed_only event_match_to_full = 0.814732143
observed_only score_mae_to_full = 0.164462842
observed_only release_mae_to_full = 0.074669816
```

Counterfactual polarity:

```text
full counterfactual_polarity_probe = 0.170622487
counterfactual_sign_flip counterfactual_polarity_probe = -0.407708026
counterfactual_shuffle counterfactual_polarity_probe = -0.216989363
```

Interpretation:

```text
previous BLOCK leaves unchosen PASS residue, which raises later score relative to observed_only.
previous PASS leaves unchosen BLOCK residue, which lowers later score relative to observed_only.
```

## Recommended next experiment

```text
contextual_membrane_v3_order_effect
```

Core idea:

```text
use the same context/object multiset
permute only order
compare final membrane state, event timing, quality, release, and residue distribution
require order-only changes to alter final membrane boundary
```

## Claim boundary

The current results are contextual component results only.

They do not establish quantum-specific behavior, formal measurement contextuality, life, metabolism, self-repair, consciousness, or physical matter synthesis.
