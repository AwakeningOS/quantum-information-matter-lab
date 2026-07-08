# Protocol: quantum_homeostatic_parts_observation_v0

Date: 2026-07-08

## Question

Can four homeostatic parts be watched as one quantum-coupled trajectory while they are also immersed in a shared whole-field?

The parts are:

```text
M = membrane
C = conversion / catalyst
R = recycler
W = waste outlet
```

The whole-field is:

```text
energy
toxicity
pressure
```

## Layer

```text
QUANTUM_OBSERVATION
```

## Stance

This is an observation model, not a PASS/FAIL test.

The purpose is to see the time trajectory:

```text
field changes
part activations rise/fall
M-C / C-R / R-W entangling gates change strength
pair negativity appears/disappears
```

## Core addition

The model keeps the classical whole-field, but adds direct quantum coupling between parts:

```text
M -- C -- R -- W
```

At each step:

1. The whole-field changes local rotations for M, C, R, W.
2. Field-modulated partial-iSWAP gates couple M-C, C-R, and R-W.
3. A weak M-W phase thread is applied.
4. Mild dephasing and relaxation dissolve correlations over time.
5. The parts are read as activation probabilities and used to update the whole-field.
6. Pair negativity and ZZ covariance are logged on the same time axis.

## Variants

```text
direct_entangling_parts:
  local field rotations plus field-modulated M-C / C-R / R-W entangling gates

field_only_parts:
  local field rotations and whole-field feedback, but no direct entangling gates

constant_entangling_parts:
  local field rotations plus direct entangling gates with constant strength
```

## Observables

```text
energy, toxicity, pressure
act_M, act_C, act_R, act_W
theta_MC, theta_CR, theta_RW
neg_M_C, neg_C_R, neg_R_W, neg_M_W, neg_M_R, neg_C_W
zzcov_M_C, zzcov_C_R, zzcov_R_W, zzcov_M_W, zzcov_M_R, zzcov_C_W
activation raster
```

## Run command

```bash
python scripts/quantum_observation/quantum_homeostatic_parts_observation_v0.py \
  --seed 20260708 \
  --steps 180 \
  --out data/quantum_observation/quantum_homeostatic_parts_observation_v0_seed20260708.json \
  --csv data/quantum_observation/quantum_homeostatic_parts_observation_v0_seed20260708_trajectory.csv \
  --summary-csv data/quantum_observation/quantum_homeostatic_parts_observation_v0_seed20260708_summary.csv
```

## Outputs

```text
data/quantum_observation/quantum_homeostatic_parts_observation_v0_seed20260708.json
data/quantum_observation/quantum_homeostatic_parts_observation_v0_seed20260708_trajectory.csv
data/quantum_observation/quantum_homeostatic_parts_observation_v0_seed20260708_summary.csv
results/quantum_homeostatic_parts_observation_v0_report_2026-07-08.md
```

## Claim boundary

This run records a density-matrix observation trajectory.

It does not try to prove advantage or promote a hardware claim. The useful object is the saved trajectory itself: fields, activations, coupling strengths, and pair negativities on the same clock.
