# Result: contextual_membrane_v1_memory_ablation

Status: RAW_LOG_BACKED  
Generator script: `scripts/contextual/contextual_membrane_v1_memory_ablation.py`  
Raw log: `data/contextual/contextual_membrane_v1_memory_ablation_seed20260708.json`  
Summary CSV: `data/contextual/contextual_membrane_v1_memory_ablation_seed20260708_summary.csv`  
Run command: `python scripts/contextual/contextual_membrane_v1_memory_ablation.py --seed 20260708 --steps 512 --out data/contextual/contextual_membrane_v1_memory_ablation_seed20260708.json --csv data/contextual/contextual_membrane_v1_memory_ablation_seed20260708_summary.csv`  
Layer: CONTEXTUAL_COMPONENT  
Verdict: PASS_MEMORY_DEPENDENT_BOUNDARY  
Claim boundary: component-level memory-dependent membrane behavior only; no quantum-specific promotion.

## Summary

`contextual_membrane_v1_memory_ablation` tests whether the contextual membrane actually needs memory.

The result is:

```text
PASS_MEMORY_DEPENDENT_BOUNDARY
```

The no-memory ablation diverged from full in event timing, passage score, quality, release, reservoir, and cumulative release.

## Main metrics

| Variant | Pass rate | Mean score | Compatibility pass gap | Mean quality | Mean release | Final cumulative release | Event match to full | Score MAE to full | Release MAE to full |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| full | 0.633928571 | 0.647863042 | 0.263241736 | 0.680546428 | 0.299855464 | 153.963406058 | n/a | n/a | n/a |
| no_memory | 0.455357143 | 0.451116071 | 0.150139387 | 0.341839146 | 0.085369974 | 52.369918094 | 0.812500000 | 0.199107556 | 0.214485490 |
| low_memory_decay | 0.462053571 | 0.455856929 | 0.159398646 | 0.348186967 | 0.089047692 | 54.313308344 | 0.819196429 | 0.194033840 | 0.210807771 |
| high_memory_decay | 0.816964286 | 0.818766176 | 0.170649144 | 0.939831737 | 0.580033190 | 281.540829666 | 0.816964286 | 0.175308835 | 0.280177727 |
| same_context_replay | 0.616071429 | 0.635140551 | 0.249701314 | 0.635524902 | 0.266046043 | 139.718119959 | 0.803571429 | 0.191056479 | 0.058659966 |
| same_transition_replay | 0.667410714 | 0.655459880 | 0.264934289 | 0.735915553 | 0.344603918 | 175.423569986 | 0.779017857 | 0.234098030 | 0.071370491 |

## Criteria

| Criterion | Result |
|---|---|
| no_memory_event_match_to_full_le_0_90 | True |
| no_memory_score_mae_to_full_ge_0_05 | True |
| no_memory_release_mae_to_full_ge_0_01 | True |
| low_memory_differs_from_full_score_mae_ge_0_02 | True |
| same_context_replay_event_match_to_full_le_0_92 | True |
| same_transition_replay_event_match_to_full_le_0_92 | True |

## Key comparison: full vs no_memory

```text
full pass_rate = 0.633928571
no_memory pass_rate = 0.455357143

full mean_quality = 0.680546428
no_memory mean_quality = 0.341839146

full mean_release = 0.299855464
no_memory mean_release = 0.085369974

full final_cumulative_release = 153.963406058
no_memory final_cumulative_release = 52.369918094

no_memory event_match_to_full = 0.812500000
no_memory score_mae_to_full = 0.199107556
no_memory release_mae_to_full = 0.214485490
```

## Interpretation

This result supports the component-level claim that the implemented membrane is not merely context-looking. It is memory-bearing under the tested mechanism.

The no-memory ablation is not close to full:

```text
event_match_to_full = 0.812500000
timing_flip_rate_vs_full = 0.187500000
score_mae_to_full = 0.199107556
quality_mae_to_full = 0.338707282
release_mae_to_full = 0.214485490
cumulative_release_delta_vs_full = -101.593487964
```

Low memory decay also diverges from full, indicating that memory lifetime matters.

High memory decay overshoots full, indicating that too much persistence changes the boundary and downstream release trajectory.

The replay variants remain substantially different from full at event level, meaning order and context/object coupling matter in this designed component.

## Limitations

```text
1. This is a designed component, not a natural discovery.
2. This is still classical contextual component behavior, not quantum-specific behavior.
3. The memory mechanism is explicit and engineered.
4. The experiment does not yet isolate counterfactual residue alone; v2 should do that.
5. The experiment does not yet isolate pure order effects alone; v3 should do that.
6. No biological, consciousness, metabolism, self-repair, or physical matter synthesis claim is made.
```

## Next local lesson

The next experiment should isolate unchosen alternatives:

```text
contextual_membrane_v2_counterfactual_residue:
  compare observed residue vs unobserved-alternative residue
  ablate only counterfactual residue
  measure next-pass bias
  test whether output-not-chosen changes later membrane decisions
```
