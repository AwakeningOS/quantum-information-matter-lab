# Protocol: contextual_reactor_v0_membrane_to_flow

Date: 2026-07-08

## Question

Do contextual membrane PASS/BLOCK decisions propagate into a downstream reactor's release, quality, reservoir, and persistence variables?

This is the next test after the v1-v4 membrane line.

```text
v1 = memory-bearing boundary
v2 = counterfactual-residue boundary
v3 = order-sensitive boundary
v4 = joint/non-additive boundary
reactor v0 = membrane-to-flow propagation
```

## Layer

```text
CLASSICAL_COMPONENT
```

## Motivation

The v1-v4 membrane line established a designed contextual component whose boundary depends on memory, unchosen alternatives, order, and full object/context joint state.

This test asks whether that membrane structure actually reaches a downstream flow component.

The target question is:

```text
Does the membrane only decide locally, or does it change downstream flow?
```

## Variants

```text
full_membrane_to_reactor:
  full joint membrane drives the reactor

no_memory_membrane_to_reactor:
  static membrane without memory drives the reactor

no_counterfactual_membrane_to_reactor:
  membrane with observed memory but no counterfactual residue drives the reactor

order_scrambled_membrane_to_reactor:
  same events under scrambled order drive the reactor

additive_boundary_membrane_to_reactor:
  additive object+context membrane drives the reactor

reactor_without_membrane:
  reactor receives a simple fixed PASS/BLOCK signal rather than contextual membrane signal
```

## Reactor variables

```text
reactor
quality
stability
release
persistence
cumulative_release
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

Propagation PASS requires all of:

```text
no_memory_release_mae_to_full >= 0.05
no_counterfactual_release_mae_to_full >= 0.02
order_scrambled_final_state_distance >= 0.20
additive_boundary_event_match_to_full <= 0.90
abs(reactor_without_membrane_cumulative_release_delta_vs_full) >= 25
full_final_persistence >= 5
```

## Failure interpretation

If downstream reactor variables remain close when memory, counterfactual residue, order, joint boundary, or membrane coupling are removed, then the propagation claim fails.

## Run command

```bash
python scripts/contextual/contextual_reactor_v0_membrane_to_flow.py \
  --seed 20260708 \
  --steps 512 \
  --out data/contextual/contextual_reactor_v0_membrane_to_flow_seed20260708.json \
  --csv data/contextual/contextual_reactor_v0_membrane_to_flow_seed20260708_summary.csv
```

## Raw outputs

```text
data/contextual/contextual_reactor_v0_membrane_to_flow_seed20260708.json
data/contextual/contextual_reactor_v0_membrane_to_flow_seed20260708_summary.csv
```

## Claim boundary

This experiment can support only a component-level membrane-to-flow propagation claim.

It does not establish quantum-specific behavior, formal measurement contextuality, biological organization, self-repair, metabolism, consciousness, or physical matter synthesis.
