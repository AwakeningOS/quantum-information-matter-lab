# Task Ledger

| ID | Task | Status | Evidence | Notes |
|---|---|---|---|---|
| QEM-01 | Full 2^7 CPU/GPU runner | done_verified | CUDA run manifest; CPU/GPU smoke comparison | Raw logs remain local |
| QEM-02 | Full 2^7 result report | done_verified | `results/qcell_local_linked_energy_machine_full2q7_final_v0_report_2026-07-09.md` | Compact evidence only |
| QEM-03 | Corrected bottleneck protocol | done_verified | Existing protocol and postprocessor | Paired no-resource and matched central |
| QEM-04 | Bottleneck GPU runner | done_verified | Smoke: 1 grid, 2 seeds, 4 variants; max residual `3.46e-14` | Supports resume |
| QEM-05 | Stage 1 1000-grid run | in_progress | Local complete markers; 400/1000 at refresh | Do not claim result yet |
| QEM-06 | Stage 1 compact result commit | todo | Requires completed validation | Exclude raw logs |
| QEM-07 | Stage 2 100-seed confirmation | todo | Requires Stage 1 region selection | Representative regions |
| QEM-08 | Local coordination causal test | todo | Roadmap only | Fixed/shuffled/central/classical controls |
| QEM-09 | Battery-powered actuator | todo | Roadmap only | Account for action energy and switching work |
| QEM-10 | Fair quantum/classical efficiency comparison | todo | Roadmap only | No advantage claim before completion |
