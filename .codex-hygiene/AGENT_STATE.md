# Agent State

## Current User Goal

Preserve Q-cell experiment code, verified findings, and next experiments in
GitHub so another agent can continue and the record can support later papers.

## Current Task

Publish full-2^7 validated artifacts and the corrected fixed-circuit
bottleneck-map runner while Stage 1 continues locally.

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
- Active bottleneck run had 443/1000 completed grid markers at last refresh.
- Commit `8bd4ba6` was pushed and draft PR 29 was opened against the PR 28
  head branch.

## Current Blockers

None. Stage 1 is still running and must be validated after completion.

Local Stage 1 output:

`/home/youthk/ダウンロード/qcell_fixed_circuit_output_bottleneck_map_v0_corrected_package/qcell_fixed_circuit_output_bottleneck_map_v0_stage1_outputs`

## Next 1-3 Actions

1. Complete and validate Stage 1; create compact corrected summaries.
2. Commit Stage 1 results in a follow-up without raw cyclewise logs.
3. Run representative Stage 2 regions with 100 initial states.

## Last Updated

2026-07-09 JST
