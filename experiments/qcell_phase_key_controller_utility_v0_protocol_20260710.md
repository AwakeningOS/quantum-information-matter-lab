# Q-cell phase-key controller utility v0 protocol

Date: 2026-07-10 JST

## Question

Can the delayed phase-key residual be used as a small downstream branch-control
signal?

## Design

Input:

```text
qcell_delayed_phase_key_utility_v0 seed summary
```

Train/test split:

```text
first 30 seeds: learn residual orientation
last 30 seeds: test branch selection
```

Branch rule:

```text
choose plus/minus branch from the sign ordering of phase-key residuals
```

Baselines:

```text
random = 0.5
oracle = 1.0
classical/dephase no-signal = 0.5
phase-shuffle control
```

## Result

Quantum angle-key controller:

```text
angle -1.5: test accuracy = 1.0
angle -1.0: test accuracy = 1.0
angle  1.0: test accuracy = 1.0
angle  1.5: test accuracy = 1.0
```

Controls:

```text
classical = 0.5 no signal
full_dephase = 0.5 no signal
phase_shuffled quantum = 0.466667 to 0.633333
```

Allowed claim:

```text
In this model, the delayed phase-key residual can be used as a tiny downstream
branch-control signal in the quantum arm.
```

Limit:

```text
The margin is around 2e-8 to 4e-8, so this is a small model-level utility
signal only. It is not a robust macroscopic control effect, quantum advantage,
or physical memory claim.
```
