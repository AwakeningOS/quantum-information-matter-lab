# Protocol: contextual_membrane_v4_joint_boundary

Date: 2026-07-08

## Question

Does the membrane decision require the full object/context joint boundary rather than object-only, context-only, additive, or static pairwise approximations?

This is the next test after `contextual_membrane_v3_order_effect`.

```text
v0 = context-looking membrane
v1 = memory-bearing boundary
v2 = counterfactual-residue boundary
v3 = order-sensitive boundary
v4 = joint/non-additive boundary
```

## Layer

```text
CONTEXTUAL_COMPONENT
```

## Motivation

`contextual_membrane_v3_order_effect` showed that order alone can alter membrane trajectory while preserving the same event multiset.

However, v3 did not isolate whether the membrane boundary requires the full joint object/context combination.

The target question is:

```text
Can object-only, context-only, additive, or static pairwise controls reproduce the full membrane boundary?
```

## Variants

```text
full_joint_boundary:
  object term + context term + joint object/context term + dynamic joint residue

object_only_replay:
  object marginal score and object-keyed residue only

context_only_replay:
  context marginal score and context-keyed residue only

additive_object_context_model:
  object + context additive model without joint term or joint residue

pairwise_static_replay:
  static pairwise object/context score but no dynamic joint residue

joint_shuffle_control:
  wrong joint association for static joint score and dynamic joint residue
```

## Model

Each event contains:

```text
context
object
u threshold
```

The full membrane computes passage score from:

```text
base level
+ object term
+ context term
+ joint object/context term
+ observed joint residue
+ counterfactual joint residue
+ separable residue
+ transition residue
- incompatibility penalty
```

Controls remove or corrupt different parts of this joint boundary.

## Metrics

```text
pass_rate
mean_score
mean_joint_term
mean_counterfactual_joint_term
mean_quality
mean_release
final_cumulative_release
event_match_to_full
score_mae_to_full
release_mae_to_full
quality_mae_to_full
final_residue_l1_to_full
final_state_distance_to_full
```

## Success criteria

Joint-boundary PASS requires all of:

```text
object_only_event_match_to_full <= 0.88
context_only_event_match_to_full <= 0.88
additive_event_match_to_full <= 0.90
pairwise_static_event_match_to_full <= 0.92
joint_shuffle_event_match_to_full <= 0.88
at least 4 controls have score_mae_to_full >= 0.08
```

## Failure interpretation

If object-only, context-only, additive, static pairwise, or shuffled joint controls remain close to full, then the joint-boundary claim fails or must be weakened.

## Run command

```bash
python scripts/contextual/contextual_membrane_v4_joint_boundary.py \
  --seed 20260708 \
  --steps 512 \
  --out data/contextual/contextual_membrane_v4_joint_boundary_seed20260708.json \
  --csv data/contextual/contextual_membrane_v4_joint_boundary_seed20260708_summary.csv
```

## Raw outputs

```text
data/contextual/contextual_membrane_v4_joint_boundary_seed20260708.json
data/contextual/contextual_membrane_v4_joint_boundary_seed20260708_summary.csv
```

## Claim boundary

This experiment can support only a component-level joint-boundary claim.

It does not establish quantum-specific behavior, formal measurement contextuality, biological organization, self-repair, metabolism, consciousness, or physical matter synthesis.
