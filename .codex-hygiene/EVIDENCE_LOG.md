# Evidence Log

## Full 2^7 execution

- Time: 2026-07-09 JST
- Action: Ran batched CUDA full model on RTX 3090 at 250 W.
- Evidence: 37/37 conditions; 743,700 metric rows; 740,000 ledger rows;
  740,000 flow rows; 456 checkpoint arrays.
- Files: local `qcell_local_linked_energy_machine_full2q7_final_v0_outputs_gpu_v2`
- Result: maximum absolute ledger residual `1.1546319456101628e-13`;
  zero NaN/Inf rows; zero invalid checkpoint arrays.

## CPU/GPU comparison

- Time: 2026-07-09 JST
- Action: Compared CPU and GPU smoke rows after sorting by seed and cycle.
- Evidence: selected metric and ledger differences were order `1e-15`.
- Files: full 2^7 CPU and GPU runners.
- Result: GPU batch implementation numerically matched CPU smoke.

## Bottleneck runner smoke

- Time: 2026-07-09 JST
- Action: Ran one grid, two seeds, four paired variants, 200 cycles.
- Evidence: 1,600 rows each for cyclewise, ledger, and linkflow;
  postprocessor produced 2 paired-seed rows and one grid summary.
- Files: corrected bottleneck runner and postprocessor.
- Result: zero NaN/Inf; maximum absolute residual `3.4638958368304884e-14`.

## Active Stage 1

- Time: latest refresh 2026-07-09 JST
- Action: Counted atomic completion markers.
- Evidence: `443`
- Files: local Stage 1 output `parts/*_complete.json`
- Result: Stage 1 in progress; not a completed result.

## GitHub publication

- Time: 2026-07-09 JST
- Action: Pushed the evidence-record branch and opened a draft stacked PR.
- Evidence: commit `8bd4ba6`; PR 29.
- Files: 16 changed files; no multi-gigabyte raw outputs.
- Result: `https://github.com/AwakeningOS/quantum-information-matter-lab/pull/29`

## Bottleneck Stage 1 completion

- Time: 2026-07-09 JST
- Action: Completed 1,000-grid corrected fixed-circuit map and postprocessed
  compact paired summaries.
- Evidence: 1,000/1,000 markers; 40,000 raw condition-seed summary rows;
  10,000 paired rows; all four variants in every pair; no non-finite compact
  values; maximum residual `1.381117442633695e-13`; commutator maximum `0`.
- Files: local Stage 1 outputs; compact grid and promising-region CSV files.
- Result: maximum attributed fixed output `17.6555578850702`; matched central
  `38.380658814001`; fixed/central `0.4600009968262461`.

## User requirements

- Time: 2026-07-09 JST
- Action: User requested code, experiment descriptions, findings, and future
  experiment order be stored in GitHub for paper writing and agent handoff.
- Evidence: explicit user instruction.
- Result: raw multi-gigabyte logs excluded by user request.
