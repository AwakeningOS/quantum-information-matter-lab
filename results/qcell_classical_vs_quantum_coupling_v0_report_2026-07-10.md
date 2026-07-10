# Q-cell classical vs quantum coupling v0

Date: 2026-07-10 JST

## Readout

- quantum_direct: W_attr `15.857558`, mean link negativity `0.001741`, mean coherence `1.669012`.
- quantum_no_internal_links: W_attr `-0.000000`, mean link negativity `0.000000`, mean coherence `0.172972`.
- quantum_post_internal_dephased: W_attr `7.810684`, mean link negativity `0.000000`, mean coherence `0.000000`.
- quantum_dephase_after_each_link: W_attr `8.309966`, mean link negativity `0.000000`, mean coherence `0.000000`.
- classical_probability_transport: W_attr `25.919585`, mean link negativity `0.000000`, mean coherence `-0.000000`.
- central_upper_quantum: W_attr `38.424002`, mean link negativity `0.000214`, mean coherence `1.058645`.

## Audit Notes

- `central_upper_quantum` is a positive-control / upper-bound arm, not a fair competitor.
- `quantum_post_internal_dephased` dephases after the internal update within each cycle.
- `quantum_dephase_after_each_link` dephases immediately after every internal link.
- W is not a quantum-signature metric here: classical probability transport has larger W with zero negativity/coherence.
- Arm summary includes seed-level spread, CI, resource/no-resource deltas for link metrics, and density-matrix health checks.

## Claim Ceiling

comparison of modeled quantum links, dephased links, no links, classical probability transport, and central upper bound; no quantum advantage claim
