# Cloud review prompt - Q-cell stored-power actuator v0

We are planning the next Q-cell experiment.

Please review the design before local GPU implementation.

## Background

Previous completed results:

```text
1. External resource input can affect W output.
2. A local-state controller improves output over a fixed circuit in selected regions.
3. A small trial-and-error parameter search improved that controller on held-out seeds.
4. Conservative post-hoc controller-cost accounting still left QFCBM_0988 positive.
5. A finite controller reservoir M test showed QFCBM_0988 remains positive when dynamic controller action is limited by a depleting controller budget.
```

But the following is not yet established:

```text
internal stored power accumulates
controller action spends that stored power
stored power depletion stops action
renewed supply restores action
```

## Next target

Test a model-level stored-power actuator:

```text
external supply -> internal store -> controller action -> store decreases
store empty -> controller action stops
supply resumes -> store refills -> action resumes
```

This is still a model-level accounting test, not a claim of real thermodynamic work.

## Proposed minimum experiment

Primary grid:

```text
QFCBM_0988
```

Optional secondary checks:

```text
QFCBM_0496
QFCBM_0399
```

Initial minimal conditions:

```text
supply_always_on
supply_never_on
supply_stop_midway
supply_restart_after_stop
internal_store_initial_zero
internal_store_initial_positive
```

Measure:

```text
internal_store_energy
external_supply_in
controller_energy_spent
controller_starved_cycles
resource_attributable_W
W_resource
W_no_resource
store_final
store_min
store_max
restart_recovery
zero_store_action_check
energy/accounting residual
```

## Questions for review

Please answer directly and practically:

1. What controls are missing?
2. What should count as failure?
3. What is the minimum condition set for a first local GPU run?
4. What must be measured to avoid a fake "stored power" claim?
5. What is the strongest allowed claim if it works?
6. What claims must still be forbidden?
7. What would a skeptical reviewer attack first?

## Hard claim limits

Do not allow claims of:

```text
life
metabolism
agency
homeostasis
quantum advantage
complete physical thermodynamics
real work reservoir
```

Allowed claim should stay near:

```text
In this explicit model, controller action is gated by an internal finite store:
the store fills under supply, depletes under action, stops action when empty,
and supports output recovery when supply resumes.
```

