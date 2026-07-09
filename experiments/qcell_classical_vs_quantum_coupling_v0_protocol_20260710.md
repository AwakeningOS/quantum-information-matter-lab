# Q-cell classical vs quantum coupling v0 protocol

Date: 2026-07-10 JST

Status: executed.

## Purpose

Compare the current Q-cell fixed region under matched resource/output settings:

```text
quantum direct links
no internal links
fully dephased quantum links
classical probability transport
central upper quantum comparison
```

This is a comparison of modeled linkage types. It is not a quantum-advantage
test.

## Run shape

```text
grid = QFCBM_0988
resource = R3_pure_1
noise = N4_dephase_plus_amplitude_damping, p = 0.06
seeds = 60
cycles = 200
GPU power limit = 250 W
```

## Required readouts

```text
W_resource
W_no_resource
resource_attributable_W
mean_link_negativity
mean_link_MI
mean_l1_coherence
energy_balance_residual
```

## Committed artifacts

```text
scripts/quantum_observation/qcell_classical_vs_quantum_coupling_v0_gpu.py
data/quantum_observation/qcell_classical_vs_quantum_coupling_v0_arm_summary.csv
data/quantum_observation/qcell_classical_vs_quantum_coupling_v0_manifest.json
results/qcell_classical_vs_quantum_coupling_v0_report_2026-07-10.md
```

Full seed summary and checkpoint trace remain local:

```text
/home/youthk/work/qcell_experiment_outputs/qcell_classical_vs_quantum_coupling_v0_outputs/
```

## Claim ceiling

Allowed:

```text
The modeled linkage types behave differently. Quantum direct links preserve
nonzero link negativity and coherence; classical probability transport can
produce larger W in this setting without quantum-link signatures.
```

Not allowed:

```text
quantum advantage
QPU result
physical energy generation
life/metabolism/homeostasis/agency
```
