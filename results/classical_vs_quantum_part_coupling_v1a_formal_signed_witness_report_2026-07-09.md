# classical_vs_quantum_part_coupling_v1a_formal_signed_witness Report

Date: 2026-07-09

Status: OBSERVATION_LOG

Protocol:

```text
experiments/classical_vs_quantum_part_coupling_v1a_protocol_20260709.md
```

Raw log:

```text
data/quantum_observation/classical_vs_quantum_part_coupling_v1a_formal_seed20260725_20260740.json
```

Summary CSV:

```text
data/quantum_observation/classical_vs_quantum_part_coupling_v1a_formal_seed20260725_20260740_summary.csv
```

## Fresh-seed guard

The previous seed-sweep diagnostic used seeds 20260709-20260716. This formal run does **not** reuse them.

```text
formal seeds = 20260725-20260740
shots per seed = 4096
inference unit = seed
```

## Estimator

```text
oriented_phase_effect_P1W =
  P1_W(phaseM=0, M perturb) - P1_W(phaseM=pi/2, M perturb)
```

The orientation was fixed because v1 exact signed effect under `pi/2 - 0` was negative for `direct_coupled`; v1a reports `0 - pi/2` so the expected direct effect is positive.

## Seed-level oriented effects

| seed | field_only | no_entangle | direct_coupled | dephased |
|---:|---:|---:|---:|---:|
| 20260725 | 0.005127 | -0.009277 | 0.043945 | 0.013672 |
| 20260726 | 0.008789 | 0.012207 | 0.057373 | 0.028320 |
| 20260727 | -0.005859 | -0.009277 | 0.045898 | 0.002686 |
| 20260728 | -0.011719 | 0.017334 | 0.053467 | -0.004150 |
| 20260729 | -0.009521 | -0.008789 | 0.049072 | -0.008301 |
| 20260730 | -0.002930 | -0.003174 | 0.073975 | -0.018066 |
| 20260731 | -0.022949 | 0.006592 | 0.036377 | 0.008301 |
| 20260732 | 0.007080 | -0.002197 | 0.054199 | 0.008789 |
| 20260733 | -0.003662 | 0.004150 | 0.049561 | 0.004150 |
| 20260734 | -0.003418 | -0.001465 | 0.038574 | -0.023438 |
| 20260735 | 0.012695 | -0.002441 | 0.047607 | 0.013428 |
| 20260736 | -0.004883 | -0.004395 | 0.055908 | 0.009521 |
| 20260737 | 0.007080 | -0.017334 | 0.043701 | 0.007568 |
| 20260738 | 0.004395 | 0.007324 | 0.035889 | -0.010498 |
| 20260739 | -0.008301 | 0.000244 | 0.036133 | -0.009033 |
| 20260740 | -0.004395 | -0.012939 | 0.028320 | -0.020996 |

## Summary by arm

| arm | exact | mean | std | min | max | signs | seed-bootstrap 95% CI |
|---|---:|---:|---:|---:|---:|---|---:|
| quantum_field_only | 0.000000 | -0.000031 | 0.011786 | -0.024414 | 0.021729 | +8 / -8 | [-0.007508, 0.001801] |
| quantum_no_entangle | 0.000000 | -0.003922 | 0.010825 | -0.022705 | 0.017334 | +6 / -10 | [-0.005814, 0.002976] |
| quantum_direct_coupled | 0.046132 | 0.049988 | 0.012283 | 0.028320 | 0.073975 | +16 / -0 | [0.044083, 0.055695] |
| quantum_dephased_control | 0.000115 | 0.000122 | 0.014334 | -0.023438 | 0.028320 | +9 / -7 | [-0.006714, 0.006821] |

## Direct-vs-control comparisons

| control | direct-control mean | seed-bootstrap 95% CI | Mann-Whitney U | one-sided exact p if U=max | min(direct)-max(control) |
|---|---:|---:|---:|---:|---:|
| quantum_field_only | 0.052752 | [0.046524, 0.059601] | 256.0/256 | 1.664e-09 | 0.015625 |
| quantum_no_entangle | 0.051404 | [0.042892, 0.059052] | 256.0/256 | 1.664e-09 | 0.010986 |
| quantum_dephased_control | 0.049805 | [0.041198, 0.059006] | 255.5/256 |  | 0.000000 |

## PASS criteria evaluation

```text
MAIN:
  direct_coupled bootstrap CI over seeds excludes 0:
  [0.044083, 0.055695]
  -> PASS

LEAKAGE CONTROL:
  no_entangle bootstrap CI includes 0:
  [-0.005814, 0.002976]
  sign split = +6 / -10
  -> PASS

SEPARATION:
  direct vs no_entangle Mann-Whitney U = 256.0/256
  one-sided exact p = 1.664e-09
  -> PASS
```

Auxiliary seed-level gap:

```text
direct_coupled min = 0.028320
no_entangle max    = 0.017334
gap                = 0.010986
```

## Verdict

```text
PASS_SIGNED_MULTI_SEED_WITNESS_SURVIVES
```

## Interpretation

The signed/oriented measurable witness survives across fresh shot-realization seeds:

```text
direct_coupled:
  exact = 0.046132
  mean  = 0.049988
  signs = +16 / -0

no_entangle:
  exact = 0
  mean  = -0.003922
  signs = +6 / -10
```

This supports the reading that the v1 `abs()` failure against `no_entangle` was an estimator/one-seed artifact, not a real no-entangle leakage path.

## Boundary

This is still not a QPU result and not a noise-model result.

```text
No quantum advantage is claimed.
No biological organization is claimed.
No matter synthesis is claimed.
```

## Next implication

The next justified step is v2 noise modeling of the signed/oriented witness. Do not submit to QPU until the witness survives the noise-floor test.
