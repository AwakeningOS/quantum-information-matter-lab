# Q-Cell Seed Instability and Expanded Situation Sweep v0 Protocol

Date: 2026-07-09
Layer: QUANTUM_OBSERVATION
Status: OBSERVATION_LOG
Experiment: `qcell_seed_instability_and_expanded_situations_v0`

## Purpose

Run the same untamed Q-cell situations across seeds `20260710` through `20260719` to find situations whose trajectories vary across seeds.

This is not a reproducibility certification. Stable situations may be ignored in the report. The purpose is to surface conditions where the same macro-operation produces divided or high-spread trajectories.

## Inputs

The first block reuses the 54 macro-situations from:

```text
qcell_untamed_situation_observation_v0
```

The second block adds 21 macro-situations along missing axes:

```text
external periodic/burst drive
three/four node chain/ring contact
measurement timing as intervention
duplication-like/asymmetric situations
```

Total:

```text
75 macro-situations × 10 seeds = 750 records
```

## Seed policy

Seeds are:

```text
20260710, 20260711, 20260712, 20260713, 20260714,
20260715, 20260716, 20260717, 20260718, 20260719
```

The macro-situation is held fixed. Seed controls microscopic preparation jitter plus the existing random-product / depolarize randomness. The seed is not used to judge reproducibility.

## Recording policy

For every seed and macro-situation, save the full JSONL record, including:

```text
scenario settings
seed
generation settings
operation history
full trajectory snapshots
part P1 values
full computational-basis population
all pair ZZ correlations
all pair negativity values
coherence
purity
entropy
classical parallel trace
```

## Report policy

The report should show:

```text
seed-spread situations
new-axis situations with large raw changes
raw min/max/range/std numbers
```

The report must not assign PASS/FAIL, winner, proof, QPU-readiness, quantum advantage, life/cell/consciousness claims, or cause-complete explanations.

## Output files

```text
scripts/quantum_observation/qcell_seed_instability_and_expanded_situations_v0.py

data/quantum_observation/qcell_seed_instability_and_expanded_situations_v0_seed20260710_20260719.jsonl
data/quantum_observation/qcell_seed_instability_and_expanded_situations_v0_seed20260710_20260719_summary.csv
data/quantum_observation/qcell_seed_instability_and_expanded_situations_v0_seed20260710_20260719_seed_volatility.csv
data/quantum_observation/qcell_seed_instability_and_expanded_situations_v0_seed20260710_20260719_manifest.json

results/qcell_seed_instability_and_expanded_situations_v0_report_2026-07-09.md
```
