# Protocol: quantum_homeostatic_parts_observation_v2_causal_touch_response

Date: 2026-07-08

## Question

If one part is locally touched, does the response spread through neighboring quantum links, or does it only look global because the whole-field moves everything together?

This follows:

```text
v0 = direct entangling links create pair-negativity pulses
v1 = peak/onset lags separate propagation from simultaneous drive
v2 = local touch response: perturb one part and watch the response spread
```

## Layer

```text
QUANTUM_OBSERVATION
```

## Stance

This is an observation model, not a PASS/FAIL test.

The goal is to record whether local perturbations create a local-to-neighbor-to-next-neighbor response pattern.

## Parts

```text
M = membrane
C = conversion / catalyst
R = recycler
W = waste outlet
```

## Modes

```text
local_touch_direct:
  one part receives a local kick while direct M-C / C-R / R-W entangling links are active

field_only_local_touch:
  one part receives the same local kick, but direct part-part entangling links are removed

global_field_pulse:
  no single-part touch; the whole-field is pulsed so all parts are driven together
```

## Touch targets

```text
M
C
R
W
```

## Field regimes

```text
fixed_field:
  energy/toxicity/pressure stay nearly fixed while the local touch propagates

slow_field:
  energy/toxicity/pressure drift slowly, but no strong pre-shaped pulse is injected
```

## Observables

For each scenario:

```text
activation delta for M/C/R/W
pair negativity delta for M-C / C-R / R-W
activation peak time per part
negativity peak time per pair
neighbor lag from touched part to adjacent link
next-link lag from adjacent link to second link
compact response raster
```

## Run command

```bash
python scripts/quantum_observation/quantum_homeostatic_parts_observation_v2_causal_touch_response.py \
  --seed 20260708 \
  --steps 120 \
  --touch-time 30 \
  --out data/quantum_observation/quantum_homeostatic_parts_observation_v2_causal_touch_response_seed20260708.json \
  --summary-csv data/quantum_observation/quantum_homeostatic_parts_observation_v2_causal_touch_response_seed20260708_summary.csv \
  --trace-csv data/quantum_observation/quantum_homeostatic_parts_observation_v2_causal_touch_response_seed20260708_compact_trace.csv
```

## Observation boundary

This run records local response trajectories. It does not try to prove an advantage or promote a hardware claim.

The saved distinction is:

```text
local touch response = a perturbation starts at one part and spreads through adjacent quantum links
global field response = many links rise together because the whole-field moved them together
field-only response = activations may change, but pair negativity stays zero
```
