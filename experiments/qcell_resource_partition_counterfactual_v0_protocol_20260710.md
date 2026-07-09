# Q-cell resource partition counterfactual v0 protocol

Date: 2026-07-10 JST

Status: executed.

## Purpose

Test the hypothesis:

```text
quantum links retain internal quantum structure, so less resource reaches W;
classical transport discards that structure, so more resource reaches W.
```

This is not a repair, store, thermodynamics, or quantum-advantage experiment.

## Run shape

```text
grid = QFCBM_0988
seeds = 60
cycles = 200
resource = R3_pure_1
noise = N4_dephase_plus_amplitude_damping, p = 0.06
```

## Arms

```text
quantum_keep_structure
dephase_after_internal_25
dephase_after_internal_50
dephase_after_internal_75
full_dephase_after_internal
classical_same_graph_transport
no_internal_links
```

## Counterfactual shadow

At every cycle, after internal coupling and before W output:

```text
rho_quantum = actual state
rho_diag = same diagonal population, all off-diagonal structure removed
```

Both are passed through the same W output bottleneck, and:

```text
W_loss_to_structure = W_diag_same_population - W_quantum_actual
```

## Result

The core same-population shadow did not support the hypothesis:

```text
W_loss_to_structure = 0 for all arms
```

The dephase ladder also did not support "less structure gives more W":

```text
quantum_keep_structure W_attr = 15.857558
dephase_25 W_attr = 12.383500
dephase_50 W_attr = 9.765229
dephase_75 W_attr = 8.282828
full_dephase W_attr = 7.810684
```

In this model/output readout, W at the bottleneck is determined by the relevant
population available to the output port, not directly by off-diagonal structure
at fixed population.

The earlier high W of `classical_probability_transport` is therefore not
explained by "discarding quantum structure at the same population." It is more
likely due to the classical transport rule moving population more effectively
toward the output.

## Claim ceiling

Allowed:

```text
The resource-partition hypothesis was not supported by this counterfactual.
At fixed population, deleting quantum structure did not increase W.
```

Not allowed:

```text
quantum advantage
physical energy partition
stored-power claim
metabolism/homeostasis/life/agency
```
