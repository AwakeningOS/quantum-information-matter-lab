# Q-cell internal information map v0 protocol

Date: 2026-07-10 JST

## Question

After the resource-partition counterfactual showed that the classical W surplus
is not explained by deleting quantum structure at fixed population, ask a
different question:

```text
What internal information does the quantum-linked Q-cell retain that the
W-optimized classical transport drops?
```

## Scope

Grid:

```text
QFCBM_0988
```

Seeds and cycles:

```text
60 seeds
200 cycles
```

Arms:

```text
quantum_keep_structure
full_dephase_after_internal
classical_same_graph_transport
no_internal_links
```

## Measurements

For each arm, record:

```text
resource_attributable_W
R_out
Q_noise
Delta_E_internal
final E/A/B/C/D populations
l1 coherence
purity
entropy
diagonal entropy
pair mutual information
pair negativity
pair ZZ structure
final population distance from quantum_keep_structure
```

## Main Readout

```text
quantum_keep_structure:
  W_attr = 15.857558
  coherence = 1.669012
  mean pair MI = 0.064643
  mean negativity = 0.001741

classical_same_graph_transport:
  W_attr = 25.919585
  coherence = 0
  mean pair MI = 0.003213
  mean negativity = 0
```

Quantum-referenced difference:

```text
classical - quantum W_attr = +10.062027
classical - quantum R_out = -8.529701
classical - quantum Q_noise = -1.431690
classical - quantum final population TV = 0.239383
classical - quantum coherence = -1.669012
classical - quantum mean pair MI = -0.061430
```

## Interpretation

The classical arm behaves like a coarse W-output-biased transport rule. It sends
more resource to W, sends less back through R, and loses less to modeled noise.

The quantum arm is weaker on W but retains richer internal dynamics: coherence,
link negativity, and much larger pair mutual information.

Allowed claim:

```text
In this model, W alone is an incomplete readout. Classical same-graph transport
is W-output-biased, while quantum transport retains internal structure and
correlation that the classical arm drops.
```

Forbidden claims:

```text
quantum advantage
physical energy storage
thermodynamic proof
life
metabolism
homeostasis
agency
```
