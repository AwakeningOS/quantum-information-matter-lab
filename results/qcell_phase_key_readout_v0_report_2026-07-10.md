# Q-cell phase-key readout v0

Date: 2026-07-10 JST

## Summary

- quantum / no_key: W `0.435367`, diag W `0.435367`, coherence-attributable W `0.000000`, key gain `0.000000`, positive coherence seeds `0/60`, prep coherence `1.172859`, prep MI `0.023753`.
- quantum / correct_key: W `25.745433`, diag W `25.745120`, coherence-attributable W `0.000312`, key gain `25.310065`, positive coherence seeds `60/60`, prep coherence `1.172859`, prep MI `0.023753`.
- quantum / wrong_key: W `25.744808`, diag W `25.745120`, coherence-attributable W `-0.000312`, key gain `25.309441`, positive coherence seeds `0/60`, prep coherence `1.172859`, prep MI `0.023753`.
- quantum / phase_shuffled_correct_key: W `17.837375`, diag W `17.837455`, coherence-attributable W `-0.000080`, key gain `17.402008`, positive coherence seeds `25/60`, prep coherence `1.172859`, prep MI `0.023753`.
- classical / no_key: W `0.518922`, diag W `0.518922`, coherence-attributable W `0.000000`, key gain `0.000000`, positive coherence seeds `0/60`, prep coherence `0.000000`, prep MI `0.000663`.
- classical / correct_key: W `25.708586`, diag W `25.708586`, coherence-attributable W `0.000000`, key gain `25.189665`, positive coherence seeds `0/60`, prep coherence `0.000000`, prep MI `0.000663`.
- classical / wrong_key: W `25.708586`, diag W `25.708586`, coherence-attributable W `0.000000`, key gain `25.189665`, positive coherence seeds `0/60`, prep coherence `0.000000`, prep MI `0.000663`.
- classical / phase_shuffled_correct_key: W `17.857965`, diag W `17.857965`, coherence-attributable W `0.000000`, key gain `17.339044`, positive coherence seeds `0/60`, prep coherence `0.000000`, prep MI `0.000663`.
- full_dephase / no_key: W `0.258356`, diag W `0.258356`, coherence-attributable W `0.000000`, key gain `0.000000`, positive coherence seeds `0/60`, prep coherence `0.000000`, prep MI `0.004272`.
- full_dephase / correct_key: W `25.825558`, diag W `25.825558`, coherence-attributable W `0.000000`, key gain `25.567202`, positive coherence seeds `0/60`, prep coherence `0.000000`, prep MI `0.004272`.
- full_dephase / wrong_key: W `25.825558`, diag W `25.825558`, coherence-attributable W `0.000000`, key gain `25.567202`, positive coherence seeds `0/60`, prep coherence `0.000000`, prep MI `0.004272`.
- full_dephase / phase_shuffled_correct_key: W `17.791987`, diag W `17.791987`, coherence-attributable W `0.000000`, key gain `17.533632`, positive coherence seeds `0/60`, prep coherence `0.000000`, prep MI `0.004272`.
- no_internal_links / no_key: W `0.000300`, diag W `0.000300`, coherence-attributable W `0.000000`, key gain `0.000000`, positive coherence seeds `0/60`, prep coherence `0.000036`, prep MI `0.000000`.
- no_internal_links / correct_key: W `25.932481`, diag W `25.932481`, coherence-attributable W `-0.000000`, key gain `25.932181`, positive coherence seeds `30/60`, prep coherence `0.000036`, prep MI `0.000000`.
- no_internal_links / wrong_key: W `25.932481`, diag W `25.932481`, coherence-attributable W `-0.000000`, key gain `25.932181`, positive coherence seeds `29/60`, prep coherence `0.000036`, prep MI `0.000000`.
- no_internal_links / phase_shuffled_correct_key: W `17.731284`, diag W `17.731284`, coherence-attributable W `-0.000000`, key gain `17.730984`, positive coherence seeds `24/60`, prep coherence `0.000036`, prep MI `0.000000`.

## Interpretation

The raw key gain is not specific: all arms gain large W because the key also
routes D population to W.

After subtracting the same-population diagonal shadow, the only clean
key-directional signal is in the quantum arm:

```text
quantum correct_key coherence-attributable W = +0.000312, 60/60 seeds positive
quantum wrong_key coherence-attributable W = -0.000312, 0/60 seeds positive
quantum phase-shuffled correct_key = -0.000080, 25/60 seeds positive
classical/full_dephase correct_key = 0
```

This is a small phase-key readout candidate, not a strong result. The effect is
tiny compared with the population-routed W. It supports only the narrow claim
that quantum-retained off-diagonal structure can produce a detectable
key-directional W contribution after population-only routing is subtracted.

## Claim Ceiling

model-level delayed readout-key test; no quantum advantage or physical energy claim
