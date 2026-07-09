# Qセル・局所連動型エネルギー機械 full 2^7 最終盤 v0 protocol

Status: OBSERVATION_LOG

## Purpose

中央制御や全体測定を使わず、局所励起交換だけで資源受入、内部輸送、一時貯蔵、出力動作、使用済み資源の排出が全体として成立するか観察する。

## Hilbert space

```text
R,E,A,B,C,D,W = 7 qubits
full cycle density matrix dimension = 128
```

Q-cell body:

```text
E,A,B,C,D
```

Q-cell body is not reset mid-run.

## Main battery condition

```text
R3 = |1>
energy yes
coherence no
```

`R4 = |+>` is a coherence-injecting comparison, not the main battery-energy condition.

## Fixed operations

No global state is used to choose operations. The global target is used only after the run for evaluation.

Cycle:

```text
1. prepare R according to fixed schedule
2. locally couple R-E
3. fixed local internal links among E,A,B,C,D
4. locally couple D-W
5. record R/W ledger
6. trace R/W and continue Q-cell body
7. apply noise on Q-cell body
8. save metrics and ledger
```

## Main grid

```text
initial states: 100
cycles: 200
g: 0.10 main, plus 0.05/0.20 sweep
theta: 0.20
noise: N4 dephase + amplitude damping
p: 0.06 main, plus p sweep
```

## Comparisons

```text
ring + R3 |1>
chain + R3 |1>
middle_cut + R3 |1>
shuffled + R3 |1>
coupling_off + R3 |1>
converter_off + R3 |1>
output_off + R3 |1>
strong_dephase + R3 |1>
classical_probability_transport + R3 |1>
central_control upper bound + R3 |1>
ring + max mixed
ring + Gibbs beta 0.5,1,2
ring + |+> coherence resource
```

## Fault response

At cycle 100, apply one fixed perturbation, then continue with the same local rules.

```text
remove_A_excitation
overexcite_C
cut_BC
weaken_AB
close_DW
empty_E
```

## Energy ledger

```text
E_R_in + W_external = Delta_E_Qcell + E_R_out + E_W_out + Q_noise
```

Conditions with residual above numerical tolerance are not physically interpreted.

## Storage

All cycles:

```text
state scalar metrics
energy ledger
linkwise flow
population
purity
entropy
l1 coherence
pair ZZ
pair mutual information
pair negativity
```

Checkpoints:

```text
complete density matrix
```

Checkpoint cycles:

```text
0,1,2,5,10,20,49,50,75,99,100,124,125,149,150,174,175,199,200
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
