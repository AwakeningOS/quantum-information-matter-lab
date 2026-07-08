# Observation: quantum_boundary_homeostasis_v0_internal_feedback

Status: OBSERVATION_LOG  
Generator script: `scripts/quantum_observation/quantum_boundary_homeostasis_v0_internal_feedback.py`  
Raw log: `data/quantum_observation/quantum_boundary_homeostasis_v0_internal_feedback_seed20260708.json`  
Summary CSV: `data/quantum_observation/quantum_boundary_homeostasis_v0_internal_feedback_seed20260708_summary.csv`  
Selected trace CSV: `data/quantum_observation/quantum_boundary_homeostasis_v0_internal_feedback_seed20260708_selected_trace.csv`  
Run command: `python scripts/quantum_observation/quantum_boundary_homeostasis_v0_internal_feedback.py --seed 20260708 --out data/quantum_observation/quantum_boundary_homeostasis_v0_internal_feedback_seed20260708.json --summary-csv data/quantum_observation/quantum_boundary_homeostasis_v0_internal_feedback_seed20260708_summary.csv --trace-csv data/quantum_observation/quantum_boundary_homeostasis_v0_internal_feedback_seed20260708_selected_trace.csv`  
Layer: QUANTUM_OBSERVATION

## What this starts

The previous observation line watched four quantum-coupled parts:

```text
M = membrane
C = conversion / catalyst
R = recycler
W = waste outlet
```

This run adds an inside/outside boundary and asks whether the system can preserve an interior without closing itself off from exchange.

## Core rule

The main arm is not an external reflex.

It uses internal negative feedback:

```text
internal_error =
  internal_toxicity - toxicity_target
+ internal_pressure - pressure_target
+ resource_target - internal_resource
```

The boundary changes because the inside is off target, not merely because the outside is disturbed.

## Arms

```text
coherent_internal_feedback
measurement_internal_feedback
external_reactive_boundary
open_boundary
overclosed_boundary
wrong_target_boundary
```

## Main metric

Protection alone is not enough. A closed wall can protect by killing exchange.

The balance metric is:

```text
homeostasis_balance = target_range_fraction * resource_intake_fraction * efficiency_factor
```

where:

```text
efficiency_factor = 1 / (1 + 3.5 * boundary_work_rate)
```

## Main observation table

| Arm | Target range | Resource intake | Boundary work | Efficiency | Balance | Gradient | Unnecessary closure | Internal sensitivity | Fatigue final | Bias final |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| coherent_internal_feedback | 0.843750000 | 0.695312500 | 0.058000000 | 0.831255195 | 0.487672421 | 0.462000000 | 0.070312500 | 0.362000000 | 0.084000000 | 0.032000000 |
| measurement_internal_feedback | 0.859375000 | 0.546875000 | 0.083000000 | 0.774893452 | 0.364177221 | 0.481000000 | 0.179687500 | 0.318000000 | 0.336000000 | 0.246000000 |
| external_reactive_boundary | 0.671875000 | 0.640625000 | 0.077000000 | 0.787711698 | 0.339046807 | 0.304000000 | 0.234375000 | 0.052000000 | 0.118000000 | 0.036000000 |
| open_boundary | 0.382812500 | 0.953125000 | 0.018000000 | 0.940733772 | 0.343243804 | 0.118000000 | 0.000000000 | 0.004000000 | 0.026000000 | 0.022000000 |
| overclosed_boundary | 0.914062500 | 0.101562500 | 0.024000000 | 0.922509225 | 0.085640657 | 0.524000000 | 0.742187500 | 0.006000000 | 0.041000000 | 0.022000000 |
| wrong_target_boundary | 0.453125000 | 0.765625000 | 0.062000000 | 0.821692687 | 0.285064772 | 0.226000000 | 0.117187500 | 0.287000000 | 0.073000000 | 0.028000000 |

## What the comparison shows

### Coherent internal feedback

```text
target_range_fraction = 0.843750000
resource_intake_fraction = 0.695312500
homeostasis_balance = 0.487672421
internal_state_sensitivity = 0.362000000
fatigue_final = 0.084000000
bias_final = 0.032000000
```

This is the cleanest homeostatic shape in the run. It protects the inside, keeps exchange alive, and changes boundary behavior according to internal state.

### Measurement internal feedback

```text
target_range_fraction = 0.859375000
resource_intake_fraction = 0.546875000
homeostasis_balance = 0.364177221
fatigue_final = 0.336000000
bias_final = 0.246000000
```

Measurement feedback protects slightly more often, but it costs more: intake is lower and bias/fatigue are much higher.

### External reactive boundary

```text
target_range_fraction = 0.671875000
internal_state_sensitivity = 0.052000000
homeostasis_balance = 0.339046807
```

It reacts, but mostly as an external mirror. Same-external / different-internal responsiveness is weak.

### Open boundary

```text
target_range_fraction = 0.382812500
resource_intake_fraction = 0.953125000
homeostasis_balance = 0.343243804
```

It exchanges well but does not preserve the interior.

### Overclosed boundary

```text
target_range_fraction = 0.914062500
resource_intake_fraction = 0.101562500
unnecessary_closure_rate = 0.742187500
homeostasis_balance = 0.085640657
```

This arm proves why target range alone is not enough. It protects by starving the interior.

### Wrong target boundary

```text
target_range_fraction = 0.453125000
resource_intake_fraction = 0.765625000
homeostasis_balance = 0.285064772
```

It moves and exchanges, but it protects the wrong internal range.

## Quantum-coupled response trace

The coherent internal feedback arm keeps the M-C -> C-R -> R-W timing seen in the earlier local-touch line:

```text
M-C peak time/value = 42 / 0.044800000000
C-R peak time/value = 55 / 0.028700000000
R-W peak time/value = 69 / 0.017900000000
lags = +13, +14
```

Measurement feedback keeps the lag structure but with weaker pair-negativity pulses:

```text
M-C peak time/value = 43 / 0.026600000000
C-R peak time/value = 57 / 0.014400000000
R-W peak time/value = 71 / 0.007200000000
lags = +14, +14
```

## Observation

This run separates six boundary behaviors:

```text
coherent internal feedback:
  protects, exchanges, responds to internal state, and keeps low fatigue/bias

measurement internal feedback:
  protects but leaves backaction-like fatigue/bias and lowers intake

external reactive boundary:
  responds to external stress but weakly differentiates internal state

open boundary:
  exchanges but fails to protect

overclosed boundary:
  protects but starves exchange

wrong target boundary:
  regulates, but around the wrong internal target
```

The useful result is not that one arm wins. The useful result is that a self-boundary is visible only when protection, exchange, efficiency, and internal-state feedback are recorded together.

## Next observation

```text
quantum_boundary_homeostasis_v1_adaptive_boundary_controller:
  let the boundary tune its own feedback gain from internal error, fatigue, and resource deficit
  compare fixed internal feedback against adaptive internal feedback
  watch whether adaptive feedback keeps balance high under changing stress without drifting into closure or exhaustion
```
