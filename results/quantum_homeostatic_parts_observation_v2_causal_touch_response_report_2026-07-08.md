# Observation: quantum_homeostatic_parts_observation_v2_causal_touch_response

Status: OBSERVATION_LOG  
Generator script: `scripts/quantum_observation/quantum_homeostatic_parts_observation_v2_causal_touch_response.py`  
Raw log: `data/quantum_observation/quantum_homeostatic_parts_observation_v2_causal_touch_response_seed20260708.json`  
Summary CSV: `data/quantum_observation/quantum_homeostatic_parts_observation_v2_causal_touch_response_seed20260708_summary.csv`  
Compact trace CSV: `data/quantum_observation/quantum_homeostatic_parts_observation_v2_causal_touch_response_seed20260708_compact_trace.csv`  
Run command: `python scripts/quantum_observation/quantum_homeostatic_parts_observation_v2_causal_touch_response.py --seed 20260708 --steps 120 --touch-time 30 --out data/quantum_observation/quantum_homeostatic_parts_observation_v2_causal_touch_response_seed20260708.json --summary-csv data/quantum_observation/quantum_homeostatic_parts_observation_v2_causal_touch_response_seed20260708_summary.csv --trace-csv data/quantum_observation/quantum_homeostatic_parts_observation_v2_causal_touch_response_seed20260708_compact_trace.csv`  
Layer: QUANTUM_OBSERVATION

## What changed from v1

v1 asked whether a pre-shaped field/profile could create time-shifted negativity peaks.

v2 removes that dependence. It touches one part locally and asks whether the response spreads through neighboring links.

The distinction is:

```text
local touch response = one part is perturbed first
global field response = all links are driven together
field-only response = activations can move, but pair negativity stays zero
```

## Modes

```text
local_touch_direct:
  local kick to one part, with direct M-C / C-R / R-W links active

field_only_local_touch:
  same local kick, but no direct part-part links

global_field_pulse:
  no single-part touch; the whole-field moves all links together
```

## Fixed-field main observations

| Mode | Target | First touched-link peak | First next-link peak | Lag | Main link peaks | Label |
|---|---|---:|---:|---:|---|---|
| local_touch_direct | M | 35 | 48 | 13 | M-C 0.0811, C-R 0.0346, R-W 0.0135 | local_touch_spreads_to_next_link |
| local_touch_direct | C | 35 | 48 | 13 | M-C 0.0811, C-R 0.0665, R-W 0.0271 | local_touch_spreads_to_next_link |
| local_touch_direct | R | 35 | 48 | 13 | C-R 0.0665, R-W 0.0519, M-C 0.0422 | local_touch_spreads_to_next_link |
| local_touch_direct | W | 35 | 48 | 13 | R-W 0.0519, C-R 0.0346, M-C 0.0211 | local_touch_spreads_to_next_link |
| field_only_local_touch | M | n/a | n/a | 0 | M-C 0, C-R 0, R-W 0 | local_activation_without_pair_negativity |
| global_field_pulse | GLOBAL | 39 | 39 | 0 | M-C 0.045, C-R 0.045, R-W 0.045 | near_simultaneous_global_field_response |

## What the touch patterns show

### Touch M

Touching M first lights the adjacent M-C link, then C-R, then a weak R-W tail:

```text
M-C peak t/value = 35 / 0.0811
C-R peak t/value = 48 / 0.0346
R-W peak t/value = 61 / 0.0135
```

Compact raster:

```text
··· ··· ··· ··· ··· ··· ··· ··· ▒·· █·· █·· ▒·· ░▒· ·▒· ·▒· ··░ ··░ ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ···
```

### Touch C

Touching C lights both adjacent links first, then the outer R-W link:

```text
M-C peak t/value = 35 / 0.0811
C-R peak t/value = 35 / 0.0665
R-W peak t/value = 48 / 0.0271
```

Compact raster:

```text
··· ··· ··· ··· ··· ··· ··· ··· ▒▒· ██· ▒▒· ░▒· ·▒· ··░ ··░ ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ···
```

### Touch R

Touching R lights C-R and R-W first, then the outer M-C link:

```text
C-R peak t/value = 35 / 0.0665
R-W peak t/value = 35 / 0.0519
M-C peak t/value = 48 / 0.0422
```

Compact raster:

```text
··· ··· ··· ··· ··· ··· ··· ··· ·▒▒ ·██ ·▒▒ ·▒░ ░·· ░·· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ···
```

### Touch W

Touching W first lights R-W, then C-R, then a weaker M-C tail:

```text
R-W peak t/value = 35 / 0.0519
C-R peak t/value = 48 / 0.0346
M-C peak t/value = 61 / 0.0211
```

Compact raster:

```text
··· ··· ··· ··· ··· ··· ··· ··· ··▒ ··█ ··▒ ·▒░ ·▒· ░·· ░·· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ···
```

## Control readings

### Field-only local touch

The same local kick can move activation values, but pair negativity stays at zero:

```text
M-C peak value = 0
C-R peak value = 0
R-W peak value = 0
```

Compact raster:

```text
··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ···
```

### Global field pulse

The global field pulse gives a different shape: all links peak together.

```text
M-C peak time = 39
C-R peak time = 39
R-W peak time = 39
```

Compact raster:

```text
··· ··· ··· ··· ··· ··· ··· ··· ▒▒▒ ███ ███ ▒▒▒ ░░░ ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ··· ···
```

## Observation

v2 gives a cleaner local-to-neighbor picture than v1.

```text
Touch an edge part: response moves inward along the chain.
Touch a middle part: both neighboring links light first, then the farther link follows.
Move the whole field: all links light together.
Remove direct links: activations can move, but pair negativity does not appear.
```

This is the first observation in the line where a local perturbation produces a structured part-to-part response rather than merely following a pre-shaped field pulse.

## Next observation

```text
quantum_homeostatic_parts_observation_v3_recovery_cycle:
  touch a part repeatedly
  let the system recover between touches
  watch whether the negativity response adapts, saturates, or habituates
  compare recovery under high-energy and high-toxicity conditions
```
