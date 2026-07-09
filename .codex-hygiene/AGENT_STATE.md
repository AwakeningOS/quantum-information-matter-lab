# Agent State

## Current User Goal

Preserve Q-cell experiment code, verified findings, and next experiments in
GitHub so another agent can continue and the record can support later papers.

## Current Task

Record completed Q-cell controller evolution v0 and keep raw logs out of Git.

## Hard Constraints

- Do not commit multi-gigabyte raw logs.
- Separate energy-only `R3=|1>` from coherence-injecting `R4=|+>`.
- Preserve thermodynamic ledger and switching-cost caveats.
- No life, metabolism, purpose, self-repair, homeostasis, optimization, QPU,
  or quantum-advantage claim without a dedicated test.
- Incomplete Stage 1 must not be reported as a completed result.

## Current Repo / Directory

`/home/youthk/デスクトップ/quantum-information-matter-lab`

Branch: `codex/qcell-full2q7-and-bottleneck-record`

## Files Touched

- full 2^7 CPU/GPU runners
- corrected bottleneck GPU runner/postprocessor
- full 2^7 report and compact manifest
- bottleneck runner note
- Q-cell energy-machine roadmap
- `results/STATUS.md`
- `.codex-hygiene/*`

## Known Verified Facts

- Full CUDA run completed: 37 conditions, 100 initial states, 200 cycles.
- Full-run maximum absolute energy-balance residual: `1.154632e-13`.
- CPU/GPU smoke outputs agreed at order `1e-15`.
- Corrected bottleneck smoke completed with maximum residual `3.46e-14`.
- Bottleneck Stage 1 completed 1000/1000 grid points.
- Stage 1 paired rows: 10,000; all four variants present for every pair.
- Stage 1 maximum absolute energy-balance residual: `1.381117e-13`.
- Maximum attributed fixed output: `17.655558`; matched central `38.380659`.
- Stage 2 completed 28/28 selected grid points with 100 initial states.
- Stage 2 paired rows: 2,800; all four variants present for every pair.
- Stage 2 maximum absolute energy-balance residual: `1.394440e-13`.
- Stage 2 maximum attributed fixed output: `17.632414`; matched central
  `38.374395`.
- Stage 2 raw logs are stored outside Downloads and outside the repo at
  `/home/youthk/work/qcell_experiment_outputs/qcell_fixed_circuit_output_bottleneck_map_v0_stage2_outputs`.
- Local-controller v0 pilot completed 6 grids x 20 seeds.
- Local-controller v0 confirmation completed 3 grids x 100 seeds.
- In confirmation, `QFCBM_0988` internal controller attributed W
  `26.024037` vs fixed `15.840497`, beating shuffled-signal and time-shift
  controls in 100/100 seeds.
- In confirmation, `QFCBM_0496` internal controller attributed W `0.258512`
  vs fixed `0.055903`, beating shuffled-signal and time-shift controls in
  100/100 seeds.
- `QFCBM_0399` is marginal: gain over fixed positive, but only 64/100 seeds
  beat time-shift action.
- Controller evolution v0 completed with population 12, generations 4.
- Best evolved controller holdout mean gain: `4.553862`; hand-coded
  controller holdout mean gain: `3.324505`.
- Best evolved controller improved `QFCBM_0988` and `QFCBM_0496`; hand-coded
  remained slightly better on `QFCBM_0399`.
- Commit `8bd4ba6` was pushed and draft PR 29 was opened against the PR 28
  head branch.

## Current Blockers

None for controller evolution v0 execution. Compact results need commit/push.

Local Stage 1 output:

`/home/youthk/ダウンロード/qcell_fixed_circuit_output_bottleneck_map_v0_corrected_package/qcell_fixed_circuit_output_bottleneck_map_v0_stage1_outputs`

Local Stage 2 raw output:

`/home/youthk/work/qcell_experiment_outputs/qcell_fixed_circuit_output_bottleneck_map_v0_stage2_outputs`

## Next 1-3 Actions

1. Inspect controller evolution v0 diff.
2. Commit compact controller evolution v0 code/results/report.
3. Next research action: battery-powered actuator or fair quantum/classical
   comparison design, depending on user priority.

## Last Updated

2026-07-10 JST
