# Protocol: contextual_membrane_v2_counterfactual_residue

Date: 2026-07-08

## Question

Do unchosen alternatives leave residue that changes later contextual membrane decisions?

This is the next test after `contextual_membrane_v1_memory_ablation`.

```text
v0 = context-looking membrane
v1 = memory-bearing boundary
v2 = counterfactual-residue boundary
```

## Layer

```text
CONTEXTUAL_COMPONENT
```

## Motivation

`contextual_membrane_v1_memory_ablation` showed that dynamic memory changes membrane decisions and downstream quality/release trajectory.

However, v1 did not isolate which part of memory matters. This v2 test isolates the residue of the output that did not happen:

```text
if PASS happened, BLOCK remains as unchosen alternative
if BLOCK happened, PASS remains as unchosen alternative
```

The target is the component-level version of:

```text
Does the meaning that was not output still remain and bias the next boundary decision?
```

## Variants

```text
full_observed_and_counterfactual:
  observed residue + unchosen-alternative residue

observed_only:
  observed residue only; counterfactual residue gain set to 0

counterfactual_only:
  counterfactual residue only; observed residue gain set to 0

no_residue:
  observed, counterfactual, and transition residue set to 0

counterfactual_sign_flip:
  counterfactual residue gain sign is reversed

counterfactual_shuffle:
  counterfactual residue is read from a wrong object key
```

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
+ observed PASS/BLOCK residue
+ counterfactual PASS/BLOCK residue
+ transition residue
- incompatibility penalty
```

A PASS event writes:

```text
observed PASS residue
counterfactual BLOCK residue
```

A BLOCK event writes:

```text
observed BLOCK residue
counterfactual PASS residue
```

## Counterfactual polarity probe

The key probe compares `full_observed_and_counterfactual` against `observed_only`.

For later same `(context, object)` events:

```text
full_minus_observed_only after previous same-key BLOCK
full_minus_observed_only after previous same-key PASS
counterfactual_polarity_probe = after_BLOCK_delta - after_PASS_delta
```

Expected direction:

```text
previous BLOCK leaves unchosen PASS residue -> raises later score
previous PASS leaves unchosen BLOCK residue -> lowers later score
```

## Metrics

```text
pass_rate
mean_score
mean_counterfactual_term
mean_quality
mean_release
final_cumulative_release
event_match_to_full
score_mae_to_full
release_mae_to_full
quality_mae_to_full
counterfactual_polarity_probe
```

## Success criteria

Counterfactual-residue PASS requires all of:

```text
observed_only_event_match_to_full <= 0.92
observed_only_score_mae_to_full >= 0.03
observed_only_release_mae_to_full >= 0.01
full_counterfactual_polarity_probe >= 0.08
counterfactual_sign_flip_event_match_to_full <= 0.85
counterfactual_shuffle_event_match_to_full <= 0.92
```

## Failure interpretation

If `observed_only` remains close to full, then unchosen-alternative residue is not necessary.

If `counterfactual_sign_flip` does not strongly alter event timing or polarity, then the apparent effect is not specific to counterfactual residue direction.

## Run command

```bash
python scripts/contextual/contextual_membrane_v2_counterfactual_residue.py \
  --seed 20260708 \
  --steps 512 \
  --out data/contextual/contextual_membrane_v2_counterfactual_residue_seed20260708.json \
  --csv data/contextual/contextual_membrane_v2_counterfactual_residue_seed20260708_summary.csv
```

## Raw outputs

```text
data/contextual/contextual_membrane_v2_counterfactual_residue_seed20260708.json
data/contextual/contextual_membrane_v2_counterfactual_residue_seed20260708_summary.csv
```

## Claim boundary

This experiment can support only a component-level counterfactual-residue claim.

It does not establish quantum-specific behavior, formal measurement contextuality, biological organization, self-repair, metabolism, consciousness, or physical matter synthesis.
