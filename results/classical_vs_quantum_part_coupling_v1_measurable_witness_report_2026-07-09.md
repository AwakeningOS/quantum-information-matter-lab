# classical_vs_quantum_part_coupling_v1_measurable_witness Report

Date: 2026-07-09

Status: OBSERVATION_LOG

Protocol:

```text
experiments/classical_vs_quantum_part_coupling_v1_protocol_20260709.md
```

Raw log:

```text
data/quantum_observation/classical_vs_quantum_part_coupling_v1_seed20260709.json
```

Summary:

```text
data/quantum_observation/classical_vs_quantum_part_coupling_v1_seed20260709_summary.csv
```

## P0 correction to v0

v0 phase-context sensitivity injected Rz phase on all four qubits. v1 corrects this weakness by locking:

```text
phase injection = M only
readout = W only
path = M-C / C-R / R-W link evolution
```

Dephasing is inserted during propagation, after each full M-C/C-R/R-W link layer, not only before readout.

## Witnesses

```text
MAIN:
  phase_sens_P1W = |P1_W(phaseM=pi/2, M perturb) - P1_W(phaseM=0, M perturb)|

SECONDARY:
  output_nonadditivity_P1W = |P1_W(M+C) - P1_W(M) - P1_W(C) + P1_W(base)|

DIAGNOSTIC:
  output_nonadditivity_ZZRW = |<Z_R Z_W>(M+C) - <Z_R Z_W>(M) - <Z_R Z_W>(C) + <Z_R Z_W>(base)|

AUXILIARY ONLY:
  link_negativity
```

## Exact ideal values

| arm | phase_sens_P1W | nonadd_P1W | nonadd_ZZRW | aux link negativity max |
|---|---:|---:|---:|---:|
| classical_if | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| classical_coupled | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| quantum_field_only | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| quantum_no_entangle | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| quantum_direct_coupled | 0.046132 | 0.000025 | 0.033989 | 0.137535 |
| quantum_dephased_control | 0.000115 | 0.000003 | 0.001772 | 0.000000 |

## 4096-shot observed values

| arm | phase_sens_P1W_shot | nonadd_P1W_shot | nonadd_ZZRW_shot |
|---|---:|---:|---:|
| classical_if | 0.000000 | 0.000000 | 0.000000 |
| classical_coupled | 0.000000 | 0.000000 | 0.000000 |
| quantum_field_only | 0.007812 | 0.009277 | 0.025879 |
| quantum_no_entangle | 0.020752 | 0.011719 | 0.016113 |
| quantum_direct_coupled | 0.048584 | 0.020996 | 0.095215 |
| quantum_dephased_control | 0.009033 | 0.026123 | 0.041016 |

## Bootstrap comparisons: direct - control

### phase_sens_P1W

| control | mean | 95% CI | excludes 0? |
|---|---:|---:|---:|
| classical_if | 0.048271 | [0.028320, 0.068365] | yes |
| classical_coupled | 0.048271 | [0.028320, 0.068365] | yes |
| quantum_field_only | 0.037353 | [0.010736, 0.061774] | yes |
| quantum_no_entangle | 0.027164 | [-0.000018, 0.055682] | no |
| quantum_dephased_control | 0.036479 | [0.008539, 0.060559] | yes |

### output_nonadditivity_P1W

| control | mean | 95% CI | excludes 0? |
|---|---:|---:|---:|
| classical_if | 0.022227 | [0.001221, 0.050293] | yes |
| classical_coupled | 0.022227 | [0.001221, 0.050293] | yes |
| quantum_field_only | 0.007532 | [-0.024182, 0.041022] | no |
| quantum_no_entangle | 0.006343 | [-0.028339, 0.039801] | no |
| quantum_dephased_control | -0.004649 | [-0.042975, 0.034436] | no |

### output_nonadditivity_ZZRW

| control | mean | 95% CI | excludes 0? |
|---|---:|---:|---:|
| classical_if | 0.096231 | [0.039038, 0.150916] | yes |
| classical_coupled | 0.096231 | [0.039038, 0.150916] | yes |
| quantum_field_only | 0.063870 | [-0.014160, 0.134302] | no |
| quantum_no_entangle | 0.068000 | [-0.003906, 0.132336] | no |
| quantum_dephased_control | 0.052003 | [-0.028320, 0.126489] | no |

## Derived observations

```text
dephase_reduction_phase_sens_exact = 0.997515880115
dephase_reduction_nonadd_P1W_exact = 0.89681770922
dephase_reduction_ZZRW_exact       = 0.947874375768
```

Exact ideal simulation says the M-only phase witness is transferred to W population in `quantum_direct_coupled`, while `quantum_field_only` and `quantum_no_entangle` remain exactly zero. Dephasing during propagation almost completely kills the exact signal.

However, with 4096-shot sampling and bootstrap, the key `direct - no_entangle` phase_sens_P1W CI is:

```text
[-0.000018, 0.055682]
```

This barely crosses zero. Therefore the main witness does **not** satisfy the pre-registered KEEP rule at 4096 shots.

## Verdict

```text
WITNESS_COLLAPSED_ON_REPLACEMENT
```

More precise wording:

```text
The ideal measurable witness survives the negativity-to-output replacement, but the 4096-shot keep rule does not pass against the no_entangle control.
```

This is not a QPU-ready witness yet.

## Interpretation

What survived:

```text
M-only phase injection -> W population change appears only in direct-coupled ideal simulation.
field_only and no_entangle are exactly zero in ideal values.
dephased control strongly reduces the exact signal.
```

What failed:

```text
4096-shot bootstrap could not separate direct from no_entangle with a CI excluding zero.
P1W nonadditivity is too small in exact value and should not be promoted.
ZZRW nonadditivity is larger in exact value but not bootstrap-robust against quantum controls at 4096 shots.
```

## Next implication

Do not submit this v1 to QPU yet.

The next safe move is either:

```text
v1b: same protocol, increase shots / optimize circuit margin without moving thresholds
```

or:

```text
v2: add noise model only after a witness passes the ideal shot-bootstrap keep rule
```

No quantum advantage, biological organization, or matter synthesis is claimed.
