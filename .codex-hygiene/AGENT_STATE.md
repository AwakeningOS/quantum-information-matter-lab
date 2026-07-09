# Agent State

## Current User Goal

Preserve Q-cell experiment code, verified findings, and next experiments in
GitHub so another agent can continue and the record can support later papers.

## Current Task

Record the completed corrected fixed-circuit Stage 2 confirmation and keep
raw multi-gigabyte logs out of Git.

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
- Commit `8bd4ba6` was pushed and draft PR 29 was opened against the PR 28
  head branch.

## Current Blockers

None for Stage 2 execution. Compact results need commit/push if the user wants
PR 29 updated.

Local Stage 1 output:

`/home/youthk/ダウンロード/qcell_fixed_circuit_output_bottleneck_map_v0_corrected_package/qcell_fixed_circuit_output_bottleneck_map_v0_stage1_outputs`

Local Stage 2 raw output:

`/home/youthk/work/qcell_experiment_outputs/qcell_fixed_circuit_output_bottleneck_map_v0_stage2_outputs`

## Next 1-3 Actions

1. Inspect Stage 2 git diff.
2. Commit compact Stage 2 summaries/report and runner CLI update.
3. Push PR 29 update if appropriate.

## Last Updated

2026-07-10 JST
