# Protocol: quantum_homeostatic_parts_observation_v1_pulse_map

Date: 2026-07-08

## Question

Can the observed part-part negativity be separated into spatial attenuation and temporal pulse propagation?

v0 showed:

```text
direct_entangling_parts creates M-C / C-R / R-W negativity pulses
field_only_parts keeps pair negativity at zero
```

v1 asks the next observation question:

```text
Do negativity pulses rise in a time-shifted sequence along M-C -> C-R -> R-W, or do all links light up together because the whole-field acts globally?
```

## Layer

```text
QUANTUM_OBSERVATION
```

## Stance

This is an observation map, not a PASS/FAIL test.

The key is not just how strong each pair becomes. The key is when each pair becomes strong.

## Profiles

```text
left_to_right_wave:
  expected pulse order M-C -> C-R -> R-W

simultaneous_burst:
  expected near-simultaneous pulse onset/peak

right_to_left_wave:
  expected pulse order R-W -> C-R -> M-C

double_pulse_wave:
  two load pulses arranged to test whether the left-to-right trace reappears under repeated disturbance
```

## Coupling scales

```text
weak
medium
strong
```

## Controls

```text
direct_entangling:
  part-part coupling is present

field_only:
  same whole-field timing but no part-part coupling
```

## Observables

For each scenario:

```text
M-C negativity time series
C-R negativity time series
R-W negativity time series
peak time per pair
onset time per pair
offset time per pair
duration above threshold
peak lag: C-R minus M-C
peak lag: R-W minus C-R
onset lag: C-R minus M-C
onset lag: R-W minus C-R
compact negativity raster
```

## Run command

```bash
python scripts/quantum_observation/quantum_homeostatic_parts_observation_v1_pulse_map.py \
  --seed 20260708 \
  --steps 120 \
  --out data/quantum_observation/quantum_homeostatic_parts_observation_v1_pulse_map_seed20260708.json \
  --summary-csv data/quantum_observation/quantum_homeostatic_parts_observation_v1_pulse_map_seed20260708_summary.csv \
  --trace-csv data/quantum_observation/quantum_homeostatic_parts_observation_v1_pulse_map_seed20260708_compact_trace.csv
```

## Observation boundary

This run records pulse timing. It does not try to prove an advantage or promote a hardware claim.

The saved distinction is:

```text
spatial attenuation = which pair is stronger
temporal propagation = when each pair peaks
```
