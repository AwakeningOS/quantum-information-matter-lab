# Q-cell repair actuator audit v0 protocol

Date: 2026-07-10 JST

Status: protocol draft.

## Purpose

Audit candidate structure-maintenance actuators before using them in a
structure-cost experiment.

The previous prototype was halted because its nonunitary repair blend changed
internal energy. This audit prevents promoting a dirty repair actuator.

## Question

```text
Can a repair actuator improve quantum-structure readouts while leaving internal
energy and population distribution effectively unchanged?
```

## Candidate actuators

```text
population_fixed_offdiag_restore
phase_only_alignment
degenerate_subspace_unitary
```

## Required checks

For each candidate, log:

```text
trace_error
hermiticity_error
min_eigenvalue
energy_delta
diag_l1_delta
coherence_delta
negativity_delta
phase_alignment_delta
store_delta
structure_cost
```

## Minimum pass rule

```text
trace_error <= 1e-10
hermiticity_error <= 1e-10
min_eigenvalue >= -1e-10
abs(energy_delta) <= 1e-10
diag_l1_delta <= 1e-10
store_delta = -structure_cost
coherence_delta > 0 or phase_alignment_delta > 0 or negativity_delta > 0
```

## Claim ceiling

Passing this audit only says:

```text
the actuator is accounting-clean enough for the next model-level experiment
```

It does not establish physical thermodynamic work, real repair, metabolism,
homeostasis, quantum advantage, or a QPU result.
