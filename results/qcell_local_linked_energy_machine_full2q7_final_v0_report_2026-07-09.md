# Observation: Q-cell local linked energy machine full 2^7 final v0

Status: `OBSERVATION_LOG`

## Purpose

This run checks whether the qualitative transport behavior previously seen in
the single-excitation hard-core model survives in the full seven-qubit cycle
space:

```text
R, E, A, B, C, D, W
```

The continuing Q-cell body is `E,A,B,C,D`. It is not reset between cycles.
`R3=|1>` is the main energy-bearing, coherence-free resource. `R4=|+>` remains
a separate coherence-injection comparison.

## Committed reproducibility artifacts

```text
scripts/quantum_observation/qcell_local_linked_energy_machine_full2q7_final_v0.py
scripts/quantum_observation/qcell_local_linked_energy_machine_full2q7_final_v0_gpu.py
data/quantum_observation/qcell_local_linked_energy_machine_full2q7_final_v0_manifest.json
```

The multi-gigabyte cyclewise CSV and checkpoint arrays are intentionally not
committed. The manifest records the completed run shape.

## Executed run

```text
runner: batched CUDA
GPU: NVIDIA GeForce RTX 3090
power limit: 250 W
conditions: 37
initial states per condition: 100
cycles: 200
metric rows: 743,700
thermodynamic ledger rows: 740,000
link-flow rows: 740,000
checkpoint arrays: 456
wall time: 235.326 s
```

Validation:

```text
NaN/Inf rows: 0
complete condition markers: 37/37
maximum absolute energy-balance residual: 1.154632e-13
checkpoint trace range: 0.9999998212 .. 1.0000002384
invalid checkpoint arrays: 0
CPU/GPU smoke difference: order 1e-15
```

## Main R3 result

Main condition:

```text
structure: ring
resource: R3=|1>
noise: dephase + amplitude damping
p=0.06
g=0.10
theta=0.20
```

Mean per-seed cumulative ledger:

```text
gross resource input: 173.000000
net resource transfer: 4.866583
W output: 0.458287
W / gross input: 0.002649
W / net resource transfer: 0.094170
noise loss: 6.681873
final internal energy: 0.209122
final l1 coherence: 0.187390
final purity: 0.655047
```

The net-transfer ratio is not a standalone thermodynamic efficiency because
initial internal-energy change and unmodeled switching costs must remain in
the ledger interpretation.

## Supply-stop-restart checkpoints

Mean trajectories for the main ring condition:

| Cycle | Internal energy | Purity | l1 coherence |
|---:|---:|---:|---:|
| 0 | 2.482699 | 1.000000 | 10.636653 |
| 50 | 0.491292 | 0.384781 | 0.393993 |
| 75 | 0.092301 | 0.829312 | 0.023310 |
| 125 | 0.438663 | 0.424848 | 0.397242 |
| 150 | 0.671267 | 0.310406 | 0.618947 |
| 175 | 0.332837 | 0.512079 | 0.231102 |
| 200 | 0.209122 | 0.655047 | 0.187390 |

The staged schedule produces a resource-dependent trajectory: values fall
during supply interruption and rise after supply resumes. This does not show
autonomous resource selection or metabolism.

## Structure and control comparison

Mean per-seed cumulative W output:

| Condition | W output |
|---|---:|
| central-control upper comparison | 1.027726 |
| ring, `g=0.20` | 0.637069 |
| weak-AB fixed circuit | 0.531464 |
| ring baseline | 0.458287 |
| strong-AB fixed circuit | 0.416212 |
| shuffled fixed circuit | 0.406615 |
| classical probability transport | 0.388945 |
| chain baseline | 0.361389 |
| ring, `g=0.05` | 0.298382 |
| middle cut | 0.244341 |
| coupling off | 0.207107 |

The ring baseline exceeds the matched chain baseline by about 27%, but it
remains below the central-control comparison. The classical comparison is
close enough that these data do not establish quantum advantage.

## Noise sweep

Ring `R3` cumulative W output:

| Noise strength | W output |
|---:|---:|
| `p=0.01` | 1.919861 |
| `p=0.03` | 0.937119 |
| `p=0.06` | 0.458287 |
| `p=0.10` | 0.240769 |
| `p=0.18` | 0.112869 |

Output declines strongly with the modeled noise strength.

## Observation

The full model reproduces the qualitative single-excitation result:
coherence-free excitation resource can enter the coupled body and some energy
reaches `W`; ring/chain, link strength, cuts, and noise alter the transport.
The full model additionally makes the low output fraction and large modeled
noise loss explicit.

## Non-claims

```text
No energy generation.
No autonomous optimization.
No local decision-making.
No life, metabolism, repair, or homeostasis.
No quantum advantage.
No QPU result.
No PASS/FAIL promotion.
```
