# Q-Cell Seed Instability and Expanded Situation Sweep v0 Report

Date: 2026-07-09
Layer: QUANTUM_OBSERVATION
Status: OBSERVATION_LOG
Experiment: `qcell_seed_instability_and_expanded_situations_v0`

## Scope

This run uses seeds `20260710` through `20260719`. The purpose is not to certify reproducibility. The purpose is to find situations whose trajectories vary across seeds.

No PASS/FAIL, no ranking, no witness promotion, no QPU-ready claim.

## Run shape

```text
54 original untamed situations
21 added-axis situations
75 macro-situations total
10 seeds
750 JSONL records
```

Added axes:

```text
external periodic/burst drive
three/four node chain/ring contact
measurement timing as intervention
duplication-like/asymmetric situations
```

Seed control:

```text
same macro-situation
seed controls microscopic preparation jitter plus existing random-product/depolarize randomness
```

## Seed-spread situations

The following are the largest seed-spread rows from the volatility table. These are not winners. They are places where the same macro-situation changed most across seeds.

| scenario | scope | family | pattern | Δcoherence min | Δcoherence max | Δcoherence range | max abs ZZ min | max abs ZZ max | max abs ZZ range | coherence signs |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---|
| 47 | original_54 | initial_environment_variation | random_product | -3.735810 | 6.695436 | 10.431246 | 1.020937 | 1.612454 | 0.591518 | +9/-1/0 |
| 29 | original_54 | rhythm_stop_burst | stop_then_reverse_phase | 1.898891 | 2.748754 | 0.849862 | 0.481852 | 0.570521 | 0.088669 | +10/-0/0 |
| 51 | original_54 | two_cell_contact | separate_recontact | 1.841836 | 2.684932 | 0.843096 | 0.890265 | 0.947725 | 0.057460 | +10/-0/0 |
| 49 | original_54 | initial_environment_variation | seed_entangled | -4.375335 | -3.545167 | 0.830169 | 0.929687 | 0.981470 | 0.051783 | +0/-10/0 |
| 26 | original_54 | rhythm_stop_burst | slow_repeat_A | 1.892445 | 2.720017 | 0.827572 | 0.812336 | 0.867311 | 0.054975 | +10/-0/0 |
| 1019 | expanded_axes | duplication_asymmetry | one_part_overdriven_B | 2.158565 | 2.973199 | 0.814634 | 0.907865 | 0.997324 | 0.089459 | +10/-0/0 |
| 54 | original_54 | two_cell_contact | shared_noise_then_contact | 0.201947 | 1.016030 | 0.814083 | 0.579667 | 0.635648 | 0.055981 | +10/-0/0 |
| 27 | original_54 | rhythm_stop_burst | irregular_ABCD | 3.433738 | 4.240290 | 0.806551 | 0.748727 | 0.803383 | 0.054656 | +10/-0/0 |

## Added-axis raw observations

These are single-seed extrema inside the added-axis block. They are raw observations only.

### External periodic / burst drive

```text
square_all_fast_toxic:
  seed 20260710
  delta_l1_coherence = -8.659396
  delta_purity = -0.937207

sin_A_period2:
  seed 20260710
  max_abs_ZZ_delta = 0.748154

sin_A_period5:
  seed 20260710
  max_abs_part_P1_delta = 0.448387
```

### Three/four node chain/ring contact

```text
three_node_ring_ABC:
  seed 20260710
  delta_l1_coherence = 3.730641

three_node_chain_AB_BC:
  seed 20260710
  max_abs_ZZ_delta = 0.713884
  max_abs_part_P1_delta = 0.545205
```

### Measurement timing intervention

```text
measure_A_each_step:
  seed 20260710
  delta_l1_coherence = 3.306734

sparse_edge_measure:
  seed 20260710
  max_abs_ZZ_delta = 1.048288

late_measure_all_then_continue:
  seed 20260710
  max_abs_part_P1_delta = 0.626150
```

### Duplication-like / asymmetric situations

```text
one_part_overdriven_B:
  seed range 20260710-20260719
  delta_l1_coherence min = 2.158565
  delta_l1_coherence max = 2.973199
  max_abs_ZZ_delta min = 0.907865
  max_abs_ZZ_delta max = 0.997324

asymmetric_long_link_AD:
  seed 20260710
  delta_l1_coherence = 4.089668

one_part_suppressed_C:
  seed 20260710
  delta_purity = -0.015776
  max_abs_part_P1_delta = 0.502457
```

## Raw files

```text
data/quantum_observation/qcell_seed_instability_and_expanded_situations_v0_seed20260710_20260719.jsonl
data/quantum_observation/qcell_seed_instability_and_expanded_situations_v0_seed20260710_20260719_summary.csv
data/quantum_observation/qcell_seed_instability_and_expanded_situations_v0_seed20260710_20260719_seed_volatility.csv
data/quantum_observation/qcell_seed_instability_and_expanded_situations_v0_seed20260710_20260719_manifest.json
```

## Non-claims

```text
No PASS/FAIL.
No ranking.
No witness promotion.
No QPU-ready claim.
No quantum advantage claim.
No life/cell/consciousness claim.
No explanation that a pattern is intrinsic rather than operation-induced.
```
