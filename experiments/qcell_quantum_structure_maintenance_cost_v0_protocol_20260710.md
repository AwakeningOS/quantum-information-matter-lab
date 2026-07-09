# Q-cell quantum structure maintenance cost v0 protocol

Date: 2026-07-10 JST

Status: draft protocol + prototype runner; smoke-tested only, not promoted.

## Purpose

Test, inside the explicit Q-cell model, whether maintaining quantum structure
can consume a shared model store and reduce the resource available for W output.

This is not a physical thermodynamic proof.

## Core question

```text
Does preserving coherence/link structure draw from the same model budget that
could otherwise support W output?
```

## First minimum run

```text
grid = QFCBM_0988
seeds = 60
cycles = 200
supply schedule = always on
resource = R3_pure_1
noise = N4_dephase_plus_amplitude_damping, p = 0.06
```

## Prototype warning

The first prototype runner exists, but the repair actuator is not yet accepted
as a clean ledger experiment. A smoke run showed the expected qualitative
pattern but also exposed an accounting issue:

```text
repair is implemented as a convex blend toward the pre-noise state
that nonunitary repair can move internal energy
therefore physical energy residual and store residual must remain separated
do not promote full results until the repair actuator ledger is tightened
```

Current safe status:

```text
protocol/design target only
prototype runner only
no full GPU result claim
```

Next required audit before full run:

```text
experiments/qcell_repair_actuator_audit_v0_protocol_20260710.md
```

The repair actuator must pass energy/population preservation checks before it
can be used to support a structure-maintenance-cost claim.

## Arms

```text
quantum_no_repair
quantum_repair_shared_store
quantum_repair_free
fake_charge_no_repair
classical_probability_transport
diag_same_population_shadow
```

## Predeclared model accounting

```text
store_after_supply =
  clamp(store_before_cycle + supply_gain * external_supply_in, 0, store_capacity)

structure_loss =
  offdiag_distance(rho_pre_noise, rho_post_noise)

structure_repaired =
  offdiag_distance(rho_post_repair, rho_post_noise)

structure_cost =
  structure_cost_rate * structure_repaired

store_after_repair =
  store_before_repair - structure_cost
```

The W output actuator also draws from the same store:

```text
W_action_cost = output_cost_rate * abs(output_angle)
W_action_scale = min(1, store_before_W / W_action_cost)
```

This makes the first test a model-level shared-budget competition:

```text
structure maintenance vs W output
```

## Required readouts

```text
store_before_cycle
store_after_supply
coherence_pre_noise
coherence_post_noise
coherence_post_repair
negativity_pre_noise
negativity_post_noise
negativity_post_repair
structure_loss
structure_repaired
structure_cost
store_before_W
store_after_W
W_quantum_actual
W_diag_same_population
accounting_residual_with_structure_cost
```

## Success pattern

```text
quantum_repair_shared_store:
  structure_repaired > 0
  structure_cost > 0
  store decreases
  W decreases relative to free repair / diag shadow

quantum_repair_free:
  structure_repaired > 0
  store does not pay structure_cost

fake_charge_no_repair:
  store decreases
  structure_repaired = 0

classical_probability_transport:
  structure_cost = 0
  coherence/negativity = 0
```

## Claim ceiling

Allowed if supported:

```text
In this explicit model, maintaining quantum structure consumes a shared model
store and competes with W output.
```

Not allowed:

```text
physical thermodynamic work
real energy used to maintain quantum structure
metabolism/homeostasis/life/agency
quantum advantage
QPU result
```
