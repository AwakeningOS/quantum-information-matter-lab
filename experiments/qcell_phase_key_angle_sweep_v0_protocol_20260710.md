# Q-cell phase-key angle sweep v0 protocol

Date: 2026-07-10 JST

## Question

The first phase-key readout showed a tiny quantum-only residual after
same-population diagonal-shadow subtraction. This sweep asks whether that
residual has the expected key-angle structure.

## Design

Prep:

```text
120 cycles
resource on
no W readout during prep
```

Readout:

```text
80 cycles
resource off
branch from the same prepared state
```

Arms:

```text
quantum
classical
full_dephase
```

Keys:

```text
angle_key
phase_shuffled_angle_key
```

Angle multipliers:

```text
-2.0 -1.5 -1.0 -0.5 0.0 0.5 1.0 1.5 2.0
```

Main metric:

```text
coherence_attributable_readout_W =
  readout_W(actual state) - readout_W(same-population diagonal shadow)
```

## Main Readout

Quantum angle key:

```text
angle -2.0: +0.000270, 60/60 positive
angle -1.5: +0.000553, 60/60 positive
angle -1.0: +0.000312, 60/60 positive
angle -0.5: -0.000296, 0/60 positive
angle  0.0:  0.000000, 0/60 positive
angle  0.5: +0.000296, 60/60 positive
angle  1.0: -0.000312, 0/60 positive
angle  1.5: -0.000553, 0/60 positive
angle  2.0: -0.000270, 0/60 positive
```

Phase-shuffled quantum key was near null and sign-incoherent. Classical and
full-dephase arms were zero for every angle after diagonal-shadow subtraction.

## Interpretation

The signal is still small, but it now has the expected identity checks:

```text
only quantum has nonzero residual
angle changes flip the sign
all seeds agree at the main positive/negative lobes
phase shuffle breaks the curve
classical/full_dephase remain zero
```

Allowed claim:

```text
This supports a small model-level phase-key readout signal: quantum-retained
off-diagonal structure produces an angle-dependent W residual after population
routing is subtracted.
```

Limit:

```text
effect size remains tiny compared with population-routed W
not quantum advantage
not a physical energy claim
```
