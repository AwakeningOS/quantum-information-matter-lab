# Result: contextual_membrane_v3_order_effect

Status: RAW_LOG_BACKED  
Generator script: `scripts/contextual/contextual_membrane_v3_order_effect.py`  
Raw log: `data/contextual/contextual_membrane_v3_order_effect_seed20260708.json`  
Summary CSV: `data/contextual/contextual_membrane_v3_order_effect_seed20260708_summary.csv`  
Run command: `python scripts/contextual/contextual_membrane_v3_order_effect.py --seed 20260708 --steps 512 --out data/contextual/contextual_membrane_v3_order_effect_seed20260708.json --csv data/contextual/contextual_membrane_v3_order_effect_seed20260708_summary.csv`  
Layer: CONTEXTUAL_COMPONENT  
Verdict: PASS_ORDER_EFFECT  
Claim boundary: component-level order-effect membrane behavior only; no quantum-specific promotion.

## Summary

`contextual_membrane_v3_order_effect` tests whether the same event multiset changes the membrane depending only on order.

The result is:

```text
PASS_ORDER_EFFECT
```

Every order variant preserves the same `(context, object, u)` event multiset. The only manipulated variable is ordering.

## Main metrics

| Variant | Pass rate | Mean score | Mean release | Final cumulative release | Event match to original | Score MAE | Release MAE | Final residue L1 | Final state distance |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| original_order | 0.640625000 | 0.624109862 | 0.282969298 | 145.156796757 | n/a | n/a | n/a | n/a | n/a |
| reverse_order | 0.631696429 | 0.625002511 | 0.261379357 | 132.740948410 | 0.535714286 | 0.190852382 | 0.096147518 | 1.395097921 | 0.251560909 |
| block_shuffle_order | 0.658482143 | 0.612684320 | 0.292718462 | 149.228270459 | 0.593750000 | 0.172580196 | 0.074048139 | 1.042309054 | 0.158769773 |
| compatible_cluster_order | 0.698660714 | 0.663760830 | 0.355225255 | 178.941328214 | 0.526785714 | 0.193337358 | 0.090498602 | 1.092896097 | 0.555788100 |
| random_order_same_multiset | 0.604910714 | 0.584343294 | 0.228613842 | 115.454200271 | 0.540178571 | 0.170379001 | 0.084804227 | 0.856036973 | 0.360170403 |
| context_sorted_order | 0.825892857 | 0.761422268 | 0.569178125 | 293.695236578 | 0.582589286 | 0.196039058 | 0.295975145 | 2.306517995 | 1.533965348 |

## Criteria

| Criterion | Result |
|---|---|
| all_variants_preserve_context_object_u_multiset | True |
| reverse_event_match_to_original_le_0_90 | True |
| random_event_match_to_original_le_0_90 | True |
| block_shuffle_release_mae_to_original_ge_0_02 | True |
| context_sorted_final_state_distance_ge_0_15 | True |
| at_least_3_order_variants_residue_l1_ge_0_10 | True |

## Key result

The same event multiset produced different membrane trajectories when order changed.

```text
original_order final_cumulative_release = 145.156796757
reverse_order final_cumulative_release = 132.740948410
random_order_same_multiset final_cumulative_release = 115.454200271
context_sorted_order final_cumulative_release = 293.695236578
```

Event timing also changed strongly:

```text
reverse_order event_match_to_original = 0.535714286
block_shuffle_order event_match_to_original = 0.593750000
compatible_cluster_order event_match_to_original = 0.526785714
random_order_same_multiset event_match_to_original = 0.540178571
context_sorted_order event_match_to_original = 0.582589286
```

Final residue distribution changed as well:

```text
reverse_order final_residue_l1_to_original = 1.395097921
block_shuffle_order final_residue_l1_to_original = 1.042309054
compatible_cluster_order final_residue_l1_to_original = 1.092896097
random_order_same_multiset final_residue_l1_to_original = 0.856036973
context_sorted_order final_residue_l1_to_original = 2.306517995
```

## Interpretation

This result supports the component-level claim that order alone can alter the implemented membrane's event timing, downstream release trajectory, and final residue distribution.

The important point is that v3 does not add new materials. It reorders the same event multiset. Therefore the effect is not explained by object frequency or context frequency.

## Limitations

```text
1. This is a designed component, not a natural discovery.
2. This is still classical contextual component behavior, not quantum-specific behavior.
3. The order-sensitive memory mechanism is explicit and engineered.
4. The experiment does not yet isolate joint/non-additive object-context boundary effects; v4 should do that.
5. The experiment does not establish formal measurement contextuality.
6. No biological, consciousness, metabolism, self-repair, or physical matter synthesis claim is made.
```

## Next local lesson

The next experiment should isolate joint boundary effects:

```text
contextual_membrane_v4_joint_boundary:
  compare object-only replay
  compare context-only replay
  compare additive object+context model
  compare pairwise replay
  require full joint boundary to reproduce membrane decisions
```
