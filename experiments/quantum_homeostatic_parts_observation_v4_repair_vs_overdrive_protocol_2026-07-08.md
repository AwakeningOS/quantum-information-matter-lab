# Protocol: quantum_homeostatic_parts_observation_v4_repair_vs_overdrive

Date: 2026-07-08

## Question

When active recovery becomes stronger, does it remain healthy repair, become damped oscillatory repair, or cross into overdrive / exhausted repair?

This follows:

```text
v0 = direct links create pair-negativity pulses
v1 = peak/onset lags separate propagation from simultaneous drive
v2 = local touch creates a local-to-neighbor response
v3 = repeated touch shows cross-touch state memory
v4 = recovery strength asks where repair turns into overdrive
```

## Layer

```text
QUANTUM_OBSERVATION
```

## Stance

This is an observation model, not a PASS/FAIL test.

The important discipline is that labels are assigned mechanically from predeclared trajectory metrics, not by looking at the plot afterward.

## Recovery modes

```text
weak_recovery
gentle_recovery
strong_recovery
oscillatory_recovery
extreme_recovery
full_reset_baseline
```

## Touch types

```text
unitary_touch
measurement_touch
```

## Conditions

```text
high_energy
high_toxicity
```

## Mechanical labels

### stable_repair

```text
0.75 <= response_ratio_last_over_first <= 1.10
overshoot_max <= 0.15
state_distance_last <= 0.25
oscillation_envelope_ratio <= 1.10
fatigue_last <= 0.20
bias_last <= 0.12
```

### damped_oscillatory_repair

```text
overshoot_max > 0.15
oscillation_envelope_ratio < 0.90
state_distance_last <= 0.15
fatigue_last <= 0.30
```

### overdrive

```text
overshoot_max >= 0.30 with growing oscillation
or state_distance_last >= 0.75
or response_ratio_last_over_first >= 1.25 while fatigue/bias also increase
```

### collapse_or_exhausted_repair

```text
response_ratio_last_over_first <= 0.20
coherence_last <= 0.20
fatigue_last >= 0.30
```

## Recorded metrics

```text
response_ratio_last_over_first
overshoot_max
state_distance_first
state_distance_last
oscillation_envelope_ratio
coherence_first / last
bias_first / last
fatigue_first / last
mechanical_label
```

## Run command

```bash
python scripts/quantum_observation/quantum_homeostatic_parts_observation_v4_repair_vs_overdrive.py \
  --seed 20260708 \
  --out data/quantum_observation/quantum_homeostatic_parts_observation_v4_repair_vs_overdrive_seed20260708.json \
  --summary-csv data/quantum_observation/quantum_homeostatic_parts_observation_v4_repair_vs_overdrive_seed20260708_summary.csv \
  --touch-csv data/quantum_observation/quantum_homeostatic_parts_observation_v4_repair_vs_overdrive_seed20260708_selected_touch_rows.csv
```

## Observation boundary

This run records repair / overdrive trajectories.

It does not try to prove an advantage or promote a hardware claim. The useful question is whether recovery strength produces convergent, damped, runaway, or exhausted trajectories under predeclared state metrics.
