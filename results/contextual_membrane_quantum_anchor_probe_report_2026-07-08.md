# Result: contextual_membrane_quantum_anchor_probe

Status: RAW_LOG_BACKED  
Generator script: `scripts/contextual/contextual_membrane_quantum_anchor_probe.py`  
Raw log: `data/contextual/contextual_membrane_quantum_anchor_probe_seed20260708.json`  
Aggregate CSV: `data/contextual/contextual_membrane_quantum_anchor_probe_seed20260708_aggregate.csv`  
Seed CSV: `data/contextual/contextual_membrane_quantum_anchor_probe_seed20260708_seed_summary.csv`  
Run command: `python scripts/contextual/contextual_membrane_quantum_anchor_probe.py --seed 20260708 --trials-per-context 256 --out data/contextual/contextual_membrane_quantum_anchor_probe_seed20260708.json --csv data/contextual/contextual_membrane_quantum_anchor_probe_seed20260708_aggregate.csv --seed-csv data/contextual/contextual_membrane_quantum_anchor_probe_seed20260708_seed_summary.csv`  
Layer: QUANTUM_AUDIT  
Verdict: PASS_ANCHOR_CANDIDATE_SURROGATE_NOT_QUANTUM  
Claim boundary: witness-shaped audit bridge only; no quantum-specific promotion.

## Summary

`contextual_membrane_quantum_anchor_probe` tests whether the contextual membrane boundary can be mapped into a PM/KCBS-like audit shape under controls.

The result is:

```text
PASS_ANCHOR_CANDIDATE_SURROGATE_NOT_QUANTUM
```

This is deliberately not a quantum-contextuality claim. It is an anchor-candidate result: the implemented boundary can be projected into a witness-shaped surrogate pattern, and the pattern survives the stated controls.

## Multi-seed panel

```text
20260708
20260709
20260710
20260711
20260712
```

## Main aggregate metrics

| Variant | KCBS anchor sum mean | Excess over 2 mean | Single marginal drift mean | PM parity accuracy mean | KCBS gap vs full | PM accuracy gap vs full |
|---|---:|---:|---:|---:|---:|---:|
| full_membrane_anchor | 2.272656250 | 0.272656250 | 0.011440947 | 0.859765625 | n/a | n/a |
| additive_boundary_anchor | 1.632812500 | -0.367187500 | 0.011505337 | 0.616015625 | 0.639843750 | 0.243750000 |
| same_marginals_replay | 1.534375000 | -0.465625000 | 0.011670582 | 0.611328125 | 0.738281250 | 0.248437500 |
| shuffled_context_anchor | 2.040625000 | 0.040625000 | 0.011540255 | 0.664713542 | 0.232031250 | 0.195052083 |
| noncontextual_hidden_state_fit | 1.746875000 | -0.253125000 | 0.011646561 | 0.640885417 | 0.525781250 | 0.218880208 |
| strong_classical_anchor_baseline | 1.864062500 | -0.135937500 | 0.011436270 | 0.701953125 | 0.408593750 | 0.157812500 |

## Criteria

| Criterion | Result |
|---|---|
| full_kcbs_anchor_sum_mean_gt_2_10 | True |
| full_kcbs_excess_over_2_mean_gt_0_10 | True |
| additive_kcbs_anchor_sum_mean_lt_2_00 | True |
| same_marginals_kcbs_anchor_sum_mean_lt_2_00 | True |
| full_pm_parity_accuracy_mean_ge_0_80 | True |
| strong_baseline_pm_accuracy_gap_ge_0_10 | True |
| full_kcbs_sum_wins_all_controls_5_of_5 | True |
| full_pm_accuracy_wins_all_controls_5_of_5 | True |

## Key result: KCBS-shaped surrogate

The full membrane anchor exceeds the surrogate odd-cycle bound, while the additive, same-marginal, noncontextual-fit, and strong classical controls remain below it.

```text
full_membrane_anchor kcbs_anchor_sum_mean = 2.272656250
additive_boundary_anchor kcbs_anchor_sum_mean = 1.632812500
same_marginals_replay kcbs_anchor_sum_mean = 1.534375000
noncontextual_hidden_state_fit kcbs_anchor_sum_mean = 1.746875000
strong_classical_anchor_baseline kcbs_anchor_sum_mean = 1.864062500
```

The shuffled-context anchor gets closer, but remains lower than full:

```text
shuffled_context_anchor kcbs_anchor_sum_mean = 2.040625000
full_membrane_anchor kcbs_anchor_sum_mean = 2.272656250
```

## Key result: PM-like parity surrogate

The full anchor has higher PM-like parity accuracy than every control.

```text
full_membrane_anchor pm_parity_accuracy_mean = 0.859765625
additive_boundary_anchor pm_parity_accuracy_mean = 0.616015625
same_marginals_replay pm_parity_accuracy_mean = 0.611328125
shuffled_context_anchor pm_parity_accuracy_mean = 0.664713542
noncontextual_hidden_state_fit pm_parity_accuracy_mean = 0.640885417
strong_classical_anchor_baseline pm_parity_accuracy_mean = 0.701953125
```

Full wins both KCBS-shaped score and PM-like parity accuracy against every control in all five seeds.

## Interpretation

This result supports only the following cautious claim:

```text
The implemented contextual membrane boundary can be mapped to a PM/KCBS-like surrogate audit pattern that survives additive, same-marginal, shuffled-context, noncontextual-fit, and strong-classical controls.
```

It does not show that the component is quantum. It does not show formal measurement contextuality. It only says that the boundary has an audit-compatible shape worth testing against a real witness later.

## Limitations

```text
1. This is a witness-shaped surrogate, not a real quantum contextuality witness.
2. This is not hardware-backed.
3. This is not a formal PM or KCBS proof.
4. The anchor mapping is engineered.
5. No quantum-specific behavior is promoted from this result alone.
6. No biological, consciousness, metabolism, self-repair, or physical matter synthesis claim is made.
```

## Next local lesson

The next step should be a stricter audit bridge, not a claim promotion:

```text
contextual_membrane_quantum_anchor_probe_v1:
  replace surrogate scores with explicit witness tables
  add no-disturbance / marginal-consistency checks
  add noncontextual polytope or exhaustive deterministic assignment bound checks
  optionally map to existing PM/KCBS hardware-backed result structure
```

Only after that should a true hardware-backed quantum audit be considered.
