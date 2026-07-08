# Protocol: quantum_homeostatic_parts_observation_v3_recovery_cycle

Date: 2026-07-08

## Question

When the same part is touched repeatedly, does the part-part negativity response recover, fatigue, saturate, or habituate?

This follows:

```text
v0 = direct links create pair-negativity pulses
v1 = peak/onset lags separate propagation from simultaneous drive
v2 = local touch creates a local-to-neighbor response
v3 = repeated touch asks what carries across time
```

## Layer

```text
QUANTUM_OBSERVATION
```

## Stance

This is an observation model, not a PASS/FAIL test.

The purpose is to watch what accumulates between touches.

## Core design choice

Use active recovery as the main biological-style recovery model, while keeping passive recovery and full reset as controls.

```text
active_recovery:
  the system is pulled toward a homeostatic setpoint between touches

passive_recovery:
  the system is left to dephase / relax without active restoration

full_reset_baseline:
  the system is reset before every touch, so cross-touch memory is removed
```

## Touch types

```text
unitary_touch:
  a coherent local rotation-like touch; mostly reversible

measurement_touch:
  a non-reversible backaction-like touch; adds population bias and fatigue more strongly
```

## Conditions

```text
high_energy:
  recovery is easier and coherence can be restored

high_toxicity:
  recovery is harder and dephasing/fatigue accumulate more strongly
```

## Target

The default target is C, because it touches both M-C and C-R links and has an outer R-W link for spread.

## Recorded state variables

Each touch records pre-touch memory variables:

```text
pre_coherence_residual
pre_population_bias
pre_baseline_negativity
pre_fatigue_index
```

and response variables:

```text
peak_neg_M_C
peak_neg_C_R
peak_neg_R_W
mean_adjacent_peak
outer_peak
response_ratio_last_over_first
```

## Baseline logic

The key baseline is `full_reset_baseline`.

If the response decays only in non-reset modes, then the decay is carried by state variables that persist across touches. If reset also decays, the script itself is baking in habituation. The reset baseline should remain stable.

## Run command

```bash
python scripts/quantum_observation/quantum_homeostatic_parts_observation_v3_recovery_cycle.py \
  --seed 20260708 \
  --out data/quantum_observation/quantum_homeostatic_parts_observation_v3_recovery_cycle_seed20260708.json \
  --summary-csv data/quantum_observation/quantum_homeostatic_parts_observation_v3_recovery_cycle_seed20260708_summary.csv \
  --touch-csv data/quantum_observation/quantum_homeostatic_parts_observation_v3_recovery_cycle_seed20260708_touch_rows.csv
```

## Observation boundary

This run records repeated-touch recovery trajectories.

It does not try to prove an advantage or promote a hardware claim. The useful question is whether response changes across touches are carried by state variables, not by an explicit touch-count rule.
