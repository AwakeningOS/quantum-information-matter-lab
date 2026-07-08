# Result: contextual_membrane_v4_joint_boundary

Status: RAW_LOG_BACKED  
Generator script: `scripts/contextual/contextual_membrane_v4_joint_boundary.py`  
Raw log: `data/contextual/contextual_membrane_v4_joint_boundary_seed20260708.json`  
Summary CSV: `data/contextual/contextual_membrane_v4_joint_boundary_seed20260708_summary.csv`  
Run command: `python scripts/contextual/contextual_membrane_v4_joint_boundary.py --seed 20260708 --steps 512 --out data/contextual/contextual_membrane_v4_joint_boundary_seed20260708.json --csv data/contextual/contextual_membrane_v4_joint_boundary_seed20260708_summary.csv`  
Layer: CONTEXTUAL_COMPONENT  
Verdict: PASS_JOINT_BOUNDARY  
Claim boundary: component-level joint-boundary membrane behavior only; no quantum-specific promotion.

## Summary

`contextual_membrane_v4_joint_boundary` tests whether the membrane decision requires the full object/context joint boundary.

The result is:

```text
PASS_JOINT_BOUNDARY
```

The key result is that object-only, context-only, additive object+context, static pairwise, and joint-shuffle controls fail to reproduce the full joint membrane.

## Main metrics

| Variant | Pass rate | Mean score | Mean release | Final cumulative release | Event match to full | Score MAE | Release MAE | Final state distance |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| full_joint_boundary | 0.575892857 | 0.578131805 | 0.191754149 | 103.696477783 | n/a | n/a | n/a | n/a |
| object_only_replay | 0.296875000 | 0.307700921 | 0.026598653 | 17.522951078 | 0.685267857 | 0.297422952 | 0.165155496 | 1.243213745 |
| context_only_replay | 0.234375000 | 0.273258598 | 0.019630208 | 12.540111148 | 0.609375000 | 0.340038949 | 0.172123941 | 1.251299401 |
| additive_object_context_model | 0.245535714 | 0.271812748 | 0.022468514 | 13.964177586 | 0.665178571 | 0.306924220 | 0.169285635 | 1.083256858 |
| static_pairwise_replay | 0.381696429 | 0.412905513 | 0.052273684 | 36.327646821 | 0.805803571 | 0.165994085 | 0.139480465 | 0.763630683 |
| joint_shuffle_control | 0.388392857 | 0.397173828 | 0.061706792 | 41.956207828 | 0.714285714 | 0.250621077 | 0.132015011 | 0.647499089 |

## Criteria

| Criterion | Result |
|---|---|
| object_only_event_match_to_full_le_0_88 | True |
| context_only_event_match_to_full_le_0_88 | True |
| additive_event_match_to_full_le_0_90 | True |
| pairwise_event_match_to_full_le_0_92 | True |
| joint_shuffle_event_match_to_full_le_0_88 | True |
| additive_score_mae_to_full_ge_0_05 | True |
| pairwise_release_mae_to_full_ge_0_02 | True |

## Key result

The additive model fails strongly:

```text
full_joint_boundary final_cumulative_release = 103.696477783
additive_object_context_model final_cumulative_release = 13.964177586
additive_object_context_model event_match_to_full = 0.665178571
additive_object_context_model score_mae_to_full = 0.306924220
additive_object_context_model release_mae_to_full = 0.169285635
```

The static pairwise replay is closer than object-only/context-only, but still fails:

```text
static_pairwise_replay final_cumulative_release = 36.327646821
static_pairwise_replay event_match_to_full = 0.805803571
static_pairwise_replay score_mae_to_full = 0.165994085
static_pairwise_replay release_mae_to_full = 0.139480465
```

The joint-shuffle control also fails:

```text
joint_shuffle_control event_match_to_full = 0.714285714
joint_shuffle_control score_mae_to_full = 0.250621077
joint_shuffle_control release_mae_to_full = 0.132015011
```

## Interpretation

This result supports the component-level claim that the implemented membrane requires a full joint object/context boundary under the tested controls.

The important distinction is:

```text
object alone is not enough
context alone is not enough
object + context as additive factors is not enough
static pair identity is not enough
wrong joint key is not enough
```

In this designed component, the membrane depends on the full object/context joint state plus dynamic joint memory, counterfactual joint residue, and joint transition residue.

## Limitations

```text
1. This is a designed component, not a natural discovery.
2. This is still classical contextual component behavior, not quantum-specific behavior.
3. The full joint boundary mechanism is explicit and engineered.
4. This does not establish formal measurement contextuality.
5. No biological, consciousness, metabolism, self-repair, or physical matter synthesis claim is made.
```

## Next local lesson

The v1-v4 membrane line is now complete enough to consider propagation:

```text
contextual_reactor_v0_membrane_to_flow:
  connect membrane PASS/BLOCK outputs to a downstream reactor
  measure release, quality, reservoir, and persistence
  test whether membrane structure changes downstream flow without making quantum-specific claims
```

The later quantum-anchor probe should still wait until the classical contextual membrane line is stable.
