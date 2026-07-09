# classical_vs_quantum_part_coupling_v1a_signed_seed_sweep_diagnostic Report

Date: 2026-07-09

Status: OBSERVATION_LOG

Scope:

```text
pre-protocol diagnostic only
not a PASS/FAIL promotion
not a QPU-ready claim
```

## Purpose

v1 used an absolute-value estimator:

```text
abs(P1_W(phaseM=pi/2) - P1_W(phaseM=0))
```

That creates a positive shot-noise bias even when the true effect is zero. This diagnostic checks whether the `quantum_no_entangle` v1 apparent effect was caused by that one-seed absolute-value bias.

## Fixed oriented estimator

```text
oriented_phase_effect_P1W =
  P1_W(phaseM=0, M perturb) - P1_W(phaseM=pi/2, M perturb)
```

Orientation lock:

```text
v1 exact signed effect under P1_W(pi/2) - P1_W(0) was negative for direct_coupled.
Therefore this diagnostic reports P1_W(0) - P1_W(pi/2) so the direct effect is positive.
This orientation is fixed before the multi-seed shot sweep and is not selected after seed-level outcomes.
```

## Config

```text
shots = 4096
seeds = 20260709, 20260710, 20260711, 20260712, 20260713, 20260714, 20260715, 20260716
arms = quantum_field_only, quantum_no_entangle, quantum_direct_coupled, quantum_dephased_control
```

## Seed-level oriented effects

| seed | field_only | no_entangle | direct_coupled | dephased |
|---:|---:|---:|---:|---:|
| 20260709 | 0.001465 | 0.000488 | 0.044189 | 0.011230 |
| 20260710 | -0.002930 | 0.013916 | 0.044922 | -0.001953 |
| 20260711 | -0.009766 | -0.022705 | 0.044922 | 0.025391 |
| 20260712 | 0.007812 | -0.008545 | 0.026367 | -0.007324 |
| 20260713 | 0.005859 | 0.009766 | 0.036377 | 0.010254 |
| 20260714 | 0.008789 | -0.020264 | 0.032959 | 0.000488 |
| 20260715 | -0.018799 | -0.013916 | 0.038574 | 0.007324 |
| 20260716 | 0.021729 | 0.009521 | 0.043701 | -0.028076 |

## Summary

| arm | exact | mean | std | min | max | signs |
|---|---:|---:|---:|---:|---:|---|
| quantum_field_only | 0.000000 | 0.001770 | 0.012416 | -0.018799 | 0.021729 | +5 / -3 / 0=0 |
| quantum_no_entangle | 0.000000 | -0.003967 | 0.014377 | -0.022705 | 0.013916 | +4 / -4 / 0=0 |
| quantum_direct_coupled | 0.046132 | 0.039001 | 0.006786 | 0.026367 | 0.044922 | +8 / -0 / 0=0 |
| quantum_dephased_control | 0.000115 | 0.002167 | 0.015757 | -0.028076 | 0.025391 | +5 / -3 / 0=0 |

## Reading

```text
quantum_no_entangle:
  exact = 0
  seed signs = +4 / -4
  mean = -0.003967
  min/max = [-0.022705, 0.013916]

quantum_direct_coupled:
  exact = 0.046132
  seed signs = +8 / -0
  mean = 0.039001
  min/max = [0.026367, 0.044922]
```

In this 8-seed diagnostic, `no_entangle` returns to a zero-centered distribution, while `direct_coupled` stays positive for every seed.

A useful separation also appears at the seed-effect level:

```text
direct_coupled min = 0.026367
no_entangle max    = 0.013916
```

So the v1 failure against no_entangle is consistent with an absolute-value / single-shot-realization bias rather than a real no_entangle leakage path.

## Diagnostic verdict

```text
SEED_SWEEP_SUPPORTS_SIGNED_V1A
```

## Implication

The next formal step should be:

```text
v1a:
  pre-register signed/oriented estimator
  keep shots = 4096
  use multi-seed or pooled-seed inference
  require direct effect > 0 while no_entangle remains zero-centered
```

Do not move to a noise model yet. Do not submit to QPU yet.
