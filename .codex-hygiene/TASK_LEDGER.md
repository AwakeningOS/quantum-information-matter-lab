# Task Ledger

| ID | Task | Status | Evidence | Notes |
|---|---|---|---|---|
| QEM-01 | Full 2^7 CPU/GPU runner | done_verified | CUDA run manifest; CPU/GPU smoke comparison | Raw logs remain local |
| QEM-02 | Full 2^7 result report | done_verified | `results/qcell_local_linked_energy_machine_full2q7_final_v0_report_2026-07-09.md` | Compact evidence only |
| QEM-03 | Corrected bottleneck protocol | done_verified | Existing protocol and postprocessor | Paired no-resource and matched central |
| QEM-04 | Bottleneck GPU runner | done_verified | Smoke: 1 grid, 2 seeds, 4 variants; max residual `3.46e-14` | Supports resume |
| QEM-05 | Stage 1 1000-grid run | done_verified | 1000 markers; 10,000 complete pairs; max residual `1.381117e-13` | Raw logs local |
| QEM-06 | Stage 1 compact result commit | done_verified | Commit `492aca6`; compact grid/region CSV and report | Raw logs excluded |
| QEM-07 | Stage 2 100-seed confirmation | done_verified | 28/28 grids completed; 2,800 paired rows; max residual `1.394440e-13` | Raw logs local under `/home/youthk/work/qcell_experiment_outputs/` |
| QEM-08 | Local coordination causal test | done_verified | Pilot 6x20 and confirmation 3x100 completed; QFCBM_0988 and QFCBM_0496 beat fixed/shuffled/time-shift controls | Raw logs local; compact results prepared |
| QEM-11 | Controller evolution v0 | done_verified | Population 12, generations 4; holdout mean gain `4.553862` vs hand-coded `3.324505` | Trial-and-error parameter search only |
| QEM-09 | Battery-powered actuator | todo | Roadmap only | Account for action energy and switching work |
| QEM-10 | Fair quantum/classical efficiency comparison | todo | Roadmap only | No advantage claim before completion |
