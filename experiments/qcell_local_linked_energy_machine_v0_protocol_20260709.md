# Qセル・局所連動型エネルギー機械 観察実験 v0 protocol

Date: 2026-07-09
Layer: QUANTUM_OBSERVATION
Status: OBSERVATION_LOG
Experiment: `qcell_local_linked_energy_machine_v0`

## Purpose

Observe whether local neighbor-only interactions can produce resource intake, internal transport, temporary storage, output action, and spent-resource discharge as a whole-system behavior.

Do not describe this as purpose, decision-making, life, optimization, metabolism, self-repair, or homeostasis.

## Most important constraint

The global target is used only after the run for evaluation. It is not supplied to local component rules.

No component reads the full global state to choose an operation.
No external program identifies a shortage and corrects it.
No direct reset to a target state.
No condition-specific retuning after seeing results.
No free energy injection gate.

## Materialized v0 limitation

This materialized v0 uses a single-excitation hard-core internal basis:

```text
[vac, E, A, B, C, D]
```

It is not a full 2^7 Hilbert-space run. It keeps 100 initial states and 200 cycles. Complete density matrices are saved at checkpoints in the truncated basis.

This limitation is intentional for this v0 run after the full 5-qubit density implementation was too slow in this environment.

## Components and local links

Internal components:

```text
E, A, B, C, D
```

Resource and output are ephemeral local ports:

```text
R -> E
D -> W
```

Local excitation exchange links:

```text
E-A
A-B
B-C
C-D
optional A-D ring link
```

Implemented local coupling:

```text
H_ij = g_ij(|i><j| + |j><i|)
```

Main parameters:

```text
g = 0.05, 0.10, 0.20
theta = 0.20 in the main grid
cycles = 200
initial states = 100
```

## Resource separation

The battery-like main condition is coherence-free excitation:

```text
R3 = |1>
```

`R4 = |+>` is recorded separately as a coherence-injecting resource, not as a pure battery-energy condition.

Resources included:

```text
R1 max mixed
R3 |1>
R4 |+>
R5 Gibbs beta = 0.5, 1, 2
```

## Schedule

```text
cycles 0-49: constant supply
cycles 50-74: supply stop
cycles 75-124: supply restart
cycles 125-149: double supply
cycles 150-174: half supply
cycles 175-199: burst supply
```

## Faults

At cycle 100, one fixed perturbation is applied, then the same local rules continue.

```text
remove_A_excitation
overexcite_C
cut_BC
weaken_AB
close_DW
empty_E
```

## Controls

```text
chain
ring
middle_cut
weak_AB
strong_AB
shuffled
coupling_off
converter_off
output_off
central_control upper-bound control
strong_dephase
```

Central control is an upper-bound comparison only and is not mixed into the main local-system claim.

## Saved outputs

```text
all_conditions.jsonl.gz
checkpoint_density_matrices.npz
cyclewise_state_metrics.csv
linkwise_energy_flow.csv
thermodynamic_ledger.csv
fault_response_trajectories.csv
chain_vs_ring_comparison.csv
quantum_vs_dephased_comparison.csv
manifest.json
observation report
regenerate_command.txt
```

## Energy ledger

For each cycle:

```text
E_R_in
E_R_out
Delta_E_Qcell
E_W_out
Q_noise
W_external
energy_balance_residual
resource_free_energy_consumed
entropy_exported_to_R
```

Balance convention:

```text
E_R_in + W_external = Delta_E_Qcell + E_R_out + E_W_out + Q_noise
```

## Non-claims

```text
No purpose.
No decision-making.
No life.
No metabolism.
No self-repair.
No homeostasis.
No optimization claim.
No quantum advantage claim.
No PASS/FAIL.
No ranking.
```
