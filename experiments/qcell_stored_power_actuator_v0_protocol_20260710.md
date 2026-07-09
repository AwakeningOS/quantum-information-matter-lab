# Q-cell stored-power actuator v0 protocol

Date: 2026-07-10 JST

Status: design-review protocol, not yet executed.

## Purpose

Test whether the next Q-cell controller can be tied to an internal stored-power
accounting variable rather than a free or purely external controller budget.

Core question:

```text
Can model-level stored power fill under supply, be spent by controller action,
stop action when empty, and support output recovery when supply resumes?
```

## Starting point

Use the evolved controller from `qcell_controller_evolution_v0` and the robust
region from `qcell_battery_powered_controller_v0`:

```text
primary grid = QFCBM_0988
```

Optional follow-up grids:

```text
QFCBM_0496
QFCBM_0399
```

## Model idea

Introduce an internal store `S`.

At each cycle:

```text
external resource supply can add to S
controller action costs kappa * sum(abs(dynamic_angles))
if S is insufficient, scale or stop dynamic action
action spending reduces S
```

This is an explicit accounting model. It is not a physical thermodynamic
actuator.

## Minimal conditions

Run first on `QFCBM_0988` only.

```text
supply_always_on
supply_never_on
supply_stop_midway
supply_restart_after_stop
initial_store_zero
initial_store_positive
```

Controller/control families:

```text
fixed circuit
evolved stored-power controller
zero-store controller
shuffled-signal stored-power controller
time-shift stored-power controller
```

## Required outputs

```text
S_initial
S_final
S_min
S_max
external_supply_added
controller_energy_spent
controller_starved_cycles
zero_store_action_check
W_resource
W_no_resource
resource_attributable_W
restart_recovery_score
energy/accounting residual
```

## Stop or fail conditions

```text
S does not increase under supply
S does not decrease under action
controller emits dynamic action when S is zero
supply stop does not reduce available action
supply restart does not restore available action in a region that worked before
apparent gain comes only from lowering W_no_resource
shuffled/time-shift controls match the evolved controller
energy/accounting residual exceeds tolerance
```

## Claim ceiling

Allowed if supported:

```text
In this explicit model, local controller action is gated by a finite internal
store that fills under supply, depletes under action, stops action when empty,
and supports output recovery when supply resumes.
```

Not allowed:

```text
real thermodynamic work
complete actuator physics
metabolism
homeostasis
life
agency
quantum advantage
```

## Cloud review

Review prompt:

```text
docs/qcell/Q_CELL_STORED_POWER_ACTUATOR_CLOUD_REVIEW_PROMPT_20260710.md
```

Do not run the GPU experiment until the review has been considered or the user
explicitly asks to proceed without it.

