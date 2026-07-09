# Protocol: classical_vs_quantum_part_coupling_v2_diag_single_noise

Date: 2026-07-09

Layer: QUANTUM_OBSERVATION -> QUANTUM_AUDIT candidate

Status: PRE-REGISTERED DIAGNOSTIC BEFORE SINGLE-NOISE RUN

Generator planned:

```text
scripts/quantum_observation/classical_vs_quantum_part_coupling_v2_diag_single_noise.py
```

Raw log planned:

```text
data/quantum_observation/classical_vs_quantum_part_coupling_v2_diag_single_noise_seed20260757_20260772.json
```

Summary CSV planned:

```text
data/quantum_observation/classical_vs_quantum_part_coupling_v2_diag_single_noise_seed20260757_20260772_summary.csv
```

## Purpose

v2 produced:

```text
none/light survive
medium fails strict max-U separation
heavy is diagnostic and fragile
```

This diagnostic isolates noise sources one at a time to avoid guessing whether the medium/heavy degradation comes mainly from:

```text
dephase
1q depolarization
2q depolarization
readout flip
```

This is a cause-separation diagnostic only. It does not promote a QPU claim.

## Fixed estimator and inference

Same as v1a/v2:

```text
oriented_phase_effect_P1W =
  P1_W(phaseM=0, M perturb) - P1_W(phaseM=pi/2, M perturb)

shots per seed = 4096
inference unit = seed
seed block = 20260757-20260772
```

## Arms

```text
quantum_field_only
quantum_no_entangle
quantum_direct_coupled
quantum_dephased_control
```

## Single-noise profiles

Medium-equivalent:

```text
medium_dephase_only:  p_dephase_layer=0.008
medium_depol1q_only:  p_depolarize_1q=0.003
medium_depol2q_only:  p_depolarize_2q=0.012
medium_readout_only:  p_readout_flip=0.025
```

Heavy-equivalent:

```text
heavy_dephase_only:  p_dephase_layer=0.018
heavy_depol1q_only:  p_depolarize_1q=0.007
heavy_depol2q_only:  p_depolarize_2q=0.030
heavy_readout_only:  p_readout_flip=0.050
```

Only one noise type is active per profile. All other noise parameters are zero.

## Diagnostic questions

```text
Q1: Does readout-only produce a positive no_entangle shift?
Q2: Does dephase-only reduce direct while keeping no_entangle centered?
Q3: Does 1q/2q depolarization create overlap between direct and no_entangle tails?
Q4: Which single noise source best explains the v2 medium/heavy separation failure?
```

## Reading rules

```text
readout_culprit:
  readout-only no_entangle CI excludes 0 or shows strong same-sign skew.

dephase_culprit:
  dephase-only strongly reduces direct and weakens direct-no_entangle separation while no_entangle remains centered.

depolarization_culprit:
  depol-only keeps no_entangle mostly centered but widens tails enough to break max-U separation.

inconclusive:
  no single-noise profile reproduces the combined-profile failure pattern.
```

## Boundary

```text
no QPU submission
no backend-calibrated noise
no quantum advantage claim
no biological organization claim
no matter synthesis claim
```
