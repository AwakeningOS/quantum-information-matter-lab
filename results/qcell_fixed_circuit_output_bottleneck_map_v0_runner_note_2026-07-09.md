# Q-cell fixed-circuit output bottleneck map v0 runner note

Status: `OBSERVATION_LOG / STAGE1_COMPLETED`

## Purpose

Map the fixed-circuit output envelope before introducing local adaptive
control. The map separates inlet, internal transport, outlet, coherent
overswap, chain/ring, and matched central-control effects.

## Corrected paired design

Every grid point runs the same initial states under:

```text
local_resource
local_no_resource
central_resource
central_no_resource
```

The primary attributed output is:

```text
resource_attributable_W
= W(local_resource) - W(local_no_resource)
```

The old central-control value is not reused as the denominator. Central
control is rerun at every matched grid point.

## Grid

```text
5 internal couplings
5 R-E inlet angles
5 D-W outlet angles
4 outlet-layer counts
2 structures
= 1,000 grid points
```

Stage 1 uses 10 initial states and 200 cycles for four paired variants. The
CUDA runner saves each completed grid atomically and supports `--resume`.

## Committed artifacts

```text
experiments/qcell_fixed_circuit_output_bottleneck_map_v0_corrected_protocol_20260709.md
scripts/quantum_observation/qcell_fixed_circuit_output_bottleneck_map_v0_gpu.py
scripts/quantum_observation/qcell_fixed_circuit_output_bottleneck_map_v0_postprocess.py
```

Raw cyclewise files are intentionally excluded from Git because Stage 1
produces multi-gigabyte logs. Compact corrected summaries and the final report
must be committed only after the run and validation complete.

Local execution:

```bash
python scripts/quantum_observation/qcell_fixed_circuit_output_bottleneck_map_v0_gpu.py \
  --stage stage1 \
  --n-seeds 10 \
  --resume \
  --no-merge \
  --outdir qcell_fixed_circuit_output_bottleneck_map_v0_stage1_outputs \
  --device cuda
```

## Execution state

Stage 1 completed locally:

```text
1,000/1,000 grid points
10 initial states
4 paired variants
200 cycles
wall time: 3,794.05 s
maximum absolute energy-balance residual: 1.381117e-13
```

See `results/qcell_fixed_circuit_output_bottleneck_map_v0_stage1_report_2026-07-09.md`.

## Non-claims

```text
No adaptive-optimization result.
No adaptive-control result.
No decision-making or purpose.
No life, metabolism, repair, or homeostasis.
No quantum advantage.
```
