# Q-Cell Phenomenon Map Wide Observation Protocol

Date: 2026-07-09
Layer: QUANTUM_OBSERVATION
Status: OBSERVATION_LOG
Experiment: `qcell_phenomenon_map_wide_observation`

## Purpose

Map what happens when a compact Q-cell sandbox receives diverse interventions.

This is an observation experiment. It is not a proof attempt, not a witness-strengthening task, not a noise-margin task, and not a QPU-readiness task.

## Explicit non-goals

- Do not improve the v2 witness line.
- Do not add noise-margin diagnostics.
- Do not make or repair a QPU-ready submission path.
- Do not tune toward a single desired phenomenon.
- Do not promote PASS/FAIL claims.
- Do not optimize performance.

## Q-cell abstraction

The Q-cell is represented as a four-role density-matrix sandbox:

```text
M = membrane / input boundary
C = core / converter
R = residue / memory-like interior
W = witness / output boundary
```

This role naming is operational only. It is used to organize observations, not to claim biological cell behavior or hardware realization.

## Observation grid

The map sweeps:

```text
6 coupling modes × 8 intervention families × 7 targets × 4 intensities × 2 phase contexts = 2688 rows
```

### Coupling modes

- `field_only`
- `no_entangle`
- `direct_chain`
- `dephased_chain`
- `broken_middle_link`
- `ring_coupled`

### Intervention families

- `ry_touch`
- `rz_phase_kick`
- `x_flip_touch`
- `z_dephase_patch`
- `weak_measurement_patch`
- `reset_patch`
- `echo_reversal`
- `saturation_drive`

### Targets

- `M`
- `C`
- `R`
- `W`
- `MC`
- `CR`
- `RW`

### Intensities

- `0.25`
- `0.50`
- `1.00`
- `1.50`

### Phase contexts

- `0`
- `pi/2`

## Metrics

For each condition, record metrics and deltas against the local baseline for the same coupling mode and phase context:

- `P1_M`, `P1_C`, `P1_R`, `P1_W`
- `ZZ_MC`, `ZZ_CR`, `ZZ_RW`
- pair negativity on `MC`, `CR`, `RW`
- max link negativity
- negativity spread count
- purity
- von Neumann entropy
- L1 coherence
- mechanical phenomenon label

## Mechanical labels

Labels are assigned mechanically from observed deltas. They are not success states.

- `quiet_or_absorbed`
- `mixed_small_response`
- `coherence_loss`
- `coherence_amplification`
- `collapse_like_decoherence`
- `direct_output_response`
- `distal_output_response`
- `entanglement_gain_without_output_shift`
- `entanglement_linked_distal_response`
- `output_suppression`

## Claim discipline

The output may be described as an observation map only.

Allowed wording:

```text
Under this sandbox and grid, intervention class X was mechanically labeled Y more often than Z.
```

Disallowed wording:

```text
This proves the Q-cell mechanism.
This improves the v2 witness.
This is QPU-ready.
This establishes a quantum advantage.
```
