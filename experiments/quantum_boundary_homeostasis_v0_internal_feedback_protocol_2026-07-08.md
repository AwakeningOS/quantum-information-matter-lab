# Protocol: quantum_boundary_homeostasis_v0_internal_feedback

Date: 2026-07-08

## Question

Can a quantum-coupled boundary protect an internal state from external disturbance while still allowing exchange?

This starts a new boundary-homeostasis line on top of the previous M/C/R/W observation line.

## Layer

```text
QUANTUM_OBSERVATION
```

## Stance

This is an observation model, not a PASS/FAIL test.

The goal is to watch whether a boundary behaves like a homeostatic self-boundary rather than an external-stimulus mirror.

## Core distinction

The main arm uses internal negative feedback:

```text
internal_error =
  internal_toxicity - toxicity_target
+ internal_pressure - pressure_target
+ resource_target - internal_resource
```

The boundary M changes from this internal error, not from external toxicity alone.

## Arms

```text
coherent_internal_feedback:
  internal state tilts boundary gates without an explicit measurement/backaction event

measurement_internal_feedback:
  internal state is sensed through a measurement-like channel that leaves bias/fatigue

external_reactive_boundary:
  boundary reacts to external toxicity/pressure directly

open_boundary:
  boundary stays open

overclosed_boundary:
  boundary stays mostly closed

wrong_target_boundary:
  boundary uses the wrong internal target setpoint
```

## Primary metrics

```text
target_range_fraction
resource_intake_fraction
boundary_work_rate
efficiency_factor
homeostasis_balance = target_range_fraction * resource_intake_fraction * efficiency_factor
internal_external_gradient_mean
unnecessary_closure_rate
internal_state_sensitivity
same_external_response_delta
fatigue_final
bias_final
negativity pulse lags M-C -> C-R -> R-W
```

## Why balance matters

A fully closed boundary can protect the interior but starves exchange.
An open boundary exchanges but fails to protect.
A homeostatic boundary must do both.

## Run command

```bash
python scripts/quantum_observation/quantum_boundary_homeostasis_v0_internal_feedback.py \
  --seed 20260708 \
  --out data/quantum_observation/quantum_boundary_homeostasis_v0_internal_feedback_seed20260708.json \
  --summary-csv data/quantum_observation/quantum_boundary_homeostasis_v0_internal_feedback_seed20260708_summary.csv \
  --trace-csv data/quantum_observation/quantum_boundary_homeostasis_v0_internal_feedback_seed20260708_selected_trace.csv
```

## Observation boundary

This run records boundary-homeostasis trajectories.

It does not try to prove an advantage or promote a hardware claim. The useful distinction is whether protection comes from internal negative feedback while preserving exchange, rather than from fixed closure or direct external reaction.
