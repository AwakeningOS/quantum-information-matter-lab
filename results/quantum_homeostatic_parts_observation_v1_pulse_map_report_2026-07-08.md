# Observation: quantum_homeostatic_parts_observation_v1_pulse_map

Status: OBSERVATION_LOG  
Generator script: `scripts/quantum_observation/quantum_homeostatic_parts_observation_v1_pulse_map.py`  
Raw log: `data/quantum_observation/quantum_homeostatic_parts_observation_v1_pulse_map_seed20260708.json`  
Summary CSV: `data/quantum_observation/quantum_homeostatic_parts_observation_v1_pulse_map_seed20260708_summary.csv`  
Compact trace CSV: `data/quantum_observation/quantum_homeostatic_parts_observation_v1_pulse_map_seed20260708_compact_trace.csv`  
Run command: `python scripts/quantum_observation/quantum_homeostatic_parts_observation_v1_pulse_map.py --seed 20260708 --steps 120 --out data/quantum_observation/quantum_homeostatic_parts_observation_v1_pulse_map_seed20260708.json --summary-csv data/quantum_observation/quantum_homeostatic_parts_observation_v1_pulse_map_seed20260708_summary.csv --trace-csv data/quantum_observation/quantum_homeostatic_parts_observation_v1_pulse_map_seed20260708_compact_trace.csv`  
Layer: QUANTUM_OBSERVATION

## What changed from v0

v0 recorded that direct part-part coupling creates pair-negativity pulses while field-only coupling does not.

v1 separates two things that were mixed in v0's max-negativity summary:

```text
spatial attenuation = which pair gets stronger
temporal propagation = when each pair rises or peaks
```

So v1 records, for each M-C / C-R / R-W pair:

```text
peak time
peak value
onset time
offset time
duration above threshold
pair-to-pair peak lag
pair-to-pair onset lag
compact negativity raster
```

## Profiles

```text
left_to_right_wave
simultaneous_burst
right_to_left_wave
double_pulse_wave
```

Each direct-entangling profile is run at:

```text
weak
medium
strong
```

Field-only controls are run at medium scale and keep pair negativity at zero.

## Main medium-scale observations

| Mode | Profile | M-C peak t/value | C-R peak t/value | R-W peak t/value | Peak lag C-R minus M-C | Peak lag R-W minus C-R | Label |
|---|---|---:|---:|---:|---:|---:|---|
| direct_entangling | left_to_right_wave | 32 / 0.069180405344 | 56 / 0.031486878512 | 74 / 0.025019349203 | 24 | 18 | left_to_right_peak_travel |
| direct_entangling | simultaneous_burst | 54 / 0.065525157382 | 55 / 0.047518386948 | 54 / 0.031339737403 | 1 | -1 | near_simultaneous_peaks |
| direct_entangling | right_to_left_wave | 75 / 0.079669134216 | 58 / 0.048731564142 | 32 / 0.016744293428 | -17 | -26 | right_to_left_peak_travel |
| direct_entangling | double_pulse_wave | 29 / 0.071762802615 | 52 / 0.030278827516 | 70 / 0.026050997304 | 23 | 18 | left_to_right_peak_travel |
| field_only | left_to_right_wave | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 | no pair negativity |

## What the lags show

The left-to-right condition does not merely show weaker values farther down the chain. It shows time-ordering:

```text
M-C peak time = 32
C-R peak time = 56
R-W peak time = 74
```

with lags:

```text
C-R minus M-C = +24
R-W minus C-R = +18
```

The simultaneous condition shows near-zero lag:

```text
M-C peak time = 54
C-R peak time = 55
R-W peak time = 54
```

The right-to-left condition reverses the sign:

```text
R-W peak time = 32
C-R peak time = 58
M-C peak time = 75
```

So v1 separates these two readings:

```text
same-time activation = whole-field-like simultaneous drive
lagged activation = pulse travel along the part chain
```

## Raster reading

Medium left-to-right compact raster:

```text
░░░ ░░░ ░░░ ░░░ █░░ █░░ █░░ █░░ █░░ █░░ █▒░ ▒▒░ ░▒░ ░▒░ ░▒░ ░▒▒ ░▒▒ ░░▒ ░░▒ ░░▒ ░░▒ ░░░ ░░░ ░░░ ░░░ ░░░ ░░░ ░░░ ░░░ ░░░
```

Medium simultaneous compact raster:

```text
░░░ ░░░ ░░░ ░░░ ░░░ ░░░ ░░░ ░░░ ░░░ ░▒▒ ███ ███ ███ ███ ███ █▒▒ ▒▒▒ ▒▒░ ░░░ ░░░ ░░░ ░░░ ░░░ ░░░ ░░░ ░░░ ░░░ ░░░ ░░░ ░░░
```

Medium right-to-left compact raster:

```text
░░░ ░░░ ░░░ ░░░ ░░░ ░░▒ ░░▒ ░▒▒ ░▒▒ ░▒▒ ░▒░ ░▒░ ░▒░ ░▒░ ▒▒░ ▒▒░ ▒▒░ ▒░░ █░░ █░░ █░░ █░░ ▒░░ ░░░ ░░░ ░░░ ░░░ ░░░ ░░░ ░░░
```

The raster now has the thing v0 did not preserve: directionality over time.

## Observation

The same spatial ordering of links can support different temporal stories:

```text
left-to-right profile: M-C -> C-R -> R-W
simultaneous profile: M-C / C-R / R-W together
right-to-left profile: R-W -> C-R -> M-C
double-pulse profile: left-to-right trace reappears under repeated disturbance
```

This means the earlier v0 max table was incomplete. Max values showed spatial attenuation, but v1 shows whether that attenuation is accompanied by propagation lag.

## Next observation

```text
quantum_homeostatic_parts_observation_v2_causal_touch_response:
  perturb one part locally while the whole-field is held fixed or slowly varying
  watch whether pair negativity and activation changes propagate through neighboring links
  compare local touch response against global-field-only drive
```

The next question is whether touching one part produces a local-to-global response, rather than merely replaying a pre-shaped field pulse.
