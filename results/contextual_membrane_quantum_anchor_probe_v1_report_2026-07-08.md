# Result: contextual_membrane_quantum_anchor_probe_v1

Status: RAW_LOG_BACKED  
Generator script: `scripts/contextual/contextual_membrane_quantum_anchor_probe_v1.py`  
Raw log: `data/contextual/contextual_membrane_quantum_anchor_probe_v1_seed20260708.json`  
Aggregate CSV: `data/contextual/contextual_membrane_quantum_anchor_probe_v1_seed20260708_aggregate.csv`  
Seed CSV: `data/contextual/contextual_membrane_quantum_anchor_probe_v1_seed20260708_seed_summary.csv`  
Run command: `python scripts/contextual/contextual_membrane_quantum_anchor_probe_v1.py --seed 20260708 --out data/contextual/contextual_membrane_quantum_anchor_probe_v1_seed20260708.json --csv data/contextual/contextual_membrane_quantum_anchor_probe_v1_seed20260708_aggregate.csv --seed-csv data/contextual/contextual_membrane_quantum_anchor_probe_v1_seed20260708_seed_summary.csv`  
Layer: QUANTUM_AUDIT  
Verdict: PASS_STRICT_WITNESS_TABLE_AUDIT_CANDIDATE_NOT_QUANTUM  
Claim boundary: explicit witness-table audit candidate only; no quantum-specific or hardware-backed promotion.

## Summary

`contextual_membrane_quantum_anchor_probe_v1` replaces the previous surrogate audit with explicit PM/KCBS-shaped probability tables.

The result is:

```text
PASS_STRICT_WITNESS_TABLE_AUDIT_CANDIDATE_NOT_QUANTUM
```

This is still not a quantum-contextuality claim. It is a stricter audit-candidate result: the simulated tables pass explicit witness-shaped checks and exhaustive deterministic-assignment bound checks.

## Computed deterministic bounds

The script computes the noncontextual-style deterministic bounds by exhaustive enumeration.

```text
KCBS-style directed-transition bound = 2
KCBS max-assignment count = 10
PM-style parity accuracy bound = 5/6 = 0.8333333333333334
PM max satisfied contexts = 5 of 6
```

## Main aggregate metrics

| Variant | KCBS witness sum mean | KCBS excess over bound | KCBS no-disturbance max | PM parity accuracy mean | PM excess over bound | PM no-disturbance max |
|---|---:|---:|---:|---:|---:|---:|
| full_witness_table_anchor | 2.256568549 | 0.256568549 | 0.000000000000 | 0.921974446 | 0.088641112 | 0.000000000000 |
| additive_boundary_table | 1.601132037 | -0.398867963 | 0.000000000000 | 0.628229114 | -0.205104220 | 0.000000000000 |
| same_marginals_independent_table | 1.241136885 | -0.758863115 | 0.000000000000 | 0.608851602 | -0.224481732 | 0.000000000000 |
| shuffled_context_table | 1.986193805 | -0.013806195 | 0.000000000000 | 0.696225106 | -0.137108227 | 0.000000000000 |
| noncontextual_hidden_assignment_fit | 1.735531896 | -0.264468104 | 0.052681778745 | 0.804391588 | -0.028941745 | 0.000000000000 |
| strong_classical_table_baseline | 1.873890389 | -0.126109611 | 0.000000000000 | 0.813065892 | -0.020267441 | 0.000000000000 |

## Criteria

| Criterion | Result |
|---|---|
| kcbs_bound_computed_eq_2 | True |
| pm_bound_computed_eq_5_over_6 | True |
| full_kcbs_sum_mean_gt_bound_plus_0_15 | True |
| full_pm_accuracy_mean_gt_bound_plus_0_05 | True |
| full_kcbs_no_disturbance_max_abs_mean_le_1e_9 | True |
| full_pm_no_disturbance_max_abs_mean_le_1e_9 | True |
| same_marginals_kcbs_sum_mean_lt_bound | True |
| strong_baseline_kcbs_sum_mean_lt_bound | True |
| strong_baseline_pm_accuracy_mean_lt_bound | True |
| full_kcbs_sum_wins_all_controls_5_of_5 | True |
| full_pm_accuracy_wins_all_controls_5_of_5 | True |

## Key result: explicit KCBS-style table

The full witness-table anchor exceeds the computed deterministic bound:

```text
full_witness_table_anchor kcbs_witness_sum_mean = 2.256568549
computed deterministic bound = 2
excess = 0.256568549
```

The controls remain below the bound:

```text
additive_boundary_table kcbs_witness_sum_mean = 1.601132037
same_marginals_independent_table kcbs_witness_sum_mean = 1.241136885
shuffled_context_table kcbs_witness_sum_mean = 1.986193805
noncontextual_hidden_assignment_fit kcbs_witness_sum_mean = 1.735531896
strong_classical_table_baseline kcbs_witness_sum_mean = 1.873890389
```

The full table also has exact expected no-disturbance under this simulation:

```text
full_witness_table_anchor kcbs_no_disturbance_max_abs_mean = 0.000000000000
```

## Key result: explicit PM-style parity table

The full witness-table anchor exceeds the computed deterministic PM parity bound:

```text
full_witness_table_anchor pm_parity_accuracy_mean = 0.921974446
computed deterministic bound = 0.8333333333333334
excess = 0.088641112
```

The controls remain below the bound:

```text
additive_boundary_table pm_parity_accuracy_mean = 0.628229114
same_marginals_independent_table pm_parity_accuracy_mean = 0.608851602
shuffled_context_table pm_parity_accuracy_mean = 0.696225106
noncontextual_hidden_assignment_fit pm_parity_accuracy_mean = 0.804391588
strong_classical_table_baseline pm_parity_accuracy_mean = 0.813065892
```

The full PM table also has exact expected no-disturbance under this simulation:

```text
full_witness_table_anchor pm_no_disturbance_max_abs_mean = 0.000000000000
```

## Interpretation

This result supports only the following cautious claim:

```text
The implemented membrane anchor can be represented by explicit PM/KCBS-shaped probability tables that pass deterministic-bound and no-disturbance checks under the stated simulated controls.
```

This is stronger than the previous surrogate audit, but it still does not show that the component is quantum. It does not show hardware-backed contextuality. It does not by itself prove formal measurement contextuality of an implemented physical system.

## Limitations

```text
1. This is a simulated witness-table audit candidate, not a real quantum experiment.
2. The probability tables are engineered.
3. The no-disturbance values are exact expected-table checks, not finite-shot hardware estimates.
4. This is not hardware-backed.
5. No quantum-specific behavior is promoted from this result alone.
6. No biological, consciousness, metabolism, self-repair, or physical matter synthesis claim is made.
```

## Next local lesson

The next experiment should move from table audit to hardware/audit compatibility:

```text
contextual_membrane_quantum_anchor_probe_v2_hardware_mapping:
  map the witness-table anchor to the existing PM/KCBS hardware-backed result format
  separate simulated table values from real QPU witness values
  add finite-shot noise model and compare with hardware witness margins
  require all quantum-specific claims to remain outside this component unless hardware witness controls pass
```
