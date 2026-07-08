# Observation: quantum_homeostatic_parts_observation_v4_repair_vs_overdrive

Status: OBSERVATION_LOG  
Generator script: `scripts/quantum_observation/quantum_homeostatic_parts_observation_v4_repair_vs_overdrive.py`  
Raw log: `data/quantum_observation/quantum_homeostatic_parts_observation_v4_repair_vs_overdrive_seed20260708.json`  
Summary CSV: `data/quantum_observation/quantum_homeostatic_parts_observation_v4_repair_vs_overdrive_seed20260708_summary.csv`  
Selected touch rows CSV: `data/quantum_observation/quantum_homeostatic_parts_observation_v4_repair_vs_overdrive_seed20260708_selected_touch_rows.csv`  
Run command: `python scripts/quantum_observation/quantum_homeostatic_parts_observation_v4_repair_vs_overdrive.py --seed 20260708 --out data/quantum_observation/quantum_homeostatic_parts_observation_v4_repair_vs_overdrive_seed20260708.json --summary-csv data/quantum_observation/quantum_homeostatic_parts_observation_v4_repair_vs_overdrive_seed20260708_summary.csv --touch-csv data/quantum_observation/quantum_homeostatic_parts_observation_v4_repair_vs_overdrive_seed20260708_selected_touch_rows.csv`  
Layer: QUANTUM_OBSERVATION

## What changed from v3

v3 asked whether repeated touches leave cross-touch state traces.

v4 asks whether active recovery remains healthy, becomes damped oscillatory repair, becomes overdrive, or collapses into exhausted repair.

The labels are assigned mechanically. They are not assigned by looking at the plot afterward.

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

## Main observation table

| Condition | Recovery | Touch | Response ratio | Overshoot max | State distance last | Oscillation envelope | Bias last | Fatigue last | Label |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| high_energy | gentle | unitary | 0.954003707 | 0.000000000 | 0.0758656072 | 0.000000000 | 0.032506796 | 0.046800278 | stable_repair |
| high_energy | strong | unitary | 1.035908941 | 0.174949411 | 0.0260516299 | 0.331310936 | 0.023213113 | 0.024225760 | damped_oscillatory_repair |
| high_energy | oscillatory | unitary | 1.081767736 | 0.257713327 | 0.0812575432 | 0.534286226 | 0.029253764 | 0.053325420 | damped_oscillatory_repair |
| high_energy | extreme | unitary | 0.943625235 | 0.245897274 | 1.0698560591 | 5.290555134 | 0.424455566 | 0.648256006 | overdrive |
| high_toxicity | weak | measurement | 0.000000000 | 0.000000000 | 2.0435109888 | 0.000000000 | 0.980157211 | 0.835481525 | collapse_or_exhausted_repair |
| high_toxicity | oscillatory | unitary | 1.312665687 | 0.316634425 | 0.2723835122 | 1.357167475 | 0.048137720 | 0.138894844 | overdrive |
| high_toxicity | extreme | measurement | 0.583472454 | 0.077049961 | 1.9252840941 | 4.126339725 | 0.906860352 | 1.000000000 | overdrive |
| high_toxicity | full reset | measurement | 1.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.020000000 | 0.020000000 | stable_repair |

## Label counts

```text
stable_repair = 7
damped_oscillatory_repair = 6
overdrive = 6
collapse_or_exhausted_repair = 3
partial_repair_or_fatigue = 2
```

## What the categories mean here

### Gentle recovery

Gentle recovery under high energy stays close to the setpoint:

```text
response ratio = 0.954003707
state_distance_last = 0.0758656072
fatigue_last = 0.046800278
mechanical_label = stable_repair
```

This is the clean repair zone.

### Strong / oscillatory recovery

Strong recovery and high-energy oscillatory recovery overshoot, but the envelope decays:

```text
high_energy strong unitary:
  overshoot_max = 0.174949411
  oscillation_envelope_ratio = 0.331310936
  label = damped_oscillatory_repair

high_energy oscillatory unitary:
  overshoot_max = 0.257713327
  oscillation_envelope_ratio = 0.534286226
  label = damped_oscillatory_repair
```

This is not overdrive. It is a stronger repair process that rings and then settles.

### Extreme recovery

Extreme recovery is not merely stronger repair. It pushes the state away from the setpoint:

```text
high_energy extreme unitary:
  state_distance_last = 1.0698560591
  oscillation_envelope_ratio = 5.290555134
  bias_last = 0.424455566
  fatigue_last = 0.648256006
  label = overdrive
```

The response ratio alone would not be enough here. The overdrive label is carried by state-distance growth, envelope growth, bias, and fatigue.

### High-toxicity oscillatory recovery

Under high toxicity, even oscillatory recovery becomes unstable:

```text
response_ratio = 1.312665687
overshoot_max = 0.316634425
oscillation_envelope_ratio = 1.357167475
label = overdrive
```

The same oscillatory idea that can damp under high-energy conditions crosses into overdrive when the environment is toxic.

### Exhausted repair

Weak recovery plus high-toxicity measurement touch collapses the repeated response:

```text
response_ratio = 0.000000000
coherence_last = 0.000000000
bias_last = 0.980157211
fatigue_last = 0.835481525
label = collapse_or_exhausted_repair
```

This is not overdrive. It is exhaustion.

## Observation

v4 separates four recovery shapes:

```text
stable repair:
  recovery is enough and does not overshoot

damped oscillatory repair:
  recovery overshoots but the oscillation envelope decays

overdrive:
  recovery pushes state distance or oscillation envelope upward

collapse / exhausted repair:
  recovery is too weak under irreversible or toxic load
```

The most useful distinction is that overdrive is not defined by a large response alone. It is defined by response or oscillation growth together with state-distance, fatigue, or bias growth.

## Next observation

```text
quantum_homeostatic_parts_observation_v5_adaptive_recovery_controller:
  let recovery gain depend on state-distance and fatigue
  compare fixed recovery against adaptive recovery
  watch whether adaptive recovery avoids both exhaustion and overdrive
```
