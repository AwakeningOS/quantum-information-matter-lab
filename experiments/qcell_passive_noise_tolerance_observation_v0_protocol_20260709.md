# Q-cell passive noise tolerance observation v0 protocol

Date: 2026-07-09
Layer: QUANTUM_OBSERVATION
Status: OBSERVATION_LOG
Experiment: `qcell_passive_noise_tolerance_observation_v0`

## Purpose

Observe whether any structure/encoding passively preserves quantum information longer under noise.

This protocol excludes recovery, measurement feedback, external resource supply, mid-run reinitialization, pure-state injection, and error-correction operations.

Do not use life, self-repair, homeostasis, PASS/FAIL, or ranking language.

## Structures

```text
A: single part
B: two-part normal encoding
C: two-part symmetric encoding
D: three-part chain
E: four-part chain
F: four-part ring
```

C uses:

```text
|0L> = |01>
|1L> = |10>
|+L> = (|01> + |10>) / sqrt(2)
```

A/B/D/E/F use comparable two-state encodings with 0L, 1L, and +L states.

## Noise channels

```text
collective_dephase
independent_dephase
asymmetric_dephase
collective_depolarizing
independent_depolarizing
```

Strengths:

```text
p = 0.00, 0.01, 0.03, 0.06, 0.10, 0.18, 0.30
```

Checkpoints:

```text
0, 1, 2, 5, 10, 20, 50, 100
```

## Seed mode

This run uses exact deterministic CPTP channel maps, not stochastic noise sampling.

The requested seed dimension is retained as exact replicas:

```text
20260710, 20260711, 20260712
```

Seed variation is therefore zero by construction. This records expected channel trajectories rather than Monte Carlo paths.

## Saved quantities

```text
complete density matrix at checkpoints
logical-state fidelity
logical coherence
whole-system l1 coherence
purity
von Neumann entropy
basis population
all pair ZZ
all pair negativity
trace distance from initial state
trace distance from maximally mixed state
```

Logical coherence is recorded separately from whole-system l1 coherence.

## Required comparisons

```text
single part vs symmetric encoding
collective noise vs independent noise
chain vs ring
noise-free condition
ordinary movement toward maximally mixed state
|+L> under collective dephase
|+L> under independent dephase
```

## Exact wording constraint

If C |+L> remains under collective dephase, write only:

```text
encoded information remained passively under a specific common-action noise channel
```

Do not write:

```text
general noise resistance
life
repair
homeostasis
```
