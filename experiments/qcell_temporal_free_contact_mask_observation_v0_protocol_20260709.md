# Q-Cell Temporal / Free / Contact / Metric-Mask Observation v0 Protocol

Date: 2026-07-09
Layer: QUANTUM_OBSERVATION
Status: OBSERVATION_LOG
Experiment: `qcell_temporal_free_contact_mask_observation_v0`

## Purpose

Add four observation axes without converting the work into PASS/FAIL, ranking, witness promotion, or QPU-readiness.

The axes are:

```text
1. time-resolution event detection
2. free observation after operation release
3. wide two-body contact scan
4. metric masking of observation quantities
```

## Non-goals

```text
No PASS/FAIL.
No ranking.
No witness promotion.
No QPU-ready claim.
No quantum advantage claim.
No life/cell/consciousness claim.
No role assignment to A/B/C/D.
No claim that a pattern is intrinsic rather than operation-induced.
```

## Seed block

Use the same seed block as the instability sweep:

```text
20260710-20260719
```

## Axis 1: Time resolution expansion

Instead of only recording final values, record event timing:

```text
first_branch_step_part025
first_branch_step_ZZ035
first_branch_step_neg010
coherence_reversal_count
purity_reversal_count
ZZ_path_reversal_count
stall_start_step
```

These are mechanical event markers, not claims.

## Axis 2: Free observation after operation release

After stimulus/contact/disturbance is removed, keep recording the trajectory under internal propagation only.

Record:

```text
post_release_len
post_release_final_part_shift
post_release_final_ZZ_shift
post_release_final_coherence_shift
```

Do not name this recovery, memory, adaptation, or repair.

## Axis 3: Two-body contact wide scan

Scan contact point, contact duration, contact strength, and whether contact is released followed by free observation.

Contact pairs:

```text
AC, AD, BC, BD
```

Durations:

```text
1, 4, 8
```

Strength values:

```text
0.4, 1.1
```

Release/free lengths:

```text
0, 8
```

## Axis 4: Metric masking

Create mechanical observation signatures with one observable group hidden at a time:

```text
full
hide_negativity
hide_classical
hide_population
hide_ZZ
hide_coherence
hide_purity
hide_negativity_and_classical
```

This checks whether the visible map is being produced mainly by a particular observer-side quantity.

## Output files

```text
scripts/quantum_observation/qcell_temporal_free_contact_mask_observation_v0.py

data/quantum_observation/qcell_temporal_free_contact_mask_observation_v0_seed20260710_20260719.jsonl
data/quantum_observation/qcell_temporal_free_contact_mask_observation_v0_seed20260710_20260719_events.csv
data/quantum_observation/qcell_temporal_free_contact_mask_observation_v0_seed20260710_20260719_metric_masks.csv
data/quantum_observation/qcell_temporal_free_contact_mask_observation_v0_seed20260710_20260719_manifest.json

results/qcell_temporal_free_contact_mask_observation_v0_report_2026-07-09.md
```

## Reporting rule

Report raw event times and raw ranges. Do not promote conclusions.
