# Q-Cell Phenomenon Map Wide Observation Report

Date: 2026-07-09
Layer: QUANTUM_OBSERVATION
Status: OBSERVATION_LOG
Experiment: `qcell_phenomenon_map_wide_observation`

## Scope

This run starts a separate Q-cell observation-map line.

It does not modify or extend the finished v2 witness, noise-margin, or QPU-ready work. The experiment treats the Q-cell as an observation target and records a broad response map across coupling modes, interventions, targets, intensities, and phase contexts.

## Run configuration

```text
coupling modes: 6
intervention families: 8
targets: 7
intensities: 4
phase contexts: 2
total rows: 2688
seed: 20260709
```

## Mechanical label counts

| Label | Count |
|---|---:|
| quiet_or_absorbed | 1073 |
| mixed_small_response | 811 |
| coherence_loss | 238 |
| collapse_like_decoherence | 195 |
| direct_output_response | 143 |
| coherence_amplification | 95 |
| entanglement_gain_without_output_shift | 65 |
| distal_output_response | 46 |
| entanglement_linked_distal_response | 22 |

## Coupling-mode observations

| Coupling mode | Rows | Mean abs ΔP1_W | Mean Δ max link negativity | Dominant labels |
|---|---:|---:|---:|---|
| broken_middle_link | 448 | 0.015548 | -0.013199 | mixed_small_response, quiet_or_absorbed, coherence_amplification |
| dephased_chain | 448 | 0.000459 | 0.000000 | quiet_or_absorbed |
| direct_chain | 448 | 0.007886 | -0.016010 | mixed_small_response, quiet_or_absorbed, entanglement_gain_without_output_shift |
| field_only | 448 | 0.021423 | 0.000000 | quiet_or_absorbed, mixed_small_response, coherence_loss |
| no_entangle | 448 | 0.021616 | 0.000000 | quiet_or_absorbed, mixed_small_response, coherence_loss |
| ring_coupled | 448 | 0.027861 | -0.033494 | mixed_small_response, quiet_or_absorbed, distal_output_response |

## Strongest output-shift regions

The highest mean absolute output-boundary shift regions were:

| Coupling mode | Intervention | Mean abs ΔP1_W | Top label |
|---|---|---:|---|
| ring_coupled | saturation_drive | 0.108911 | distal_output_response |
| no_entangle | saturation_drive | 0.081719 | coherence_loss |
| field_only | saturation_drive | 0.078781 | coherence_loss |
| no_entangle | ry_touch | 0.047533 | coherence_loss |
| field_only | ry_touch | 0.047284 | coherence_loss |
| broken_middle_link | saturation_drive | 0.032466 | coherence_amplification |
| ring_coupled | ry_touch | 0.028774 | mixed_small_response |
| broken_middle_link | x_flip_touch | 0.028607 | mixed_small_response |
| broken_middle_link | ry_touch | 0.028549 | mixed_small_response |
| ring_coupled | weak_measurement_patch | 0.023980 | collapse_like_decoherence |

## Intervention-family observations

| Intervention | Mean abs ΔP1_W | Dominant labels |
|---|---:|---|
| echo_reversal | 0.005627 | quiet_or_absorbed, mixed_small_response, coherence_amplification |
| reset_patch | 0.002171 | quiet_or_absorbed, mixed_small_response, coherence_loss |
| ry_touch | 0.026401 | mixed_small_response, quiet_or_absorbed, coherence_loss |
| rz_phase_kick | 0.007593 | quiet_or_absorbed, mixed_small_response, coherence_amplification |
| saturation_drive | 0.053782 | coherence_loss, quiet_or_absorbed, mixed_small_response |
| weak_measurement_patch | 0.012296 | collapse_like_decoherence, mixed_small_response, quiet_or_absorbed |
| x_flip_touch | 0.011964 | quiet_or_absorbed, mixed_small_response, coherence_amplification |
| z_dephase_patch | 0.006553 | mixed_small_response, quiet_or_absorbed, collapse_like_decoherence |

## Interpretation guardrails

This report is not a claim that any coupling mode is better. It is also not a claim that a QPU witness has been improved.

The useful product is the map shape:

- most of the grid was quiet, absorbed, or small-response;
- dephased-chain conditions were almost completely quiet under this label scheme;
- saturation drive created the largest output-boundary shifts, but those shifts often came with coherence-loss labels;
- ring coupling produced the clearest distal-output region in this sandbox;
- weak-measurement and dephase-like interventions often moved the map toward collapse-like decoherence labels.

## Status

OBSERVATION_LOG only. No PASS/FAIL promotion.
