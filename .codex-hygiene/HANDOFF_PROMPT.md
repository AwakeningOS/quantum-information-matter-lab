# Handoff Prompt

## User Goal

Maintain a paper-ready, evidence-backed Q-cell research record in GitHub and
continue toward locally coordinated, resource-driven information machinery.

## Current Task

Finish and analyze `qcell_fixed_circuit_output_bottleneck_map_v0` Stage 1.

## Hard Constraints

- Do not commit multi-gigabyte raw logs.
- Do not treat `R4=|+>` coherence injection as energy-only battery behavior.
- Preserve resource/no-resource pairing and matched central controls.
- Account for energy ledger and unmodeled switching cost.
- No life, purpose, metabolism, homeostasis, autonomous optimization, QPU, or
  quantum-advantage claim without its dedicated experiment.

## Verified Facts

- Full 2^7 CUDA run completed and passed numerical validation.
- Main ring `R3` cumulative W output: `0.458287`.
- Matched central-control comparison: `1.027726`.
- Chain baseline: `0.361389`; classical transport: `0.388945`.
- Full-run maximum ledger residual: `1.154632e-13`.
- Corrected bottleneck runner smoke passed with residual `3.46e-14`.
- Stage 1 had 400/1000 completed grids at last evidence refresh.

## Files Touched

- `scripts/quantum_observation/qcell_local_linked_energy_machine_full2q7_final_v0*.py`
- `scripts/quantum_observation/qcell_fixed_circuit_output_bottleneck_map_v0*.py`
- `results/qcell_local_linked_energy_machine_full2q7_final_v0_report_2026-07-09.md`
- `results/qcell_fixed_circuit_output_bottleneck_map_v0_runner_note_2026-07-09.md`
- `docs/qcell/Q_CELL_ENERGY_MACHINE_ROADMAP_20260709.md`
- `data/quantum_observation/qcell_local_linked_energy_machine_full2q7_final_v0_manifest.json`

## Current Status

Stage 1 is running locally with atomic per-grid files and `--resume`. The
GitHub branch records code and verified completed work, not unfinished claims.

Local output directory:

`/home/youthk/ダウンロード/qcell_fixed_circuit_output_bottleneck_map_v0_corrected_package/qcell_fixed_circuit_output_bottleneck_map_v0_stage1_outputs`

## Next Actions

1. Count `parts/*_complete.json`; require 1000.
2. Validate NaN/Inf, energy residual, commutator, and paired row completeness.
3. Merge only the compact condition-seed summary first.
4. Run corrected postprocessor and select representative Stage 2 regions.
5. Commit compact summaries and final Stage 1 report; exclude raw logs.

## Do Not Assume

- Do not assume Stage 1 completed because it was launched.
- Do not use old central `W=1.028` as the denominator for the new grid.
- Do not call raw W output resource-attributable without subtracting the
  matched no-resource output.
- Do not call a fixed circuit adaptive or intelligent.

## Quarantined / Unverified Claims

See `.codex-hygiene/QUARANTINE.md`.
