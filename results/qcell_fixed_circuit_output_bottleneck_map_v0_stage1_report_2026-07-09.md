# Observation: Q-cell fixed-circuit output bottleneck map v0 Stage 1

Status: `OBSERVATION_LOG`

## Purpose

Establish the output and efficiency envelope of fixed local circuits before
adding local state-dependent control.

## Executed grid

```text
1,000 grid points
4 paired variants per grid
10 initial states
200 cycles
GPU: NVIDIA GeForce RTX 3090
wall time: 3,794.05 s
```

Paired variants:

```text
local_resource
local_no_resource
central_resource
central_no_resource
```

Primary attributed output:

```text
resource_attributable_W
= W(local_resource) - W(local_no_resource)
```

Validation:

```text
complete grid markers: 1,000/1,000
paired seed rows: 10,000
all four variants present: 10,000/10,000
non-finite compact-summary values: 0
maximum absolute energy-balance residual: 1.381117e-13
maximum [U_DW, H_D + H_W] norm: 0
output switching cost: not modeled
```

## Maximum attributed output

Four discrete outlet settings share the same effective coherent outlet angle:

```text
theta_out_DW * out_layers = 0.8
```

They produced the same maximum within numerical precision.

Representative grid:

```text
grid_id: QFCBM_0488
structure: chain
g_internal: 0.4
theta_in_RE: 0.8
theta_out_DW: 0.1
out_layers: 8
resource_attributable_W: 17.655558
matched central resource_attributable_W: 38.380659
fixed / matched central: 0.460001
efficiency_resource_to_W: 0.521196
net_resource_transfer: 33.875018
modeled Q_noise: 16.620085
```

Best ring grid under the same effective outlet angle:

```text
grid_id: QFCBM_0988
resource_attributable_W: 15.879790
matched central resource_attributable_W: 38.405943
fixed / matched central: 0.413459
efficiency_resource_to_W: 0.485147
```

The global maximum is therefore a chain condition, although ring conditions
exceed their matched chain conditions at many other grid points.

## Output/efficiency tradeoff

Highest mean resource-transfer efficiency region:

```text
grid_id: QFCBM_0408
structure: chain
g_internal: 0.4
theta_in_RE: 0.05
effective outlet angle: 0.8
resource_attributable_W: 0.234301
efficiency_resource_to_W: 0.560784
fixed / matched central: 0.774684
```

The highest efficiency does not coincide with the highest output. Stage 2
must preserve both regions rather than choosing one scalar winner.

## Fixed/central ratio caveat

The largest fixed-to-central ratio was:

```text
0.883564
```

but its attributed output was only:

```text
0.049198
```

The ratio alone favors low-output regimes and must not be treated as the main
performance score.

## Strong-output coherent overswap

For chain, `g=0.4`, `theta_in_RE=0.8`, changing the effective outlet angle
produced:

| Effective outlet angle | Attributed W |
|---:|---:|
| 0.05 | 0.221700 |
| 0.10 | 0.870047 |
| 0.20 | 3.231164 |
| 0.40 | 9.876997 |
| 0.80 | 17.655558 |
| 1.60 | 11.039254 |
| 3.20 | 0.055991 |
| 6.40 | 1.176372 |

Output rises to an intermediate coherent exchange angle and then collapses
under stronger repeated exchange. No measurement mechanism is present, so
this is recorded as coherent overswap/output suppression, not a Zeno effect.

## Stage 1 observation

The original low output was not a single unavoidable Q-cell limit. It was
strongly dependent on inlet strength, internal coupling, outlet exchange, and
outlet-layer count. A fixed chain circuit increased attributed output
substantially, but still reached only about 46% of its matched central-control
comparison at the highest-output grid.

This establishes a meaningful gap for the planned local-coordination causal
test. It does not show that components optimize a global objective.

## Committed compact data

```text
data/quantum_observation/qcell_fixed_circuit_output_bottleneck_map_stage1_grid_summary_corrected.csv
data/quantum_observation/qcell_fixed_circuit_output_bottleneck_map_stage1_promising_regions_corrected.csv
data/quantum_observation/qcell_fixed_circuit_output_bottleneck_map_v0_stage1_manifest.json
```

Multi-gigabyte cyclewise, link-flow, and ledger files remain local.

## Next action

Select representative Stage 2 regions and rerun with 100 initial states:

```text
maximum attributed output
maximum efficiency
central-nearest with nontrivial output
outlet narrow
internal transport slow
ring circulation
strong-output suppression
chain-best
ring-best
```

## Non-claims

```text
No adaptive control.
No autonomous optimization.
No purpose or decision-making.
No life, metabolism, repair, or homeostasis.
No quantum advantage.
No QPU result.
```
