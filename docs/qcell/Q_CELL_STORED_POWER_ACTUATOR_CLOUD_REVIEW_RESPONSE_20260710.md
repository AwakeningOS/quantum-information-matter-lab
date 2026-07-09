# Cloud review response - Q-cell stored-power actuator v0

Date: 2026-07-10 JST

## Core conclusion

The design direction is acceptable, but the central risk is that
`internal_store_energy` may look like bookkeeping after the fact rather than a
causal variable that constrains controller action.

The experiment must prove this ordering:

```text
store exists before action
store_before_action decides whether action is allowed
allowed action spends store
W changes as a consequence of allowed action
```

Do not explain store after observing W.

## Required controls

```text
store_shuffle_control
supply_label_only_control
equal_total_supply_timing_control
no_controller_drain_control
fixed_controller_baseline
```

Required integrity checks:

```text
action_used > 0 implies controller_energy_spent > 0
store_empty implies action_used = 0
store_before_action, not store_after_action, gates action
```

## Minimum first GPU run

Use only `QFCBM_0988` for the first run.

Conditions:

```text
supply_never_on + initial_store_zero
supply_always_on + initial_store_zero
supply_stop_midway + initial_store_zero
supply_restart_after_stop + initial_store_zero
supply_never_on + initial_store_positive
```

This is enough to test:

```text
zero store -> no action
supply -> fill
fill -> action
action -> spend/depletion
empty -> starvation
restart -> refill
refill -> action recovery
```

## Required cyclewise trace fields

```text
t
seed
condition
supply_on
external_supply_in
store_before_action
controller_action_requested
controller_action_allowed
controller_energy_spent
store_after_action
controller_starved
W_resource
W_no_resource
resource_attributable_W
accounting_residual
```

`store_before_action` is mandatory. Without it, the store looks like a
post-hoc accounting log.

## Fixed store update rule

Use a predeclared update rule:

```text
store[t+1] =
  clamp(
    store[t]
    + supply_gain * external_supply_in[t]
    - controller_energy_spent[t]
    - leak[t],
    0,
    store_capacity
  )
```

Action gating:

```text
controller_action_allowed[t] =
  controller_action_requested[t] and store_before_action[t] >= action_cost
```

## Failure conditions

Immediate failure:

```text
store = 0 and controller action fires
controller action fires but store does not decrease
supply_never_on + initial_zero produces sustained action
supply_stop_midway continues without starvation after depletion
restart refills store but action/W does not recover
W improves without matching store/spend/starvation trace
```

Research failure:

```text
store mechanics work but W does not improve
W improves but does not track store depletion/recovery
```

## Claim ceiling

Allowed:

```text
In this explicit model, controller action is causally gated by a finite internal
store. External supply fills the store, controller action depletes it, action
stops when the store is empty, and output recovery occurs when supply resumes
and the store refills.
```

Must attach:

```text
This establishes a model-level stored-power actuator, not a physical energy
reservoir.
```

Forbidden:

```text
life
metabolism
agency
homeostasis
quantum advantage
real thermodynamic work
physical energy storage
autonomous energy harvesting
self-maintenance
biological organization
```

## Reviewer attack surface

The first attack will be:

```text
store is just bookkeeping
```

The defense must be cyclewise evidence that `store_before_action` gates
`controller_action_allowed`.

The second attack will be:

```text
supply condition is doing the work, not store
```

Therefore the store-shuffle, supply-label-only, and equal-total-supply timing
controls are required before promotion beyond the first mechanistic trace.

