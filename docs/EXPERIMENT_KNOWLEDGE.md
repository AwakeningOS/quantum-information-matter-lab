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

The component-level contextual behavior passed the v0 criteria, but memory necessity is not yet established.

The context-no-memory variant remained close to full:

```text
event_match_to_full = 0.984375
score_mae_to_full = 0.008596154
```

This means v1 should sharpen the memory question.

### Do not claim

```text
Do not claim contextual_membrane_v0 demonstrates quantum-specific behavior.
Do not claim it demonstrates formal measurement contextuality.
Do not claim it demonstrates biological organization or consciousness.
Do not claim memory necessity from v0 alone.
```

### Better v1 direction

Use memory ablations and delayed-effect metrics:

```text
full
no_memory
low_memory_decay
high_memory_decay
same-context replay
same-transition replay
```

Primary success should require memory ablation to reduce event-level fit or delayed context effects, not merely preserve context-conditioned bias.
