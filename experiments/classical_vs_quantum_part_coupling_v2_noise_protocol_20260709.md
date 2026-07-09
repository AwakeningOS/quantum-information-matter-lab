# Protocol: classical_vs_quantum_part_coupling_v2_noise_model

Date: 2026-07-09

Layer: QUANTUM_OBSERVATION -> QUANTUM_AUDIT candidate

Status: PRE-REGISTERED BEFORE V2 NOISE RUN

Generator planned:

```text
scripts/quantum_observation/classical_vs_quantum_part_coupling_v2_noise_model.py
```

Raw log planned:

```text
data/quantum_observation/classical_vs_quantum_part_coupling_v2_noise_seed20260741_20260756.json
```

Summary CSV planned:

```text
data/quantum_observation/classical_vs_quantum_part_coupling_v2_noise_seed20260741_20260756_summary.csv
```

## P0: input from v1a

v1a promoted the signed/oriented measurable witness to a noise-model candidate, not to QPU.

```text
oriented_phase_effect_P1W =
  P1_W(phaseM=0, M perturb) - P1_W(phaseM=pi/2, M perturb)
```

v1a passed with fresh seeds 20260725-20260740 using seed-level inference:

```text
direct_coupled mean = 0.049988, CI [0.044083, 0.055695], signs +16/-0
no_entangle mean    = -0.003922, CI [-0.005814, 0.002976], signs +6/-10
```

v2 asks only whether this witness survives simple noise models. It does not submit to QPU.

## Fresh-seed guard

Do not reuse v1a diagnostic or v1a formal seeds.

```text
v1a diagnostic seeds = 20260709-20260716
v1a formal seeds     = 20260725-20260740
v2 noise seeds       = 20260741-20260756
```

## Fixed circuit and estimator

Same circuit family as v1a:

```text
qubits = M,C,R,W
phase injection = M only
readout = W only
estimator = P1_W(phaseM=0,M perturb) - P1_W(phaseM=pi/2,M perturb)
inference unit = seed
shots per seed = 4096
seed count = 16
```

## Arms

```text
quantum_field_only
quantum_no_entangle
quantum_direct_coupled
quantum_dephased_control
```

`field_only` and `no_entangle` are both retained.

## Noise profiles

The noise model is deliberately simple and pre-hardware:

```text
none:
  p_dephase_layer = 0.000
  p_depolarize_1q = 0.000
  p_depolarize_2q = 0.000
  p_readout_flip  = 0.000

light:
  p_dephase_layer = 0.003
  p_depolarize_1q = 0.001
  p_depolarize_2q = 0.004
  p_readout_flip  = 0.010

medium:
  p_dephase_layer = 0.008
  p_depolarize_1q = 0.003
  p_depolarize_2q = 0.012
  p_readout_flip  = 0.025

heavy:
  p_dephase_layer = 0.018
  p_depolarize_1q = 0.007
  p_depolarize_2q = 0.030
  p_readout_flip  = 0.050
```

The `dephased_control` arm still applies its strong propagation dephase from v1/v1a; the profile noise is additional.

## PASS criteria per noise profile

For a profile to be considered surviving:

```text
MAIN:
  direct_coupled seed bootstrap CI excludes 0.

LEAKAGE CONTROL:
  no_entangle seed bootstrap CI includes 0 and sign split is not all-same.

SEPARATION:
  direct - no_entangle paired seed bootstrap CI excludes 0
  and Mann-Whitney one-sided separation is p < 0.01 when U is maximal.
```

Auxiliary 5% floor rule:

```text
Log the absolute noise-floor proxy:
  floor = max(abs(mean(field_only)), abs(mean(no_entangle)), abs(mean(dephased_control)))

If floor >= 0.05, mark the profile as FLOOR_TOO_HIGH even if separation appears.
```

The 5% floor rule is a guard against promoting a profile where controls themselves show large apparent phase effects.

## Overall v2 verdict labels

```text
PASS_NOISE_MODEL_CANDIDATE:
  none, light, and medium all survive; no profile among light/medium has FLOOR_TOO_HIGH.

PARTIAL_NOISE_MODEL_CANDIDATE:
  none and light survive, but medium fails.

NOISE_MODEL_FRAGILE:
  none survives but light fails.

NOISE_MODEL_REJECT:
  none fails or leakage controls fail.
```

Heavy noise is diagnostic only. Failure under heavy noise does not by itself reject the witness.

## Boundary

```text
no QPU submission
no quantum advantage claim
no biological organization claim
no matter synthesis claim
```
