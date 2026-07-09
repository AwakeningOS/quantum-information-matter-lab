# classical_vs_quantum_part_coupling_v2_diag_single_noise Report

Date: 2026-07-09

Status: OBSERVATION_LOG

Protocol:

```text
experiments/classical_vs_quantum_part_coupling_v2_diag_protocol_20260709.md
```

Data:

```text
data/quantum_observation/classical_vs_quantum_part_coupling_v2_diag_single_noise_seed20260757_20260772.json
data/quantum_observation/classical_vs_quantum_part_coupling_v2_diag_single_noise_seed20260757_20260772_summary.csv
```

## Purpose

v2 showed:

```text
none/light survive
medium fails strict max-U separation
heavy is fragile
```

This diagnostic isolates noise sources one at a time.

## Important readout-model caveat

The v2 readout model is symmetric bit-flip readout noise. It is not an asymmetric hardware readout model.

Therefore, readout-only survival here does not prove hardware readout asymmetry is harmless.

## Medium-equivalent single-noise results

| profile | direct mean | no_entangle mean | direct-vs-no U | gap |
|---|---:|---:|---:|---:|
| medium_dephase_only | 0.038406 | -0.002441 | 256/256 | 0.005615 |
| medium_depol1q_only | 0.036697 | 0.002670 | 250/256 | -0.013184 |
| medium_depol2q_only | 0.038391 | -0.001923 | 256/256 | 0.010498 |
| medium_readout_only | 0.047333 | -0.002014 | 256/256 | 0.011719 |

Medium reading:

```text
readout-only is not the culprit.
dephase-only erodes the witness but still separates cleanly.
2q depolarization-only still separates cleanly.
1q depolarization-only best reproduces the strict max-U fragility.
```

## Heavy-equivalent single-noise results

| profile | direct mean | no_entangle mean | direct-vs-no U | gap |
|---|---:|---:|---:|---:|
| heavy_dephase_only | 0.031052 | 0.004379 | 249/256 | -0.004639 |
| heavy_depol1q_only | 0.035065 | -0.000290 | 253/256 | -0.008301 |
| heavy_depol2q_only | 0.033829 | -0.001923 | 256/256 | 0.004883 |
| heavy_readout_only | 0.039429 | 0.002197 | 253.5/256 | -0.004395 |

Heavy reading:

```text
heavy profiles are diagnostic and tail-overlap appears in several single-noise sources.
readout-only still does not show a systematic no_entangle mean shift that would explain the combined heavy result.
2q depolarization-only remains the cleanest among heavy single-noise tests.
```

## Diagnostic verdict

```text
READOUT_NOT_PRIMARY_IN_CURRENT_SYMMETRIC_MODEL
ONE_Q_DEPOLARIZATION_BEST_REPRODUCES_MEDIUM_FRAGILITY
```

## Interpretation

The earlier v2 medium failure is not best explained by readout-only bias under the implemented symmetric readout model.

Instead, the strongest culprit is:

```text
1q depolarization + seed/shot tail overlap
```

Why:

```text
medium_depol1q_only:
  direct-vs-no U = 250/256
  gap = -0.013184
  paired direct-no_entangle CI remains positive
```

This mirrors the v2 medium pattern: effect remains positive on average, but strict distribution separation fails.

Dephase-only is not the main failure mode in the medium profile:

```text
medium_dephase_only:
  direct mean = 0.038406
  no_entangle mean = -0.002441
  U = 256/256
```

So the witness is not simply dying because coherence is erased. It becomes harder to separate because single-qubit depolarization broadens/reshapes seed-level tails.

## Boundary

```text
No QPU result.
No backend-calibrated noise.
No quantum advantage claim.
No biological organization claim.
No matter synthesis claim.
```

## Next implication

Better next options:

```text
v2c:
  test mitigation against 1q depolarization / basis-conversion fragility
  without changing the witness definition.

or

v3:
  backend-calibrated noise with explicit asymmetric readout model,
  because hardware readout asymmetry was not tested by this symmetric model.
```
