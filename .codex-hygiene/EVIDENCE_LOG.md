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

## Bottleneck Stage 2 completion

- Time: 2026-07-10 JST
- Action: Ran corrected fixed-circuit Stage 2 selected-grid confirmation on
  RTX 3090 using 28 representative grid IDs, 100 seeds, four matched variants,
  and 200 cycles.
- Evidence: runner manifest reports 28/28 completed grids, 2,800 paired
  postprocessed rows, maximum absolute energy-balance residual
  `1.3944401189291966e-13`, and commutator maximum `0`.
- Files: raw local output at
  `/home/youthk/work/qcell_experiment_outputs/qcell_fixed_circuit_output_bottleneck_map_v0_stage2_outputs`;
  compact CSV/report copied into `data/quantum_observation/` and `results/`.
- Result: highest attributed fixed output `17.632413845010216` for
  `QFCBM_0488`/`QFCBM_0497`; matched central `38.37439457135488`; highest
  efficiency `0.5608344141133803` for `QFCBM_0408`.

## Raw-output storage correction

- Time: 2026-07-10 JST
- Action: User instructed not to put experiment raw data directly under
  Downloads and to use an appropriate storage location.
- Evidence: explicit user instruction during Stage 2 run.
- Result: interrupted the run after 7 completed grids, moved partial outputs to
  `/home/youthk/work/qcell_experiment_outputs/`, and resumed successfully from
  completion markers.

## Local-controller causal test v0

- Time: 2026-07-10 JST
- Action: Ran local-controller v0 pilot and 100-seed confirmation on RTX 3090.
- Evidence: pilot completed 6 grids x 20 seeds x 16 variants; confirmation
  completed 3 grids x 100 seeds x 10 variants; maximum residual in summaries
  `7.327471962526033e-14`.
- Files: raw local outputs under
  `/home/youthk/work/qcell_experiment_outputs/qcell_local_controller_causal_test_v0_pilot_outputs`
  and
  `/home/youthk/work/qcell_experiment_outputs/qcell_local_controller_causal_test_v0_confirm_outputs`;
  compact CSV/report copied to `data/quantum_observation/` and `results/`.
- Result: `QFCBM_0988` internal controller attributed W `26.024037` vs fixed
  `15.840497`, beating shuffled-signal/time-shift controls in 100/100 seeds.
  `QFCBM_0496` internal controller attributed W `0.258512` vs fixed
  `0.055903`, also beating both controls in 100/100 seeds. `QFCBM_0399` is
  marginal against time-shift action: 64/100 positive.

## Controller evolution v0

- Time: 2026-07-10 JST
- Action: Ran small evolutionary/random search over interpretable local
  internal-controller parameters on RTX 3090.
- Evidence: population 12, generations 4, train seeds 20, validation seeds 20,
  holdout seeds 60, grids `QFCBM_0988`, `QFCBM_0496`, `QFCBM_0399`; manifest
  wall seconds `255.96470093727112`; max holdout residual `8.504e-14`.
- Files: raw local output at
  `/home/youthk/work/qcell_experiment_outputs/qcell_controller_evolution_v0_outputs`;
  compact CSV/report copied to `data/quantum_observation/` and `results/`.
- Result: best evolved controller holdout mean gain `4.553862` versus
  hand-coded `3.324505`. Evolved controller improved `QFCBM_0988` and
  `QFCBM_0496`; hand-coded remained slightly better on `QFCBM_0399`.

## Controller cost accounting v0

- Time: 2026-07-10 JST
- Action: Applied conservative gross per-angle cost sweep to controller
  evolution holdout detail rows.
- Evidence: de-duplicated 360 holdout rows; swept cost_per_angle values from
  `0` through `0.1`; output summary and report generated.
- Files: local output at
  `/home/youthk/work/qcell_experiment_outputs/qcell_controller_cost_accounting_v0_outputs`;
  compact CSV/report copied to `data/quantum_observation/` and `results/`.
- Result: evolved `QFCBM_0988` remained all-seed positive through swept
  cost_per_angle `0.03` with minimum break-even `0.042163`; `QFCBM_0496`
  through `0.0003`; `QFCBM_0399` only through `0.00003`.
