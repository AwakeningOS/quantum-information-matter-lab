# Q-cell internal information map v0

Date: 2026-07-10 JST

## Arm Readout

- quantum_keep_structure: W_attr `15.857558`, R_out `140.288759`, Q_noise `17.070650`, coherence `1.669012`, entropy `3.043298`, MI `0.064643`.
- full_dephase_after_internal: W_attr `7.810684`, R_out `150.098734`, Q_noise `15.462675`, coherence `0.000000`, entropy `2.884571`, MI `0.007819`.
- classical_same_graph_transport: W_attr `25.919585`, R_out `131.759059`, Q_noise `15.638960`, coherence `0.000000`, entropy `3.550616`, MI `0.003213`.
- no_internal_links: W_attr `-0.000000`, R_out `162.423649`, Q_noise `11.811605`, coherence `0.172972`, entropy `0.919527`, MI `0.000000`.

## Quantum-Referenced Differences

- classical_same_graph_transport_minus_quantum_keep_structure: W `10.062027`, R_out `-8.529701`, Q_noise `-1.431690`, final TV `0.239383`, coherence `-1.669012`, MI `-0.061430`.
- full_dephase_after_internal_minus_quantum_keep_structure: W `-8.046874`, R_out `9.809975`, Q_noise `-1.607975`, final TV `0.258750`, coherence `-1.669012`, MI `-0.056824`.
- no_internal_links_minus_quantum_keep_structure: W `-15.857558`, R_out `22.134889`, Q_noise `-5.259045`, final TV `0.593180`, coherence `-1.496040`, MI `-0.064643`.

## Interpretation

The classical same-graph transport arm is strongest on W because it routes less
resource back through R and loses less to modeled noise than the quantum arm.

The quantum arm is not W-optimal, but it retains the internal features that the
classical arm drops: nonzero coherence, nonzero negativity, and much larger
mean pair mutual information. In this model, the clean reading is:

```text
classical transport = coarse W-output-biased transport
quantum transport = lower W, richer internal dynamics
```

This does not prove quantum advantage. It only shows that W alone is an
incomplete readout of the modeled Q-cell dynamics.

## Claim Ceiling

model-level internal information map; no quantum advantage or physical energy claim
