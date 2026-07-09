# Qセル資源駆動型・情報秩序維持実験 v0 protocol

Date: 2026-07-09
Layer: QUANTUM_OBSERVATION
Status: OBSERVATION_LOG
Experiment: `qcell_resource_driven_info_order_v0`

## Purpose

Observe whether continuous external resource input under noise can support a non-equilibrium Q-cell state, with thermodynamic bookkeeping.

No claim is made of energy generation, life, metabolism, self-repair, homeostasis, or quantum advantage.

## System

```text
Q-cell S: A,B,C,D four qubits
Resource R: one auxiliary qubit per cycle
Spent resource W: R after converter interaction, separated and recorded
Hamiltonian: H_i = |1><1|, omega = 1
H_S = H_A + H_B + H_C + H_D
H_R = |1><1|
```

## Converter

```text
U_converter(theta) = exp[-i theta(sigma+_C sigma-_R + sigma-_C sigma+_R)]
theta = 0.05, 0.10, 0.20, 0.40
```

Numerically record:

```text
[U_converter, H_C + H_R]
```

## Cycle

```text
1. internal excitation-preserving Q-cell coupling
2. noise on S
3. fresh or scheduled resource R
4. C-R converter
5. trace out R as spent W
6. record S and W ledger
```

Q-cell S is never reset mid-run. Only the incoming resource state is newly prepared.

## Resource schedule

```text
cycles 0-49: supply on
cycles 50-99: supply stop
cycles 100-149: supply restart
cycles 150-199: half-quality supply
```

Controls include noise-only, resource-only with converter off, max-mixed converter, spent-resource reuse, internal-coupling off, and single-C-only.

## Resource types in materialized compact grid

```text
R1 max mixed
R2 pure |0>
R3 pure |1>
R4 |+>
R5 Gibbs beta=1
```

The wider instruction listed Gibbs beta 0.2, 0.5, 1, 2, 5; this materialized v0 compact ledger grid includes beta=1 in the full p/theta sweep.

## Noise conditions

```text
N0 none
N1 dephase
N2 depolarizing
N3 amplitude damping
N4 dephase + amplitude damping
p = 0.01, 0.03, 0.06, 0.10, 0.18 for N1-N4
```

## Ledger

For each cycle:

```text
Delta E_S
Delta E_R
Q_noise
W_gate
energy_balance_residual = Delta E_S + Delta E_R - Q_noise - W_gate
Delta S_S
Delta S_R
resource_free_energy_consumed
resource_reset_min_work
```

The converter and internal coupling are energy-preserving in the implemented Hamiltonian, so W_gate should stay numerical-error small.

## Important storage note

Cyclewise scalar metrics and ledgers are saved for all included conditions and all cycles. Complete density matrices are saved at checkpoint cycles:

```text
0, 1, 2, 5, 10, 20, 50, 100, 150, 199, 200
```

This is due file-size constraints. Do not present the checkpoint NPZ as every-cycle density storage.
