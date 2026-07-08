# Protocol: contextual_membrane_quantum_anchor_probe_v1

Date: 2026-07-08

## Question

Can the contextual membrane anchor survive an explicit witness-table audit instead of only a surrogate score audit?

This follows:

```text
contextual_membrane_quantum_anchor_probe = surrogate audit bridge
contextual_membrane_quantum_anchor_probe_v1 = stricter witness-table audit
```

## Layer

```text
QUANTUM_AUDIT
```

## Motivation

The first anchor probe showed that the membrane boundary can be mapped to a PM/KCBS-like surrogate pattern.

The v1 audit makes the bridge stricter:

```text
explicit KCBS-style probability tables
explicit PM-style parity tables
no-disturbance / marginal-consistency checks
exhaustive deterministic-assignment bound checks
same-marginal and noncontextual controls
```

This is still not a quantum-specific claim.

## KCBS-style table

The KCBS-shaped part uses five binary measurements:

```text
q0 q1 q2 q3 q4
```

and five edge contexts:

```text
q0-q1
q1-q2
q2-q3
q3-q4
q4-q0
```

The audited event is the directed transition:

```text
E_i = q_i=1 and q_{i+1}=0
```

Exhaustive deterministic assignments over five binary variables give:

```text
max sum_i E_i = 2
```

## PM-style table

The PM-shaped part uses a 3x3 parity table with six row/column contexts.

Five contexts have target parity +1. The final column has target parity -1.

Exhaustive deterministic assignments over nine +/-1 variables give:

```text
max satisfied contexts = 5 of 6
accuracy bound = 5/6
```

## Variants

```text
full_witness_table_anchor
additive_boundary_table
same_marginals_independent_table
shuffled_context_table
noncontextual_hidden_assignment_fit
strong_classical_table_baseline
```

## Multi-seed panel

```text
20260708
20260709
20260710
20260711
20260712
```

## Success criteria

```text
kcbs_bound_computed_eq_2
pm_bound_computed_eq_5_over_6
full_kcbs_sum_mean_gt_bound_plus_0_15
full_pm_accuracy_mean_gt_bound_plus_0_05
full_kcbs_no_disturbance_max_abs_mean_le_1e_9
full_pm_no_disturbance_max_abs_mean_le_1e_9
same_marginals_kcbs_sum_mean_lt_bound
strong_baseline_kcbs_sum_mean_lt_bound
strong_baseline_pm_accuracy_mean_lt_bound
full_kcbs_sum_wins_all_controls_5_of_5
full_pm_accuracy_wins_all_controls_5_of_5
```

## Run command

```bash
python scripts/contextual/contextual_membrane_quantum_anchor_probe_v1.py \
  --seed 20260708 \
  --out data/contextual/contextual_membrane_quantum_anchor_probe_v1_seed20260708.json \
  --csv data/contextual/contextual_membrane_quantum_anchor_probe_v1_seed20260708_aggregate.csv \
  --seed-csv data/contextual/contextual_membrane_quantum_anchor_probe_v1_seed20260708_seed_summary.csv
```

## Claim boundary

This experiment can support only a witness-table audit-candidate claim.

It does not establish quantum-specific behavior, formal measurement contextuality, hardware-backed contextuality, biological organization, self-repair, metabolism, consciousness, or physical matter synthesis.
