# Protocol: contextual_membrane_v3_order_effect

Date: 2026-07-08

## Question

Does the same context/object event multiset change the membrane depending only on order?

This is the next test after `contextual_membrane_v2_counterfactual_residue`.

```text
v0 = context-looking membrane
v1 = memory-bearing boundary
v2 = counterfactual-residue boundary
v3 = order-sensitive boundary
```

## Layer

```text
CONTEXTUAL_COMPONENT
```

## Motivation

`contextual_membrane_v2_counterfactual_residue` showed that unchosen alternatives can leave residue that changes later membrane decisions.

However, v2 did not isolate pure order effects. This v3 test holds the event multiset fixed and permutes only order.

The target question is:

```text
If the same materials appear in a different sequence, does the final boundary change?
```

## Variants

```text
original_order:
  baseline order

reverse_order:
  exact reverse of the baseline event multiset

block_shuffle_order:
  shuffle contiguous blocks while preserving events inside blocks

compatible_cluster_order:
  cluster compatible context families differently

random_order_same_multiset:
  random permutation of the same event multiset

context_sorted_order:
  group by context, then object, then u
```

All variants preserve the same `(context, object, u)` multiset.

## Model

Each event contains:

```text
context
object
u threshold
```

The membrane computes passage score from:

```text
base object score
+ context-object bias
+ observed residue
+ counterfactual residue
+ transition residue
+ order trace residue
- incompatibility penalty
```

A PASS event writes:

```text
observed PASS residue
counterfactual BLOCK residue
order trace for the context
```

A BLOCK event writes:

```text
observed BLOCK residue
counterfactual PASS residue
anti-order trace for the context
```

## Metrics

```text
pass_rate
mean_score
mean_order_trace_term
mean_quality
mean_release
final_quality
final_reservoir
final_cumulative_release
event_match_to_original
score_mae_to_original
release_mae_to_original
quality_mae_to_original
final_residue_l1_to_original
final_state_distance_to_original
```

## Success criteria

Order-effect PASS requires all of:

```text
all_variants_preserve_context_object_u_multiset = True
reverse_event_match_to_original <= 0.90
random_event_match_to_original <= 0.90
block_shuffle_release_mae_to_original >= 0.02
context_sorted_final_state_distance >= 0.15
at least 3 order variants have final_residue_l1_to_original >= 0.10
```

## Failure interpretation

If order variants remain close to original while preserving the same event multiset, then the order-effect claim fails.

## Run command

```bash
python scripts/contextual/contextual_membrane_v3_order_effect.py \
  --seed 20260708 \
  --steps 512 \
  --out data/contextual/contextual_membrane_v3_order_effect_seed20260708.json \
  --csv data/contextual/contextual_membrane_v3_order_effect_seed20260708_summary.csv
```

## Raw outputs

```text
data/contextual/contextual_membrane_v3_order_effect_seed20260708.json
data/contextual/contextual_membrane_v3_order_effect_seed20260708_summary.csv
```

## Claim boundary

This experiment can support only a component-level order-effect claim.

It does not establish quantum-specific behavior, formal measurement contextuality, biological organization, self-repair, metabolism, consciousness, or physical matter synthesis.
