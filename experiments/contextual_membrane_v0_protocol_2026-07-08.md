# Protocol: contextual_membrane_v0

Date: 2026-07-08

## Question

Can the first contextual membrane component produce passage behavior that depends on question/context structure, compatibility, and memory, rather than object identity alone?

## Layer

```text
CONTEXTUAL_COMPONENT
```

## Model

The membrane receives a stream of `(context, object, threshold)` events.

Contexts:

```text
identity
path
boundary
history
```

Objects:

```text
A
B
P
Q
```

The full component uses:

```text
base object score
+ context-object bias
+ retained observed/unobserved memory term
- incompatibility penalty for incompatible context transitions
```

The component records both the observed output and the unobserved alternative for each event.

## Controls

```text
context_no_memory:
  context-object bias and compatibility penalty, but no retained memory term

object_only:
  object base score only; context, compatibility, and memory removed

object_marginal_replay:
  object-only replay using mean object scores learned from the full run

shuffled_context_full:
  full contextual mechanism on the same object/threshold stream, but with context order shuffled
```

## Metrics

```text
pass_rate
mean_score
object_conditioned_context_score_range_mean
compatibility_score_gap
event_match_to_full
score_mae_to_full
```

## Success criteria

```text
full_object_conditioned_context_range_ge_0_15
full_compatibility_gap_ge_0_10
object_only_context_range_le_0_05
object_replay_event_match_below_0_90
```

## Fixed seed/config

```text
seed: 20260708
steps: 64
memory_decay: 0.94
memory_gain: 0.18
alternative_gain: 0.06
incompatibility_penalty: 0.22
min_score: 0.02
max_score: 0.98
```

## Raw outputs

```text
data/contextual/contextual_membrane_v0_seed20260708.json
data/contextual/contextual_membrane_v0_seed20260708_rows.csv
```

## Claim boundary

This experiment can support only a designed contextual-component claim:

```text
The implemented membrane expresses context-conditioned passage behavior
against object-only/replay controls.
```

It does not support a quantum-specific claim, a physical matter claim, or a consciousness claim. Quantum/contextuality promotion requires a separate witness/audit experiment.
