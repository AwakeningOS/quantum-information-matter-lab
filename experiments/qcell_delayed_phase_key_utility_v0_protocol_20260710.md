# Q-cell delayed phase-key utility v0 protocol

Date: 2026-07-10 JST

## Question

Can the delayed phase-key residual carry a small recoverable phase bit, rather
than merely exist as a tiny observable residual?

## Design

Encode:

```text
100 cycles
resource on
label plus/minus encoded as a C-D phase-only mark
```

Delay:

```text
50 cycles
resource off
internal dynamics and noise continue
```

Readout:

```text
80 cycles
phase-key readout
same-population diagonal-shadow subtraction
```

Arms:

```text
quantum
classical
full_dephase
phase_shuffled quantum control
```

Angles:

```text
-1.5 -1.0 1.0 1.5
```

## Result

Quantum angle-key readout separates the labels with a tiny but seed-consistent
margin:

```text
angle -1.0:
  oriented classification = 1.0
  mean abs plus/minus margin = 0.000000043
  counts plus/minus/tie = 0/60/0

angle 1.0:
  oriented classification = 1.0
  mean abs plus/minus margin = 0.000000043
  counts plus/minus/tie = 0/60/0
```

Controls:

```text
classical = tie/no signal, 0.5
full_dephase = tie/no signal, 0.5
phase_shuffled quantum = near random, 0.466667 to 0.633333
```

Allowed claim:

```text
The delayed phase-key residual carries a tiny model-level phase bit in the
quantum arm. The bit is not recoverable from classical transport or full
dephasing, and phase shuffling largely destroys the usable label relation.
```

Limit:

```text
effect size is extremely small
this is not quantum advantage
this is not a physical memory or energy claim
```
