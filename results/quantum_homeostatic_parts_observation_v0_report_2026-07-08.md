# Observation: quantum_homeostatic_parts_observation_v0

Status: OBSERVATION_LOG  
Generator script: `scripts/quantum_observation/quantum_homeostatic_parts_observation_v0.py`  
Raw log: `data/quantum_observation/quantum_homeostatic_parts_observation_v0_seed20260708.json`  
Summary CSV: `data/quantum_observation/quantum_homeostatic_parts_observation_v0_seed20260708_summary.csv`  
Run command: `python scripts/quantum_observation/quantum_homeostatic_parts_observation_v0.py --seed 20260708 --steps 180 --out data/quantum_observation/quantum_homeostatic_parts_observation_v0_seed20260708.json --csv data/quantum_observation/quantum_homeostatic_parts_observation_v0_seed20260708_trajectory.csv --summary-csv data/quantum_observation/quantum_homeostatic_parts_observation_v0_seed20260708_summary.csv`  
Layer: QUANTUM_OBSERVATION

## What was built

This run watches four parts as a single 4-qubit density matrix:

```text
M = membrane
C = conversion / catalyst
R = recycler
W = waste outlet
```

The parts are immersed in three whole-field variables:

```text
energy
toxicity
pressure
```

The direct version adds field-modulated entangling gates:

```text
M -- C -- R -- W
```

implemented as weak partial-iSWAP gates on:

```text
M-C
C-R
R-W
```

plus a weak M-W phase thread.

## Variants

```text
direct_entangling_parts:
  whole-field local rotations + field-modulated direct entangling gates

field_only_parts:
  same whole-field local rotations and feedback, but no direct entangling gates

constant_entangling_parts:
  whole-field local rotations + fixed-strength direct entangling gates
```

## Main observation table

| Variant | neg_M_C max | neg_C_R max | neg_R_W max | frac M-C > .005 | frac C-R > .005 | frac R-W > .005 | energy/neg_M-C corr | energy/neg_C-R corr | energy/neg_R-W corr |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| direct_entangling_parts | 0.126998385 | 0.095496553 | 0.043610747 | 0.133333333 | 0.116666667 | 0.066666667 | 0.647824902 | 0.535590200 | 0.456004405 |
| field_only_parts | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| constant_entangling_parts | 0.216683639 | 0.021194988 | 0.058936607 | 0.138888889 | 0.027777778 | 0.138888889 | 0.658472118 | 0.244143702 | 0.672728012 |

## What appeared

The direct-entangling version produced visible pair-negativity pulses:

```text
M-C max negativity = 0.126998385
C-R max negativity = 0.095496553
R-W max negativity = 0.043610747
```

The field-only version produced none:

```text
M-C max negativity = 0
C-R max negativity = 0
R-W max negativity = 0
```

That cleanly separates these two cases:

```text
parts only reading the same classical field
parts directly connected by quantum gates
```

## The important shape

The direct version did not behave like a simple load meter.

Toxicity and pressure increase the entangling angles, but they also increase dephasing. In this run, the strongest negativity pulses appeared in high-energy / lower-dissipation windows:

```text
direct corr energy -> neg_M_C = 0.647824902
direct corr energy -> neg_C_R = 0.535590200
direct corr energy -> neg_R_W = 0.456004405
```

while toxicity and pressure were negatively correlated with M-C negativity:

```text
direct corr toxicity -> neg_M_C = -0.245447107
direct corr pressure -> neg_M_C = -0.268154870
```

So the observed pattern is not merely:

```text
more pressure = more entanglement
```

It is closer to:

```text
coupling tries to bind the parts together
load-driven dephasing tries to dissolve the bond
the visible negativity is the pulse left by that tug-of-war
```

## Reading the run

The useful object is the time-aligned trajectory:

```text
field values
part activations
coupling strengths
pair negativities
ZZ covariances
activation raster
```

The summary says that direct M-C / C-R / R-W coupling creates actual pair negativity, while field-only coupling does not. The constant-coupling comparison shows that merely adding a fixed quantum thread is not the same as making the thread breathe with the whole-field.

## Observation boundary

This is not a winner/loser test.

This run records a trajectory. The saved question is:

```text
when the whole-field changes, where do the part-part quantum correlations rise, fade, and move?
```

## Next observation

```text
quantum_homeostatic_parts_observation_v1_pulse_map:
  keep the same M-C-R-W density matrix
  sweep pulse shapes and coupling strengths
  output a compact raster of negativity pulses
  track whether pulses move from M-C to C-R to R-W as toxicity/pressure waves travel through the system
```
