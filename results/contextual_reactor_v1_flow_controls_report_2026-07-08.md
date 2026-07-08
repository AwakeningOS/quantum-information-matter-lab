# Result: contextual_reactor_v1_flow_controls

Status: RAW_LOG_BACKED  
Generator script: `scripts/contextual/contextual_reactor_v1_flow_controls.py`  
Raw log: `data/contextual/contextual_reactor_v1_flow_controls_seed20260708.json`  
Aggregate CSV: `data/contextual/contextual_reactor_v1_flow_controls_seed20260708_aggregate.csv`  
Seed CSV: `data/contextual/contextual_reactor_v1_flow_controls_seed20260708_seed_summary.csv`  
Run command: `python scripts/contextual/contextual_reactor_v1_flow_controls.py --seed 20260708 --steps 512 --out data/contextual/contextual_reactor_v1_flow_controls_seed20260708.json --csv data/contextual/contextual_reactor_v1_flow_controls_seed20260708_aggregate.csv --seed-csv data/contextual/contextual_reactor_v1_flow_controls_seed20260708_seed_summary.csv`  
Layer: CLASSICAL_COMPONENT  
Verdict: PASS_HARDENED_MEMBRANE_TO_FLOW_CONTROLS  
Claim boundary: component-level hardened membrane-to-flow propagation controls only; no quantum-specific promotion.

## Summary

`contextual_reactor_v1_flow_controls` stress-tests the reactor v0 propagation result.

The result is:

```text
PASS_HARDENED_MEMBRANE_TO_FLOW_CONTROLS
```

The key result is that full contextual membrane propagation survives multi-seed controls, matched pass-rate controls, matched signal replay controls, an additive-boundary replacement, and a stronger reactor-without-membrane baseline.

## Multi-seed panel

```text
20260708
20260709
20260710
20260711
20260712
```

## Main aggregate metrics

| Variant | Pass rate mean | Final quality mean | Final persistence mean | Final cumulative release mean | Event match to full mean | Release MAE to full mean | Final state distance mean |
|---|---:|---:|---:|---:|---:|---:|---:|
| full_membrane_to_reactor | 0.689285714 | 1.308064781 | 20.400910610 | 100.992143180 | n/a | n/a | n/a |
| no_memory_membrane_to_reactor | 0.451785714 | 0.515222977 | 1.836211665 | 15.680632362 | 0.751785714 | 0.182037735 | 2.216888086 |
| no_counterfactual_membrane_to_reactor | 0.631696428 | 0.946087913 | 10.767849220 | 56.589383421 | 0.853125000 | 0.096875427 | 1.130867426 |
| matched_pass_rate_random_membrane | 0.670535714 | 0.799324150 | 5.114475169 | 45.316304998 | 0.562500000 | 0.131686605 | 1.763983170 |
| matched_signal_shuffle_replay | 0.674107143 | 0.908414851 | 9.438825659 | 76.914353974 | 0.569642857 | 0.097656770 | 1.222437163 |
| matched_signal_lag_replay | 0.678571429 | 1.061318978 | 11.981202902 | 79.115226502 | 0.586607143 | 0.086895798 | 0.932307199 |
| additive_boundary_membrane_to_reactor | 0.271428571 | 0.358967487 | 0.921519354 | 7.062086795 | 0.579464286 | 0.200911773 | 2.400786743 |
| strong_reactor_without_membrane | 0.668750000 | 1.149719729 | 10.167187854 | 52.936920966 | 0.568750000 | 0.121152732 | 1.278174529 |

## Criteria

| Criterion | Result |
|---|---|
| multi_seed_full_persistence_wins_all_controls_5_of_5 | True |
| multi_seed_full_quality_wins_all_controls_5_of_5 | True |
| matched_pass_rate_release_mae_mean_ge_0_03 | True |
| matched_signal_shuffle_final_state_distance_mean_ge_0_20 | True |
| matched_signal_lag_persistence_mae_mean_ge_0_75 | True |
| strong_reactor_without_membrane_full_persistence_margin_ge_1 | True |
| additive_boundary_cumulative_release_delta_abs_mean_ge_25 | True |

## Key result: full wins quality and persistence across seeds

Full membrane wins final quality and final persistence against every control in every seed.

```text
all_controls_persistence_wins = 5/5 for every control
all_controls_quality_wins = 5/5 for every control
all_controls_cumulative_release_wins = 5/5 for every control
```

The strongest comparison is not pass rate. The matched pass-rate random control has nearly the same pass rate as full:

```text
full_membrane_to_reactor pass_rate_mean = 0.689285714
matched_pass_rate_random_membrane pass_rate_mean = 0.670535714
```

But it does not reproduce downstream flow:

```text
full_membrane_to_reactor final_persistence_mean = 20.400910610
matched_pass_rate_random_membrane final_persistence_mean = 5.114475169

full_membrane_to_reactor final_cumulative_release_mean = 100.992143180
matched_pass_rate_random_membrane final_cumulative_release_mean = 45.316304998

matched_pass_rate_random_membrane release_mae_to_full_mean = 0.131686605
```

## Matched signal controls

The matched-signal controls preserve the signal distribution but break timing or alignment.

```text
matched_signal_shuffle_replay final_persistence_mean = 9.438825659
matched_signal_lag_replay final_persistence_mean = 11.981202902
full_membrane_to_reactor final_persistence_mean = 20.400910610
```

So the result is not explained by signal distribution alone.

## Strong no-membrane baseline

The stronger non-contextual reactor baseline is closer than the weak no-membrane baseline, but it still does not match full.

```text
strong_reactor_without_membrane final_quality_mean = 1.149719729
full_membrane_to_reactor final_quality_mean = 1.308064781

strong_reactor_without_membrane final_persistence_mean = 10.167187854
full_membrane_to_reactor final_persistence_mean = 20.400910610

strong_reactor_without_membrane final_cumulative_release_mean = 52.936920966
full_membrane_to_reactor final_cumulative_release_mean = 100.992143180
```

## Interpretation

This result supports the component-level claim that membrane-to-flow propagation is not reducible to:

```text
same pass rate
same signal distribution
lagged signal replay
additive object/context boundary
stronger reactor dynamics without membrane state
```

The result hardens the classical component claim:

```text
A contextual membrane can control the flow of a downstream reaction field in this designed component.
```

## Limitations

```text
1. This is a designed component, not a natural discovery.
2. This is classical component propagation, not quantum-specific behavior.
3. The reactor and membrane mechanisms are explicit and engineered.
4. This does not establish formal measurement contextuality.
5. No biological, consciousness, metabolism, self-repair, or physical matter synthesis claim is made.
```

## Next local lesson

After this result, the component line is strong enough to branch cautiously:

```text
contextual_membrane_quantum_anchor_probe:
  keep separate from the component propagation claim
  test whether boundary decisions can be linked to PM/KCBS-like contextuality witnesses
  do not promote quantum-specific claims unless witness-level controls pass
```

A further `contextual_reactor_v2` can still be used if more classical robustness is desired, but the immediate next conceptual bridge is the quantum-anchor probe.
