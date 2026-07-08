# Protocol: contextual_membrane_quantum_anchor_probe

Date: 2026-07-08

## Question

Can the contextual membrane boundary be connected to PM/KCBS-like witness logic as a separate audit bridge?

This follows the hardened classical component line:

```text
v1 = memory-bearing boundary
v2 = counterfactual-residue boundary
v3 = order-sensitive boundary
v4 = joint/non-additive boundary
reactor v0 = downstream propagation
reactor v1 = hardened propagation controls
quantum anchor = separate audit bridge
```

## Layer

```text
QUANTUM_AUDIT
```

## Motivation

The reactor v1 result hardened the classical component claim. The next question is not whether the component is already quantum.

The next question is narrower:

```text
Can the membrane decision boundary be mapped into a witness-shaped PM/KCBS audit pattern under controls?
```

This experiment is intentionally separated from the classical component propagation claim.

## Variants

```text
full_membrane_anchor:
  full contextual membrane mapped to KCBS-like cycle events and PM-like parity contexts

additive_boundary_anchor:
  additive object/context boundary, no full joint membrane state

same_marginals_replay:
  preserves rough single-measurement marginals but breaks contextual edge alignment

shuffled_context_anchor:
  shifts context-edge structure and residue alignment

noncontextual_hidden_state_fit:
  single hidden-state style fit with edge-independent probability level

strong_classical_anchor_baseline:
  stronger classical baseline with smooth non-contextual drive
```

## Audit shapes

### KCBS-like cycle surrogate

Five edge contexts are used:

```text
q0-q1
q1-q2
q2-q3
q3-q4
q4-q0
```

The probe computes an anchor-event sum over the five edges.

The classical odd-cycle exclusivity bound is used only as a surrogate audit threshold:

```text
KCBS-shaped surrogate bound = 2.0
```

### PM-like parity surrogate

Six parity contexts are used:

```text
r1
r2
r3
c1
c2
c3
```

The probe measures how consistently the membrane tracks a PM-like parity pattern.

## Metrics

```text
kcbs_anchor_sum
kcbs_anchor_excess_over_2
kcbs_event_rate_mean
single_marginal_drift
pm_parity_accuracy
pm_parity_error
win counts against controls
```

## Success criteria

Anchor-candidate PASS requires all of:

```text
full_kcbs_anchor_sum_mean_gt_2_10
full_kcbs_excess_over_2_mean_gt_0_10
additive_kcbs_anchor_sum_mean_lt_2_00
same_marginals_kcbs_anchor_sum_mean_lt_2_00
full_pm_parity_accuracy_mean_ge_0_80
strong_baseline_pm_accuracy_gap_ge_0_10
full_kcbs_sum_wins_all_controls_5_of_5
full_pm_accuracy_wins_all_controls_5_of_5
```

## Failure interpretation

If same-marginal or additive controls reproduce the full anchor pattern, the anchor candidate fails.

If the strong classical baseline matches the PM/KCBS-like scores, the anchor candidate should not be promoted.

## Run command

```bash
python scripts/contextual/contextual_membrane_quantum_anchor_probe.py \
  --seed 20260708 \
  --trials-per-context 256 \
  --out data/contextual/contextual_membrane_quantum_anchor_probe_seed20260708.json \
  --csv data/contextual/contextual_membrane_quantum_anchor_probe_seed20260708_aggregate.csv \
  --seed-csv data/contextual/contextual_membrane_quantum_anchor_probe_seed20260708_seed_summary.csv
```

## Claim boundary

This experiment can support only a witness-shaped audit-bridge claim.

It does not establish quantum-specific behavior, formal measurement contextuality, biological organization, self-repair, metabolism, consciousness, or physical matter synthesis.

Any quantum-specific claim still requires a separate real quantum witness or hardware-backed audit.
