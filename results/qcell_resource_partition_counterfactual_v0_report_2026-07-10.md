# Q-cell resource partition counterfactual v0

Date: 2026-07-10 JST

## Readout

- quantum_keep_structure: W_attr `15.857558`, diag W_attr `15.857558`, W_loss `0.000000`, coherence `2.465686`.
- dephase_after_internal_25: W_attr `12.383500`, diag W_attr `12.383500`, W_loss `0.000000`, coherence `0.898948`.
- dephase_after_internal_50: W_attr `9.765229`, diag W_attr `9.765229`, W_loss `0.000000`, coherence `0.325722`.
- dephase_after_internal_75: W_attr `8.282828`, diag W_attr `8.282828`, W_loss `0.000000`, coherence `0.075262`.
- full_dephase_after_internal: W_attr `7.810684`, diag W_attr `7.810684`, W_loss `0.000000`, coherence `0.000000`.
- classical_same_graph_transport: W_attr `25.919585`, diag W_attr `25.919585`, W_loss `0.000000`, coherence `0.000000`.
- no_internal_links: W_attr `-0.000000`, diag W_attr `-0.000000`, W_loss `0.000000`, coherence `0.212525`.

## Interpretation

This run does not support the hypothesis that quantum structure suppresses W at
fixed population. Deleting off-diagonal structure from the same population gave
`W_loss = 0`.

The dephase ladder also moved opposite the proposed pattern: less structure
gave lower W.

## Gap Accounting

`classical_same_graph_transport - quantum_keep_structure`:

```text
W_attr difference = +10.062027
R_out difference = -8.529701
Q_noise difference = -1.431690
final internal energy difference = -0.255438
final D population difference = +0.008533
```

The current best reading is that classical transport routes less resource back
through R and loses less to modeled noise, so more reaches W. The gap is not
explained by deleting quantum structure at fixed population.

## Claim Ceiling

model-level resource partition counterfactual; no quantum advantage or physical energy claim
