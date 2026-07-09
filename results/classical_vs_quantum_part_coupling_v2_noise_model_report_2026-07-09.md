# classical_vs_quantum_part_coupling_v2_noise_model Report

Date: 2026-07-09

Status: OBSERVATION_LOG

Protocol:

```text
experiments/classical_vs_quantum_part_coupling_v2_noise_protocol_20260709.md
```

Raw/summary data:

```text
data/quantum_observation/classical_vs_quantum_part_coupling_v2_noise_seed20260741_20260756.json
data/quantum_observation/classical_vs_quantum_part_coupling_v2_noise_seed20260741_20260756_summary.csv
```

## Purpose

v1a promoted the signed/oriented `P1_W` witness to a noise-model candidate. v2 tests whether the same witness survives simple pre-hardware noise profiles.

This is not backend-calibrated and not a QPU result.

## Estimator

```text
oriented_phase_effect_P1W =
  P1_W(phaseM=0, M perturb) - P1_W(phaseM=pi/2, M perturb)
```

Inference unit remains the seed.

```text
shots per seed = 4096
seeds = 20260741-20260756
```

## Noise profiles

| profile | p_dephase_layer | p_depolarize_1q | p_depolarize_2q | p_readout_flip |
|---|---:|---:|---:|---:|
| none | 0.000 | 0.000 | 0.000 | 0.000 |
| light | 0.003 | 0.001 | 0.004 | 0.010 |
| medium | 0.008 | 0.003 | 0.012 | 0.025 |
| heavy | 0.018 | 0.007 | 0.030 | 0.050 |

## Summary by profile

### none

| arm | exact | mean | CI | signs | min | max |
|---|---:|---:|---:|---:|---:|---:|
| quantum_field_only | 0.000000 | -0.005005 | [-0.010559, 0.001344] | +4 / -12 | -0.019043 | 0.024414 |
| quantum_no_entangle | 0.000000 | 0.001663 | [-0.002838, 0.006317] | +9 / -7 | -0.014648 | 0.019287 |
| quantum_direct_coupled | 0.046132 | 0.049835 | [0.045914, 0.054184] | +16 / -0 | 0.037842 | 0.072266 |
| quantum_dephased_control | 0.000115 | 0.000183 | [-0.006088, 0.006912] | +9 / -7 | -0.018311 | 0.031982 |

Direct-vs-control:

| control | direct-control mean | CI | U | p if U=max | gap |
|---|---:|---:|---:|---:|---:|
| field_only | 0.054906 | [0.046753, 0.062805] | 256/256 | 1.664e-09 | 0.013428 |
| no_entangle | 0.048213 | [0.042603, 0.053940] | 256/256 | 1.664e-09 | 0.018555 |
| dephased | 0.049730 | [0.042343, 0.057220] | 256/256 | 1.664e-09 | 0.005859 |

Profile verdict: **survives**.

### light

| arm | exact | mean | CI | signs | min | max |
|---|---:|---:|---:|---:|---:|---:|
| quantum_field_only | 0.000000 | -0.001266 | [-0.007156, 0.004624] | +6 / -9 | -0.017822 | 0.024170 |
| quantum_no_entangle | 0.000000 | 0.001144 | [-0.002319, 0.004853] | +9 / -7 | -0.010254 | 0.019531 |
| quantum_direct_coupled | 0.038029 | 0.040390 | [0.037445, 0.043290] | +16 / -0 | 0.029541 | 0.050537 |
| quantum_dephased_control | 0.000095 | -0.001846 | [-0.008011, 0.004211] | +8 / -8 | -0.024902 | 0.016357 |

Direct-vs-control:

| control | direct-control mean | CI | U | p if U=max | gap |
|---|---:|---:|---:|---:|---:|
| field_only | 0.041652 | [0.034485, 0.048965] | 256/256 | 1.664e-09 | 0.005371 |
| no_entangle | 0.039256 | [0.033676, 0.044205] | 256/256 | 1.664e-09 | 0.010010 |
| dephased | 0.042241 | [0.036240, 0.048706] | 256/256 | 1.664e-09 | 0.013184 |

Profile verdict: **survives**.

### medium

| arm | exact | mean | CI | signs | min | max |
|---|---:|---:|---:|---:|---:|---:|
| quantum_field_only | 0.000000 | 0.002594 | [-0.001801, 0.006577] | +11 / -5 | -0.017090 | 0.013184 |
| quantum_no_entangle | 0.000000 | -0.003723 | [-0.009018, 0.001572] | +5 / -11 | -0.028076 | 0.020508 |
| quantum_direct_coupled | 0.026703 | 0.026520 | [0.023819, 0.029327] | +16 / -0 | 0.018555 | 0.038574 |
| quantum_dephased_control | 0.000068 | -0.002838 | [-0.007416, 0.001556] | +6 / -10 | -0.021240 | 0.012695 |

Direct-vs-control:

| control | direct-control mean | CI | U | p if U=max | gap |
|---|---:|---:|---:|---:|---:|
| field_only | 0.023937 | [0.019912, 0.028412] | 256/256 | 1.664e-09 | 0.005371 |
| no_entangle | 0.030196 | [0.024368, 0.035904] | 252/256 |  | -0.001953 |
| dephased | 0.029318 | [0.023865, 0.034500] | 256/256 | 1.664e-09 | 0.005859 |

Profile verdict: **fails strict survival criterion**.

Reason:

```text
direct - no_entangle paired CI remains positive,
but Mann-Whitney U is 252/256 rather than the pre-registered max-U separation.
```

### heavy

| arm | exact | mean | CI | signs | min | max |
|---|---:|---:|---:|---:|---:|---:|
| quantum_field_only | 0.000000 | -0.000504 | [-0.006668, 0.005280] | +8 / -8 | -0.028564 | 0.018311 |
| quantum_no_entangle | 0.000000 | 0.005737 | [0.001465, 0.009460] | +13 / -3 | -0.015137 | 0.020020 |
| quantum_direct_coupled | 0.012789 | 0.015442 | [0.009781, 0.020599] | +14 / -2 | -0.008545 | 0.030518 |
| quantum_dephased_control | 0.000033 | 0.000748 | [-0.005829, 0.007904] | +6 / -9 | -0.017334 | 0.028320 |

Direct-vs-control:

| control | direct-control mean | CI | U | p if U=max | gap |
|---|---:|---:|---:|---:|---:|
| field_only | 0.015968 | [0.007721, 0.023972] | 212/256 |  | -0.026855 |
| no_entangle | 0.009654 | [0.002899, 0.016006] | 193.5/256 |  | -0.028564 |
| dephased | 0.014750 | [0.005005, 0.023697] | 201/256 |  | -0.036865 |

Profile verdict: **diagnostic failure under heavy noise**.

## Overall verdict

```text
PARTIAL_NOISE_MODEL_CANDIDATE
```

## Interpretation

The signed/oriented witness survives:

```text
none
light
```

It becomes fragile at:

```text
medium
```

and is not reliable under:

```text
heavy
```

The important point is that v2 does **not** justify immediate QPU submission. It only says the witness survives a light pre-hardware noise floor and should either be strengthened or tested against a backend-calibrated noise model before hardware.

## Boundary

```text
No QPU result.
No quantum advantage claim.
No biological organization claim.
No matter synthesis claim.
```

## Next implication

The next justified step is not a broad QPU run. Options:

```text
v2b:
  strengthen circuit margin while preserving the v1a protocol structure,
  then rerun the same noise profiles.

or

v3 backend-calibrated noise:
  use a specific target backend noise model and keep only if light/medium-equivalent survival remains.
```
