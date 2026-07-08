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

### What was tested

A membrane whose passage score depends on:

```text
object identity
readout/question context
context compatibility
retained observed outputs
retained unobserved alternatives
```

### Controls and variants

```text
full_contextual
context_no_memory
object_only
object_marginal_replay
shuffled_context_full
```

### Result snapshot

```text
full_contextual object_conditioned_context_score_range_mean = 0.333906636
full_contextual compatibility_score_gap = 0.285508247
object_only object_conditioned_context_score_range_mean = 0.0
object_marginal_replay compatibility_score_gap = 0.055738863
shuffled_context_full compatibility_score_gap = 0.221874876
```

### Lesson

The component-level contextual behavior passed the v0 criteria, but memory necessity was not established.

The context-no-memory variant remained close to full:

```text
event_match_to_full = 0.984375
score_mae_to_full = 0.008596154
```

## contextual_membrane_v1_memory_ablation knowledge

### What was tested

A memory-bearing membrane with ablations:

```text
full
no_memory
low_memory_decay
high_memory_decay
same_context_replay
same_transition_replay
```

The test included downstream trajectory variables:

```text
quality
release
reservoir
cumulative_release
event timing
```

### Result snapshot

```text
Verdict = PASS_MEMORY_DEPENDENT_BOUNDARY

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

### Lesson

v1 supports the component-level claim that, in the implemented mechanism, dynamic memory changes membrane decisions and downstream quality/release trajectory.

Low memory decay diverged from full, so memory lifetime matters.

High memory decay overshot full, so too much persistence also changes the boundary.

Replay variants stayed event-level different from full, so context/object coupling and order remain important.

### Do not claim

```text
Do not claim v1 demonstrates quantum-specific behavior.
Do not claim v1 demonstrates formal measurement contextuality.
Do not claim v1 demonstrates biological organization or consciousness.
Do not claim v1 isolates counterfactual residue alone.
Do not claim v1 isolates pure order effects alone.
```

## Next experiment: contextual_membrane_v2_counterfactual_residue

The next experiment should isolate unchosen alternatives.

Use variants such as:

```text
full_observed_and_counterfactual
observed_only
counterfactual_only
no_counterfactual
counterfactual_sign_flip
next-pass-bias probe
```

Primary success should require counterfactual-residue ablation to change next-pass bias or later membrane decisions while observed-path residue is held fixed.
