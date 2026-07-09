# Q-Cell Untamed Situation Observation v0 Report

Date: 2026-07-09
Layer: QUANTUM_OBSERVATION
Status: OBSERVATION_LOG
Experiment: `qcell_untamed_situation_observation_v0`

## Scope

This report records a broad, deliberately untuned observation run. It does not improve the v2 witness line, does not add noise-margin diagnostics, and does not move anything toward QPU readiness.

The parts are named `A/B/C/D` only. No membrane/core/residue/output role is assigned before the run.

## Run contents

```text
54 total situations
24 all-order A/B/C/D touch sequences
5 rhythm / stop / burst situations
8 damage / restore / rewire situations
5 topology mutation situations
7 initial-state / environment situations
5 two-mini-cell contact situations
```

The raw JSONL stores the full trajectory for every situation. Each snapshot contains part populations, full computational-basis population, all pair ZZ correlations, pair negativity, coherence, purity, entropy, operation history, and a simple classical parallel trace.

## What was observed, without promoting it

These are observations only, not claims of mechanism.

### All-order touch block

The 24 permutations did not collapse to one uniform response. Several orders produced large final part-population shifts and large pair-correlation changes.

Examples from the compact summary:

| Scenario | Family | Pattern | Max abs part P1 delta | Max abs ZZ delta | Max abs negativity delta | Δcoherence |
|---:|---|---|---:|---:|---:|---:|
| 12 | all_24_touch_orders | BDCA | 0.688346 | 0.771477 | 0.265389 | 2.132231 |
| 10 | all_24_touch_orders | BCDA | 0.687223 | 0.686584 | 0.246303 | 1.842847 |
| 22 | all_24_touch_orders | DBCA | 0.649669 | 0.822332 | 0.319795 | 2.850660 |
| 20 | all_24_touch_orders | DACB | 0.635814 | 0.624588 | 0.384861 | 4.311718 |

Do not read this as an order ranking. It only says that order changes the trajectory under this sandbox.

### Repetition / burst / stop block

The strongest coherence increase in this family appeared in `fast_repeat_A`.

```text
scenario 25 fast_repeat_A
Δcoherence = 5.127871
max abs ZZ delta = 0.616683
max abs negativity delta = 0.190231
```

The largest purity loss in this family appeared in `burst_then_idle`.

```text
scenario 28 burst_then_idle
Δpurity = -0.739704
Δcoherence = -2.697425
max abs ZZ delta = 0.654089
```

This is not called self-oscillation, fatigue, repair, or overdrive. The raw trace simply records repeated stimulation, abrupt strengthening, idling, and the resulting trajectory.

### Damage / restore / rewire block

The `cut_middle_then_reconnect` situation produced one of the larger pair-correlation changes in this block.

```text
scenario 37 cut_middle_then_reconnect
max abs ZZ delta = 1.083095
max abs negativity delta = 0.286851
Δcoherence = 3.111256
```

Deletion and restoration situations are recorded as operation histories. The report does not claim that the system repaired itself.

### Topology mutation block

`ring` and `star_B` produced large coherence changes under the chosen operations.

```text
scenario 38 ring
Δcoherence = 4.282908
max abs ZZ delta = 0.709096

scenario 41 star_B
Δcoherence = 4.714847
max abs ZZ delta = 0.420688
```

This is a topology observation only.

### Initial-state / environment block

Initial-state variation produced some of the largest pair-correlation changes in the run.

```text
scenario 44 biased_left
max abs ZZ delta = 1.488708
Δcoherence = 5.074479
Δpurity = -0.391349

scenario 43 empty
max abs ZZ delta = 1.467166
Δcoherence = 8.898063
Δpurity = -0.275384

scenario 45 biased_right
max abs ZZ delta = 1.440597
Δcoherence = 6.455115
Δpurity = -0.374101
```

This says the starting condition mattered. It does not say why.

### Two-mini-cell contact block

The contact block uses the same four unnamed parts as two two-part mini-cells: `AB` and `CD`, with `BC` as the contact link when contact is enabled.

```text
scenario 50 touch_A_contact_BC
max abs part P1 delta = 0.647690
max abs ZZ delta = 1.020200
max abs negativity delta = 0.309114
Δcoherence = 1.242911
```

This is a contact/separation observation only. It is not a claim of exchange, synchronization, competition, or biological interaction.

## Classical parallel trace

A simple classical trajectory is saved beside every quantum trajectory. It is included as context, not as a winner/loser comparison. The classical trace records part values, pair centered-products, mean value, entropy-like bit measure, and active links.

## Raw files

```text
data/quantum_observation/qcell_untamed_situation_observation_v0_seed20260709.jsonl
data/quantum_observation/qcell_untamed_situation_observation_v0_seed20260709_summary.csv
data/quantum_observation/qcell_untamed_situation_observation_v0_seed20260709_manifest.json
```

## What this run does not conclude

```text
No PASS/FAIL.
No ranking.
No witness promotion.
No QPU-ready claim.
No quantum advantage claim.
No life/cell/consciousness claim.
No explanation that a pattern is intrinsic rather than operation-induced.
```

## Status

OBSERVATION_LOG only.
