# Protocol: classical_vs_quantum_part_coupling_v1a_formal_signed_witness

Date: 2026-07-09

Layer: QUANTUM_OBSERVATION -> QUANTUM_AUDIT candidate

Status: PRE-REGISTERED AFTER DIAGNOSTIC, BEFORE FORMAL FRESH-SEED RUN

Generator planned:

```text
scripts/quantum_observation/classical_vs_quantum_part_coupling_v1a_formal_signed_witness.py
```

Raw log planned:

```text
data/quantum_observation/classical_vs_quantum_part_coupling_v1a_formal_seed20260725_20260740.json
```

Summary CSV planned:

```text
data/quantum_observation/classical_vs_quantum_part_coupling_v1a_formal_seed20260725_20260740_summary.csv
```

## P0: relation to v1 and v1a diagnostic

v1 used:

```text
abs(P1_W(phaseM=pi/2) - P1_W(phaseM=0))
```

That absolute-value estimator creates a positive shot-noise bias for zero-truth controls.

The v1a seed-sweep diagnostic was used only to check estimator behavior. It is not promoted as the formal result. The formal v1a run uses a fresh seed block:

```text
diagnostic seeds: 20260709-20260716
formal seeds:     20260725-20260740
```

## Orientation lock

v1 exact signed effect under:

```text
P1_W(phaseM=pi/2) - P1_W(phaseM=0)
```

was negative for direct_coupled. Therefore v1a reports the oriented effect:

```text
oriented_phase_effect_P1W =
  P1_W(phaseM=0, M perturb) - P1_W(phaseM=pi/2, M perturb)
```

This orientation is fixed before the fresh-seed formal run. It is not chosen after inspecting formal seed outcomes.

## Fixed circuit structure

```text
qubits: M, C, R, W
phase injection point = M only
readout point = W only
path = M-C / C-R / R-W link evolution
```

Phase MUST NOT be injected on C, R, or W.

## Arms

```text
quantum_field_only
quantum_no_entangle
quantum_direct_coupled
quantum_dephased_control
```

`field_only` and `no_entangle` are both retained because they test different controls:

```text
field_only  = common drive is insufficient
no_entangle = directional link is required
```

## Inference unit

Use seed-level inference.

```text
shots per seed = 4096
formal seeds = 16
seed block = 20260725-20260740
```

Do NOT pool all shots into one larger pseudo-experiment for the primary inference. Each seed contributes one oriented effect. This tests whether the witness survives independent shot realizations.

## Primary witness

```text
oriented_phase_effect_P1W =
  P1_W(phaseM=0, M perturb) - P1_W(phaseM=pi/2, M perturb)
```

## PASS criteria

```text
MAIN:
  quantum_direct_coupled seed-level mean > 0
  and the 95% bootstrap CI over seeds excludes 0.

LEAKAGE CONTROL:
  quantum_no_entangle seed-level 95% bootstrap CI includes 0
  and sign split is not all-same.

SEPARATION:
  quantum_direct_coupled distribution is greater than quantum_no_entangle distribution
  by one-sided Mann-Whitney U with p < 0.01.

SUPPORTING CONTROLS:
  field_only remains zero-centered.
  dephased_control remains near-zero and direct - dephased seed bootstrap CI excludes 0.
```

`min(direct) > max(no_entangle)` is logged as a useful auxiliary check, not the primary criterion.

## Verdict labels

```text
PASS_SIGNED_MULTI_SEED_WITNESS_SURVIVES
PARTIAL_SIGNED_WITNESS_SURVIVES
SIGNED_WITNESS_NOT_SEPARATED
SIGNED_WITNESS_LEAKAGE_SUSPECTED
```

## Out of scope

```text
no noise model
no QPU submission
no quantum advantage claim
no biological organization claim
no matter synthesis claim
```
