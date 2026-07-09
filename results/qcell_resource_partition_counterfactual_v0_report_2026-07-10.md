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

This run does not support the resource-partition hypothesis.

The same-population shadow gave `W_loss = 0`: deleting off-diagonal structure
while keeping the same population did not increase W.

The dephase ladder also moved opposite to the proposed pattern: less structure
gave lower W, not higher W.

The higher W in `classical_same_graph_transport` is therefore not explained by
discarding quantum structure at fixed population. It is more likely explained by
the classical transport rule moving population toward the output more
effectively.

## Claim Ceiling

model-level resource partition counterfactual; no quantum advantage or physical energy claim
