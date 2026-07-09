# Q-Cell Untamed Situation Observation v0 Protocol

Date: 2026-07-09
Layer: QUANTUM_OBSERVATION
Status: OBSERVATION_LOG
Experiment: `qcell_untamed_situation_observation_v0`

## Purpose

Throw many odd situations at a small Q-cell sandbox and record what happens.

This is not a witness experiment, not a performance experiment, not a QPU-readiness path, and not a regime-ranking task. The parts are named only `A/B/C/D`; they have no pre-assigned membrane/core/residue/output roles.

## Non-goals

- No v2 witness improvement.
- No noise-margin improvement.
- No QPU-ready conversion.
- No single-score extraction.
- No PASS/FAIL outcome.
- No ranking of situations.
- No claim of life, consciousness, quantum advantage, or hardware readiness.

## Observation policy

The experiment keeps the raw trajectories. The report may describe visible changes, but must not explain them as completed mechanisms.

Allowed wording:

```text
scenario X showed a large change in pair ZZ or population under this operation history.
```

Avoid:

```text
scenario X proves repair, memory, life, or quantum advantage.
```

## Situation families

The run includes 54 situations:

```text
24 all_24_touch_orders
5 rhythm_stop_burst
8 damage_restore_rewire
5 topology_mutation
7 initial_environment_variation
5 two_cell_contact
```

The all-order block intentionally includes every permutation of touching A/B/C/D once. No order is selected or promoted.

## Recorded per scenario

Each JSONL record contains:

```text
scenario settings
seed
generation settings
operation history
full trajectory snapshots
classical parallel trace
```

Each trajectory snapshot contains:

```text
part_P1 for all parts
population over all computational-basis states
all pair ZZ correlations
all pair negativity values
l1_coherence
purity
entropy_vn
classical parallel part values and pair centered-products
```

## Classical parallel trace

The classical trace is kept only as nearby context. It is not used as a win/loss comparison and not used as a promotion gate.

## Output files

```text
scripts/quantum_observation/qcell_untamed_situation_observation_v0.py

data/quantum_observation/qcell_untamed_situation_observation_v0_seed20260709.jsonl
data/quantum_observation/qcell_untamed_situation_observation_v0_seed20260709_summary.csv
data/quantum_observation/qcell_untamed_situation_observation_v0_seed20260709_manifest.json

results/qcell_untamed_situation_observation_v0_report_2026-07-09.md
```

## Validity checks

The run is valid as an observation log if:

```text
all planned scenarios are present
all scenarios contain operation history
all scenarios contain at least initial and final trajectory snapshots
all snapshots contain part values, population, pair ZZ, coherence, purity, entropy
no PASS/FAIL verdict is emitted
```
