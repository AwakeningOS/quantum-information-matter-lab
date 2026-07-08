# Observation: quantum_homeostatic_parts_observation_v3_recovery_cycle

Status: OBSERVATION_LOG  
Generator script: `scripts/quantum_observation/quantum_homeostatic_parts_observation_v3_recovery_cycle.py`  
Raw log: `data/quantum_observation/quantum_homeostatic_parts_observation_v3_recovery_cycle_seed20260708.json`  
Summary CSV: `data/quantum_observation/quantum_homeostatic_parts_observation_v3_recovery_cycle_seed20260708_summary.csv`  
Touch rows CSV: `data/quantum_observation/quantum_homeostatic_parts_observation_v3_recovery_cycle_seed20260708_touch_rows.csv`  
Run command: `python scripts/quantum_observation/quantum_homeostatic_parts_observation_v3_recovery_cycle.py --seed 20260708 --out data/quantum_observation/quantum_homeostatic_parts_observation_v3_recovery_cycle_seed20260708.json --summary-csv data/quantum_observation/quantum_homeostatic_parts_observation_v3_recovery_cycle_seed20260708_summary.csv --touch-csv data/quantum_observation/quantum_homeostatic_parts_observation_v3_recovery_cycle_seed20260708_touch_rows.csv`  
Layer: QUANTUM_OBSERVATION

## What changed from v2

v2 touched one part once and watched the response spread.

v3 touches C repeatedly and asks what carries across time:

```text
coherence residual
population bias
baseline negativity
fatigue index
```

The response is computed from these state variables, not from an explicit touch-count response rule.

## Design

Recovery modes:

```text
passive_recovery
active_recovery
full_reset_baseline
```

Touch types:

```text
unitary_touch
measurement_touch
```

Conditions:

```text
high_energy
high_toxicity
```

Target:

```text
C
```

## Main summary

| Condition | Recovery | Touch | First adjacent peak | Last adjacent peak | Last/first | Coherence first -> last | Bias first -> last | Fatigue first -> last | Label |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| high_energy | passive | unitary | 0.075935522263 | 0.034707634089 | 0.457067168 | 0.860000000 -> 0.440613760 | 0.020000000 -> 0.079337272 | 0.020000000 -> 0.169577969 | habituation_like_response_decay |
| high_energy | passive | measurement | 0.066519517502 | 0.008437906089 | 0.126848576 | 0.860000000 -> 0.173379520 | 0.020000000 -> 0.381904432 | 0.020000000 -> 0.342332500 | habituation_like_response_decay |
| high_energy | active | unitary | 0.075935522263 | 0.067009545836 | 0.882453216 | 0.860000000 -> 0.774896250 | 0.020000000 -> 0.015562008 | 0.020000000 -> 0.060639219 | active_recovery_holds_response |
| high_energy | active | measurement | 0.066519517502 | 0.048471783851 | 0.728685139 | 0.860000000 -> 0.696815625 | 0.020000000 -> 0.085963248 | 0.020000000 -> 0.125592500 | partial_recovery_or_mild_decay |
| high_energy | full reset | unitary | 0.075935522263 | 0.075935522263 | 1.000000000 | 0.860000000 -> 0.860000000 | 0.020000000 -> 0.020000000 | 0.020000000 -> 0.020000000 | reset_control_stable |
| high_energy | full reset | measurement | 0.066519517502 | 0.066519517502 | 1.000000000 | 0.860000000 -> 0.860000000 | 0.020000000 -> 0.020000000 | 0.020000000 -> 0.020000000 | reset_control_stable |
| high_toxicity | passive | unitary | 0.046075042049 | 0.005112266104 | 0.110955213 | 0.700000000 -> 0.097454448 | 0.020000000 -> 0.124237224 | 0.020000000 -> 0.313874910 | habituation_like_response_decay |
| high_toxicity | passive | measurement | 0.040361736835 | 0.000000000000 | 0.000000000 | 0.700000000 -> 0.000000000 | 0.020000000 -> 0.639302544 | 0.020000000 -> 0.645545760 | habituation_like_response_decay |
| high_toxicity | active | unitary | 0.046075042049 | 0.031481863624 | 0.683273682 | 0.700000000 -> 0.533593250 | 0.020000000 -> 0.049947625 | 0.020000000 -> 0.184142790 | habituation_like_response_decay |
| high_toxicity | active | measurement | 0.040361736835 | 0.016303891506 | 0.403944250 | 0.700000000 -> 0.424280375 | 0.020000000 -> 0.272223250 | 0.020000000 -> 0.382081440 | habituation_like_response_decay |
| high_toxicity | full reset | unitary | 0.046075042049 | 0.046075042049 | 1.000000000 | 0.700000000 -> 0.700000000 | 0.020000000 -> 0.020000000 | 0.020000000 -> 0.020000000 | reset_control_stable |
| high_toxicity | full reset | measurement | 0.040361736835 | 0.040361736835 | 1.000000000 | 0.700000000 -> 0.700000000 | 0.020000000 -> 0.020000000 | 0.020000000 -> 0.020000000 | reset_control_stable |

## What the reset baseline shows

The full-reset baseline stays exactly stable:

```text
high_energy reset unitary last/first = 1.000000000
high_energy reset measurement last/first = 1.000000000
high_toxicity reset unitary last/first = 1.000000000
high_toxicity reset measurement last/first = 1.000000000
```

This is important because it means the response decay is not baked in as a function of touch count. When cross-touch state is erased, the response does not decay.

## Active vs passive recovery

### High-energy unitary touch

```text
passive recovery ratio = 0.457067168
active recovery ratio = 0.882453216
full reset ratio = 1.000000000
```

Active recovery keeps coherence high enough to preserve most of the repeated response.

```text
active high-energy unitary coherence: 0.860000000 -> 0.774896250
active high-energy unitary fatigue: 0.020000000 -> 0.060639219
```

### High-energy measurement touch

```text
active recovery ratio = 0.728685139
```

Measurement touch leaves more population bias and fatigue than unitary touch:

```text
active high-energy measurement bias: 0.020000000 -> 0.085963248
active high-energy measurement fatigue: 0.020000000 -> 0.125592500
```

## High-toxicity condition

High toxicity makes recovery harder.

```text
active high-toxicity unitary ratio = 0.683273682
active high-toxicity measurement ratio = 0.403944250
passive high-toxicity measurement ratio = 0.000000000
```

In the strongest decay case, passive recovery plus measurement touch collapses coherence and accumulates bias/fatigue:

```text
coherence: 0.700000000 -> 0.000000000
population bias: 0.020000000 -> 0.639302544
fatigue: 0.020000000 -> 0.645545760
```

## Observation

v3 shows three qualitatively different repeated-touch regimes:

```text
reset baseline:
  no cross-touch memory, response stable

active recovery under high energy:
  response mostly preserved, especially for unitary touch

passive recovery / high toxicity / measurement touch:
  coherence falls, bias and fatigue accumulate, response decays strongly
```

This is the first observation in the line where response strength depends on variables that persist across touches.

## Next observation

```text
quantum_homeostatic_parts_observation_v4_repair_vs_overdrive:
  test whether too-strong active recovery becomes overdrive
  compare gentle recovery, strong recovery, and oscillatory recovery
  watch whether repeated touches produce stable adaptation or runaway rebound
```
