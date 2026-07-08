# Agent Handoff

Updated: 2026-07-08

## Repository role

This repository is a clean lab for contextual information-matter components and quantum-coupled observation models.

```text
No code + no raw log = no result.
```

## Observation line

```text
watch several quantum-coupled parts immersed in one whole-field
```

## Completed observation experiments

```text
quantum_homeostatic_parts_observation_v0 = OBSERVATION_LOG
quantum_homeostatic_parts_observation_v1_pulse_map = OBSERVATION_LOG
quantum_homeostatic_parts_observation_v2_causal_touch_response = OBSERVATION_LOG
quantum_homeostatic_parts_observation_v3_recovery_cycle = OBSERVATION_LOG
quantum_homeostatic_parts_observation_v4_repair_vs_overdrive = OBSERVATION_LOG
```

## v0 lesson

```text
The field-only model can make parts move together, but it does not create pair negativity.
The direct-entangling model produces pair-negativity pulses along M-C / C-R / R-W.
```

## v1 pulse-map lesson

```text
spatial attenuation = which pair is stronger
temporal propagation = when each pair peaks
```

```text
left_to_right_wave peak lags = +24, +18
simultaneous_burst peak lags = +1, -1
right_to_left_wave peak lags = -17, -26
```

## v2 causal-touch lesson

```text
Edge touches move inward along the chain.
Middle touches light both neighboring links first, then the farther link follows.
Global field movement lights all links together.
Removing direct links removes pair negativity.
```

## v3 recovery-cycle lesson

```text
Full reset removes cross-touch memory and keeps response stable.
Active recovery under high energy mostly preserves unitary-touch response.
Measurement touch leaves more population bias and fatigue than unitary touch.
High toxicity makes recovery harder and turns repeated measurement into strong response decay.
```

## v4 repair-vs-overdrive lesson

v4 assigns labels mechanically from predeclared metrics:

```text
response_ratio_last_over_first
overshoot_max
state_distance_last
oscillation_envelope_ratio
bias_last
fatigue_last
```

Key observations:

```text
high_energy + gentle + unitary:
  response ratio = 0.954003707
  state_distance_last = 0.0758656072
  label = stable_repair

high_energy + strong + unitary:
  response ratio = 1.035908941
  overshoot_max = 0.174949411
  oscillation_envelope_ratio = 0.331310936
  label = damped_oscillatory_repair

high_energy + oscillatory + unitary:
  response ratio = 1.081767736
  overshoot_max = 0.257713327
  oscillation_envelope_ratio = 0.534286226
  label = damped_oscillatory_repair

high_energy + extreme + unitary:
  state_distance_last = 1.0698560591
  oscillation_envelope_ratio = 5.290555134
  bias_last = 0.424455566
  fatigue_last = 0.648256006
  label = overdrive

high_toxicity + weak + measurement:
  response ratio = 0.000000000
  coherence_last = 0.000000000
  fatigue_last = 0.835481525
  label = collapse_or_exhausted_repair

high_toxicity + oscillatory + unitary:
  response ratio = 1.312665687
  overshoot_max = 0.316634425
  oscillation_envelope_ratio = 1.357167475
  label = overdrive
```

Interpretation:

```text
Gentle recovery can repair without overshoot.
Strong/oscillatory recovery can ring and then settle when the envelope decays.
Extreme recovery or toxic oscillatory recovery becomes overdrive when state-distance or envelope grows.
Weak recovery under toxic measurement can collapse into exhausted repair.
```

## Recommended next experiment

```text
quantum_homeostatic_parts_observation_v5_adaptive_recovery_controller
```

Core rule:

```text
Let recovery gain depend on state-distance and fatigue.
Compare fixed recovery against adaptive recovery.
Watch whether adaptive recovery avoids both exhaustion and overdrive.
```

## Boundary

The quantum-homeostatic results are observation logs.

They record trajectories; they do not try to prove advantage or promote a hardware claim.
