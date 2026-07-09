# Handoff Prompt

## User Goal

Maintain a paper-ready, evidence-backed Q-cell research record in GitHub and
continue toward locally coordinated, resource-driven information machinery.

## Current Task

Freeze and execute representative `qcell_fixed_circuit_output_bottleneck_map_v0`
Stage 2 regions with 100 initial states.

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
- Stage 1 completed 1000/1000 grids with complete four-variant pairing.
- Stage 1 maximum residual: `1.381117e-13`.
- Maximum attributed W: `17.655558`; matched central: `38.380659`.
- Draft PR 29 records the completed full run and active-map handoff.

## Files Touched

- `scripts/quantum_observation/qcell_local_linked_energy_machine_full2q7_final_v0*.py`
- `scripts/quantum_observation/qcell_fixed_circuit_output_bottleneck_map_v0*.py`
- `results/qcell_local_linked_energy_machine_full2q7_final_v0_report_2026-07-09.md`
- `results/qcell_fixed_circuit_output_bottleneck_map_v0_runner_note_2026-07-09.md`
- `docs/qcell/Q_CELL_ENERGY_MACHINE_ROADMAP_20260709.md`
- `data/quantum_observation/qcell_local_linked_energy_machine_full2q7_final_v0_manifest.json`

## Current Status

Stage 1 is complete. Compact corrected summaries and a report are prepared;
multi-gigabyte raw files remain local.

Local output directory:

`/home/youthk/ダウンロード/qcell_fixed_circuit_output_bottleneck_map_v0_corrected_package/qcell_fixed_circuit_output_bottleneck_map_v0_stage1_outputs`

## Next Actions

1. Commit compact Stage 1 summary/regions/report; exclude raw logs.
2. Freeze representative Stage 2 grid IDs across the preregistered regions.
3. Run Stage 2 with 100 initial states and four matched variants.
4. Commit compact Stage 2 summary and final comparison report.

## Do Not Assume

- Do not use old central `W=1.028` as the denominator for the new grid.
- Do not call raw W output resource-attributable without subtracting the
  matched no-resource output.
- Do not call a fixed circuit adaptive or intelligent.

## Quarantined / Unverified Claims

See `.codex-hygiene/QUARANTINE.md`.
