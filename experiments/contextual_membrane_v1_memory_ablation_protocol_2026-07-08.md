# Protocol: contextual_membrane_v1_memory_ablation

Date: 2026-07-08

## Question

Does the contextual membrane actually require dynamic memory to change its membrane decisions and downstream trajectory?

This is the first main test after `contextual_membrane_v0`.

```text
v0 = context-looking membrane
v1 = memory-bearing boundary
```

## Layer

```text
CONTEXTUAL_COMPONENT
```

## Motivation

`contextual_membrane_v0` showed that membrane decisions can depend on context/question structure.

However, v0 did not establish that memory was necessary. The `context_no_memory` variant remained close to full.

This v1 experiment therefore asks whether the boundary carries causal residue from:

```text
past context
observed path
unobserved alternatives
context order
```

## Variants

```text
full:
  normal memory-bearing membrane

no_memory:
  memory_gain = 0
  alternative_gain = 0
  transition_memory_gain = 0

low_memory_decay:
  short memory lifetime

high_memory_decay:
  long memory lifetime

same_context_replay:
  keep context sequence and event timing fixed
  shuffle objects inside each context

same_transition_replay:
  preserve compatible/incompatible transition mask
  alter concrete context order and object assignment
```

## Model

Each event contains:

```text
context
object
u threshold
```

The membrane computes a passage score from:

```text
base object score
+ context-object bias
+ observed PASS/BLOCK residue
+ unchosen alternative PASS/BLOCK residue
+ transition memory
- incompatibility penalty
```

A pass event feeds a small downstream component:

```text
reservoir
quality
release
cumulative_release
```

This makes the test stricter than v0: memory must change not only score, but also event timing and downstream release/quality trajectory.

## Metrics

```text
pass_rate
mean_score
compatible_pass_rate
incompatible_pass_rate
compatibility_pass_gap
mean_quality
mean_release
final_reservoir
final_cumulative_release
mean_inter_pass_interval
event_match_to_full
timing_flip_rate_vs_full
score_mae_to_full
quality_mae_to_full
release_mae_to_full
reservoir_mae_to_full
cumulative_release_delta_vs_full
```

## Success criteria

Memory-dependent boundary PASS requires all of:

```text
no_memory_event_match_to_full <= 0.90
no_memory_score_mae_to_full >= 0.05
no_memory_release_mae_to_full >= 0.01
low_memory_decay_score_mae_to_full >= 0.02
same_context_replay_event_match_to_full <= 0.92
same_transition_replay_event_match_to_full <= 0.92
```

## Failure interpretation

If `no_memory` remains close to `full`, then the memory claim fails even if context-conditioned membrane behavior remains.

## Run command

```bash
python scripts/contextual/contextual_membrane_v1_memory_ablation.py \
  --seed 20260708 \
  --steps 512 \
  --out data/contextual/contextual_membrane_v1_memory_ablation_seed20260708.json \
  --csv data/contextual/contextual_membrane_v1_memory_ablation_seed20260708_summary.csv
```

## Raw outputs

```text
data/contextual/contextual_membrane_v1_memory_ablation_seed20260708.json
data/contextual/contextual_membrane_v1_memory_ablation_seed20260708_summary.csv
```

## Claim boundary

This experiment can support only a component-level memory-dependent membrane claim.

It does not establish quantum-specific behavior, formal measurement contextuality, biological organization, self-repair, metabolism, consciousness, or physical matter synthesis.
