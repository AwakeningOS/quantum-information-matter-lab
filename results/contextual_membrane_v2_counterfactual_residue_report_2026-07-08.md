# Result: contextual_membrane_v2_counterfactual_residue

Status: RAW_LOG_BACKED  
Generator script: `scripts/contextual/contextual_membrane_v2_counterfactual_residue.py`  
Raw log: `data/contextual/contextual_membrane_v2_counterfactual_residue_seed20260708.json`  
Summary CSV: `data/contextual/contextual_membrane_v2_counterfactual_residue_seed20260708_summary.csv`  
Run command: `python scripts/contextual/contextual_membrane_v2_counterfactual_residue.py --seed 20260708 --steps 512 --out data/contextual/contextual_membrane_v2_counterfactual_residue_seed20260708.json --csv data/contextual/contextual_membrane_v2_counterfactual_residue_seed20260708_summary.csv`  
Layer: CONTEXTUAL_COMPONENT  
Verdict: PASS_COUNTERFACTUAL_RESIDUE  
Claim boundary: component-level counterfactual-residue membrane behavior only; no quantum-specific promotion.

## Summary

`contextual_membrane_v2_counterfactual_residue` tests whether unchosen alternatives leave residue that changes later membrane decisions.

The result is:

```text
PASS_COUNTERFACTUAL_RESIDUE
```

The key result is that `observed_only` does not reproduce full, and sign-flipping or shuffling counterfactual residue strongly changes event timing and polarity.

## Main metrics

| Variant | Pass rate | Mean score | Mean counterfactual term | Mean quality | Mean release | Final cumulative release | Event match to full | Score MAE to full | Release MAE to full | Counterfactual polarity probe |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| full_observed_and_counterfactual | 0.479910714 | 0.475670917 | -0.015057860 | 0.360622958 | 0.092296099 | 52.388208985 | n/a | n/a | n/a | 0.170622487 |
| observed_only | 0.531250000 | 0.518475615 | 0.000000000 | 0.470364245 | 0.151449205 | 75.770977236 | 0.814732143 | 0.164462842 | 0.074669816 | 0.000000000 |
| counterfactual_only | 0.482142857 | 0.476129748 | -0.006741548 | 0.349113777 | 0.087105546 | 48.473879637 | 0.921875000 | 0.072250799 | 0.012345634 | 0.242536873 |
| no_residue | 0.459821429 | 0.451049107 | 0.000000000 | 0.328747932 | 0.076970814 | 44.016919647 | 0.935267857 | 0.066409824 | 0.019157654 | 0.113089664 |
| counterfactual_sign_flip | 0.448660714 | 0.480633449 | 0.010738009 | 0.362382333 | 0.104332672 | 53.808430877 | 0.665178571 | 0.333786105 | 0.061339437 | -0.407708026 |
| counterfactual_shuffle | 0.537946429 | 0.540405568 | 0.022350255 | 0.463218509 | 0.149360429 | 77.848100292 | 0.745535714 | 0.258644598 | 0.060655774 | -0.216989363 |

## Criteria

| Criterion | Result |
|---|---|
| observed_only_event_match_to_full_le_0_92 | True |
| observed_only_score_mae_to_full_ge_0_03 | True |
| observed_only_release_mae_to_full_ge_0_01 | True |
| full_counterfactual_polarity_probe_ge_0_08 | True |
| counterfactual_sign_flip_event_match_to_full_le_0_85 | True |
| counterfactual_shuffle_event_match_to_full_le_0_92 | True |

## Key comparison: full vs observed_only

```text
full pass_rate = 0.479910714
observed_only pass_rate = 0.531250000

full mean_score = 0.475670917
observed_only mean_score = 0.518475615

full mean_release = 0.092296099
observed_only mean_release = 0.151449205

full final_cumulative_release = 52.388208985
observed_only final_cumulative_release = 75.770977236

observed_only event_match_to_full = 0.814732143
observed_only score_mae_to_full = 0.164462842
observed_only release_mae_to_full = 0.074669816
```

## Counterfactual polarity probe

The polarity probe measures how much full differs from observed-only after the previous same-key event was BLOCK versus PASS.

```text
full cf_delta_after_prior_block_vs_observed_only = 0.037041787
full cf_delta_after_prior_pass_vs_observed_only = -0.133580700
full counterfactual_polarity_probe = 0.170622487
```

Interpretation:

```text
previous BLOCK leaves unchosen PASS residue, which raises later score relative to observed_only.
previous PASS leaves unchosen BLOCK residue, which lowers later score relative to observed_only.
```

Sign flip control reverses this polarity:

```text
counterfactual_sign_flip counterfactual_polarity_probe = -0.407708026
counterfactual_sign_flip event_match_to_full = 0.665178571
```

Shuffle control also destroys/reverses the original polarity:

```text
counterfactual_shuffle counterfactual_polarity_probe = -0.216989363
counterfactual_shuffle event_match_to_full = 0.745535714
```

## Interpretation

This result supports the component-level claim that, in the implemented mechanism, later membrane decisions depend on residue from unchosen alternatives.

The important point is not simply that memory matters. v1 already showed that. v2 narrows the claim: the unobserved alternative branch itself contributes a directional bias to later membrane scores.

## Limitations

```text
1. This is a designed component, not a natural discovery.
2. This is still classical contextual component behavior, not quantum-specific behavior.
3. The counterfactual residue mechanism is explicit and engineered.
4. The experiment does not yet isolate pure order effects alone; v3 should do that.
5. The experiment does not establish formal measurement contextuality.
6. No biological, consciousness, metabolism, self-repair, or physical matter synthesis claim is made.
```

## Next local lesson

The next experiment should isolate order effects:

```text
contextual_membrane_v3_order_effect:
  use the same context/object multiset
  permute only order
  compare final membrane state, event timing, quality, release, and residue distribution
  require order-only changes to alter final membrane boundary
```
