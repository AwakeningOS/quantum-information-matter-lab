# Protocol: contextual_reactor_v1_flow_controls

Date: 2026-07-08

## Question

Does membrane-to-flow propagation survive stronger classical controls?

This test follows `contextual_reactor_v0_membrane_to_flow`.

```text
v1 = memory-bearing boundary
v2 = counterfactual-residue boundary
v3 = order-sensitive boundary
v4 = joint/non-additive boundary
reactor v0 = downstream propagation
reactor v1 = hardened flow controls
```

## Layer

```text
CLASSICAL_COMPONENT
```

## Motivation

The v0 reactor result showed that membrane structure can propagate into downstream release, quality, reservoir, and persistence.

However, v0 still leaves an obvious criticism:

```text
Maybe the reactor only needs a similar pass rate or a similar signal distribution.
Maybe the membrane was only wired in, not functionally necessary.
```

This v1 test attacks that criticism before attempting any quantum-anchor connection.

## Variants

```text
full_membrane_to_reactor:
  full contextual membrane drives the reactor

no_memory_membrane_to_reactor:
  full static boundary, but no dynamic memory terms

no_counterfactual_membrane_to_reactor:
  dynamic memory remains, but counterfactual residue is removed

matched_pass_rate_random_membrane:
  random membrane signal matched to the full membrane pass rate

matched_signal_shuffle_replay:
  exact full membrane signal distribution, shuffled in time

matched_signal_lag_replay:
  exact full membrane signal distribution, shifted by seed-dependent lag

additive_boundary_membrane_to_reactor:
  additive object+context boundary replaces full joint membrane

strong_reactor_without_membrane:
  stronger non-contextual reactor baseline with mean-drive feedback, but no membrane state
```

## Multi-seed panel

```text
20260708
20260709
20260710
20260711
20260712
```

## Metrics

```text
pass_rate
mean_membrane_signal
mean_reactor
mean_quality
mean_stability
mean_release
final_reactor
final_quality
final_stability
final_persistence
final_cumulative_release
event_match_to_full
membrane_signal_mae_to_full
release_mae_to_full
reactor_mae_to_full
quality_mae_to_full
persistence_mae_to_full
final_state_distance_to_full
```

## Success criteria

Hardened propagation PASS requires all of:

```text
multi_seed_full_persistence_wins_all_controls_5_of_5
multi_seed_full_quality_wins_all_controls_5_of_5
matched_pass_rate_release_mae_mean_ge_0_03
matched_signal_shuffle_final_state_distance_mean_ge_0_20
matched_signal_lag_persistence_mae_mean_ge_0_75
strong_reactor_without_membrane_full_persistence_margin_ge_1
additive_boundary_cumulative_release_delta_abs_mean_ge_25
```

## Failure interpretation

If matched pass-rate or matched signal controls reproduce full flow, then the membrane-specific propagation claim fails.

If a strong reactor-without-membrane baseline matches full, then the result is probably generic reactor dynamics rather than membrane-to-flow propagation.

If quality/persistence do not remain stable across seeds, then the result should not be promoted beyond v0.

## Run command

```bash
python scripts/contextual/contextual_reactor_v1_flow_controls.py \
  --seed 20260708 \
  --steps 512 \
  --out data/contextual/contextual_reactor_v1_flow_controls_seed20260708.json \
  --csv data/contextual/contextual_reactor_v1_flow_controls_seed20260708_aggregate.csv \
  --seed-csv data/contextual/contextual_reactor_v1_flow_controls_seed20260708_seed_summary.csv
```

## Raw outputs

```text
data/contextual/contextual_reactor_v1_flow_controls_seed20260708.json
data/contextual/contextual_reactor_v1_flow_controls_seed20260708_aggregate.csv
data/contextual/contextual_reactor_v1_flow_controls_seed20260708_seed_summary.csv
```

## Claim boundary

This experiment can support only a component-level hardened propagation-control claim.

It does not establish quantum-specific behavior, formal measurement contextuality, biological organization, self-repair, metabolism, consciousness, or physical matter synthesis.
