# Q-cell stored-power actuator v0 protocol

Date: 2026-07-10 JST

Status: executed on QFCBM_0988 minimum condition set.

## Purpose

Test whether the next Q-cell controller can be tied to an internal stored-power
state variable rather than a free, purely external, or post-hoc accounting
budget.

Core question:

```text
Can model-level stored power fill under supply, be spent by controller action,
stop action when empty, and support output recovery when supply resumes?
```

The central causal requirement is:

```text
store_before_action must decide whether controller action is allowed.
```

The experiment must not explain `store` after observing `W`.

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

Predeclared update rule:

```text
S[t+1] =
  clamp(
    S[t]
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
  controller_action_requested[t] and S_before_action[t] >= action_cost
```

If action cost is only partially payable, the v0 implementation must choose one
policy before running:

```text
strict gate: insufficient S means zero dynamic action
```

Do not choose the policy after seeing output.

## Minimal conditions

Run first on `QFCBM_0988` only.

```text
supply_never_on + initial_store_zero
supply_always_on + initial_store_zero
supply_stop_midway + initial_store_zero
supply_restart_after_stop + initial_store_zero
supply_never_on + initial_store_positive
```

Controller/control families:

```text
fixed circuit
evolved stored-power controller
zero-store controller
shuffled-signal stored-power controller
time-shift stored-power controller
store-shuffle controller
supply-label-only controller
equal-total-supply timing controls
no-controller-drain control
```

## Required outputs

```text
S_initial
S_final
S_min
S_max
S_before_action_cyclewise
S_after_action_cyclewise
external_supply_added
controller_energy_spent
controller_starved_cycles
controller_action_requested
controller_action_allowed
zero_store_action_check
W_resource
W_no_resource
resource_attributable_W
restart_recovery_score
energy/accounting residual
```

Required cyclewise trace fields:

```text
t
seed
condition
supply_on
external_supply_in[t]
store_before_action[t]
controller_action_requested[t]
controller_action_allowed[t]
controller_energy_spent[t]
store_after_action[t]
controller_starved[t]
W_resource[t]
W_no_resource[t]
resource_attributable_W[t]
accounting_residual[t]
```

## Stop or fail conditions

```text
S does not increase under supply
S does not decrease under action
controller emits dynamic action when S is zero
controller action fires while controller_energy_spent is zero
supply_never_on + initial_store_zero sustains action
supply stop does not reduce available action
supply restart does not restore available action in a region that worked before
apparent gain comes only from lowering W_no_resource
shuffled/time-shift controls match the evolved controller
store-shuffle control matches the real store trace
supply-label-only control recovers without store filling
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
docs/qcell/Q_CELL_STORED_POWER_ACTUATOR_CLOUD_REVIEW_RESPONSE_20260710.md
```

The review was incorporated before execution.

## Execution record

```text
script = scripts/quantum_observation/qcell_stored_power_actuator_v0_gpu.py
postprocess = scripts/quantum_observation/qcell_stored_power_actuator_v0_postprocess.py
grid = QFCBM_0988
seeds = 60
conditions = 5
cycle rows = 60000
kappa = 0.03
store_capacity = 1.0
supply_gain = 0.08
gate_policy = strict
```

Compact committed outputs:

```text
data/quantum_observation/qcell_stored_power_actuator_v0_condition_summary.csv
data/quantum_observation/qcell_stored_power_actuator_v0_window_summary.csv
data/quantum_observation/qcell_stored_power_actuator_v0_manifest.json
results/qcell_stored_power_actuator_v0_report_2026-07-10.md
```

Full cycle trace remains local:

```text
/home/youthk/work/qcell_experiment_outputs/qcell_stored_power_actuator_v0_outputs/qcell_stored_power_actuator_v0_cycle_trace.csv
```

Minimum-run integrity checks:

```text
zero-store action violations = 0
action-without-spend violations = 0
insufficient-store action violations = 0
max accounting residual = 5.285e-14
```
