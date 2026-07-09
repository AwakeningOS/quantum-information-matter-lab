# Q-cell fixed-circuit output bottleneck map v0 — Stage 2 confirmation

Date: 2026-07-09 / 2026-07-10 JST

## Scope

Stage 2 reran 28 representative grid points from the corrected Stage 1 fixed-circuit map with 100 initial states. The purpose is confirmation of representative regions, not full-grid ranking.

Primary metric: `resource_attributable_W = W(local_resource) - W(local_no_resource)`. Matched central controls were rerun for each grid with the same inlet, outlet, noise, schedule, and initial states.

Raw cyclewise/linkflow/ledger logs are intentionally not committed. Local raw storage: `/home/youthk/work/qcell_experiment_outputs/qcell_fixed_circuit_output_bottleneck_map_v0_stage2_outputs`.

## Run facts

- completed grids: 28/28
- variants per grid: 4
- seeds per grid: 100
- cycles: 200
- GPU: NVIDIA GeForce RTX 3090
- wall seconds after resume: 554.307
- max energy-balance residual: 1.394440e-13
- max `[U_DW, H_D+H_W]` norm: 0.000000e+00
- output switching cost: `not_modeled`

## Highest resource-attributable W

| grid_id | structure | g_internal | theta_in_RE | theta_out_DW | out_layers | resource_attributable_W_mean | central_resource_attributable_W_mean | fixed_to_matched_central_ratio_mean | efficiency_resource_to_W_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QFCBM_0488 | chain | 0.400000 | 0.800000 | 0.100000 | 8.000000 | 17.632414 | 38.374395 | 0.459473 | 0.521259 |
| QFCBM_0497 | chain | 0.400000 | 0.800000 | 0.800000 | 1.000000 | 17.632414 | 38.374395 | 0.459473 | 0.521259 |
| QFCBM_0988 | ring | 0.400000 | 0.800000 | 0.100000 | 8.000000 | 15.840497 | 38.404064 | 0.412461 | 0.484763 |
| QFCBM_0992 | ring | 0.400000 | 0.800000 | 0.200000 | 8.000000 | 14.861370 | 47.854960 | 0.310544 | 0.457972 |
| QFCBM_0492 | chain | 0.400000 | 0.800000 | 0.200000 | 8.000000 | 11.022786 | 47.333162 | 0.232870 | 0.359127 |
| QFCBM_0468 | chain | 0.400000 | 0.400000 | 0.100000 | 8.000000 | 9.935375 | 15.356931 | 0.646952 | 0.548954 |
| QFCBM_0975 | ring | 0.400000 | 0.400000 | 0.400000 | 4.000000 | 7.724708 | 17.689657 | 0.436673 | 0.445252 |
| QFCBM_0470 | chain | 0.400000 | 0.400000 | 0.200000 | 2.000000 | 5.734886 | 7.216036 | 0.794733 | 0.332428 |

## Highest resource-to-W efficiency

| grid_id | structure | g_internal | theta_in_RE | theta_out_DW | out_layers | resource_attributable_W_mean | efficiency_resource_to_W_mean | net_resource_transfer_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QFCBM_0408 | chain | 0.400000 | 0.050000 | 0.100000 | 8.000000 | 0.234025 | 0.560834 | 0.417279 |
| QFCBM_0428 | chain | 0.400000 | 0.100000 | 0.100000 | 8.000000 | 0.914825 | 0.560203 | 1.633023 |
| QFCBM_0448 | chain | 0.400000 | 0.200000 | 0.100000 | 8.000000 | 3.352016 | 0.557757 | 6.009803 |
| QFCBM_0468 | chain | 0.400000 | 0.400000 | 0.100000 | 8.000000 | 9.935375 | 0.548954 | 18.098716 |
| QFCBM_0488 | chain | 0.400000 | 0.800000 | 0.100000 | 8.000000 | 17.632414 | 0.521259 | 33.826429 |
| QFCBM_0497 | chain | 0.400000 | 0.800000 | 0.800000 | 1.000000 | 17.632414 | 0.521259 | 33.826429 |
| QFCBM_0988 | ring | 0.400000 | 0.800000 | 0.100000 | 8.000000 | 15.840497 | 0.484763 | 32.676456 |
| QFCBM_0992 | ring | 0.400000 | 0.800000 | 0.200000 | 8.000000 | 14.861370 | 0.457972 | 32.450220 |

## Highest fixed/matched-central ratio

| grid_id | structure | g_internal | theta_in_RE | theta_out_DW | out_layers | resource_attributable_W_mean | central_resource_attributable_W_mean | fixed_to_matched_central_ratio_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QFCBM_0441 | chain | 0.400000 | 0.200000 | 0.050000 | 1.000000 | 0.049151 | 0.055669 | 0.882920 |
| QFCBM_0449 | chain | 0.400000 | 0.200000 | 0.200000 | 1.000000 | 0.695668 | 0.796167 | 0.873777 |
| QFCBM_0469 | chain | 0.400000 | 0.400000 | 0.200000 | 1.000000 | 1.931651 | 2.277121 | 0.848286 |
| QFCBM_0470 | chain | 0.400000 | 0.400000 | 0.200000 | 2.000000 | 5.734886 | 7.216036 | 0.794733 |
| QFCBM_0408 | chain | 0.400000 | 0.050000 | 0.100000 | 8.000000 | 0.234025 | 0.302410 | 0.773854 |
| QFCBM_0428 | chain | 0.400000 | 0.100000 | 0.100000 | 8.000000 | 0.914825 | 1.193729 | 0.766349 |
| QFCBM_0500 | chain | 0.400000 | 0.800000 | 0.800000 | 8.000000 | 1.175128 | 1.557686 | 0.754404 |
| QFCBM_0448 | chain | 0.400000 | 0.200000 | 0.100000 | 8.000000 | 3.352016 | 4.542087 | 0.737980 |

## Strong-output overswap / suppression representatives

| grid_id | structure | theta_out_DW | out_layers | resource_attributable_W_mean | D_to_W_flow_cum_mean | D_population_mean |
| --- | --- | --- | --- | --- | --- | --- |
| QFCBM_0488 | chain | 0.100000 | 8.000000 | 17.632414 | 19.012182 | 0.084287 |
| QFCBM_0492 | chain | 0.200000 | 8.000000 | 11.022786 | 12.217594 | 4.900e-05 |
| QFCBM_0496 | chain | 0.400000 | 8.000000 | 0.055903 | 0.083366 | 0.114594 |
| QFCBM_0500 | chain | 0.800000 | 8.000000 | 1.175128 | 1.281969 | 0.437539 |
| QFCBM_0988 | ring | 0.100000 | 8.000000 | 15.840497 | 17.301129 | 0.076701 |
| QFCBM_0992 | ring | 0.200000 | 8.000000 | 14.861370 | 16.337668 | 6.553e-05 |
| QFCBM_0996 | ring | 0.400000 | 8.000000 | 0.098270 | 0.125805 | 0.172931 |
| QFCBM_1000 | ring | 0.800000 | 8.000000 | 1.012308 | 1.119551 | 0.382105 |

## Interpretation guardrails

- This confirms fixed-circuit envelope regions only.
- It does not show local adaptive optimization, purpose, life, metabolism, homeostasis, or quantum advantage.
- `fixed_to_matched_central_ratio` alone is misleading when central output is tiny; `QFCBM_0441` remains the explicit bad-ratio example.
- Output switching cost remains not modeled.

## Compact committed artifacts

- `data/quantum_observation/qcell_fixed_circuit_output_bottleneck_map_stage2_grid_summary_corrected.csv`
- `data/quantum_observation/qcell_fixed_circuit_output_bottleneck_map_stage2_promising_regions_corrected.csv`
- `data/quantum_observation/qcell_fixed_circuit_output_bottleneck_map_v0_stage2_manifest.json`
- `data/quantum_observation/qcell_fixed_circuit_output_bottleneck_map_stage2_selected_grid_ids.txt`
