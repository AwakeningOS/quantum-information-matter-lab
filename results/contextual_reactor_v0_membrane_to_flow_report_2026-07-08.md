# Result: contextual_reactor_v0_membrane_to_flow

Status: RAW_LOG_BACKED  
Generator script: `scripts/contextual/contextual_reactor_v0_membrane_to_flow.py`  
Raw log: `data/contextual/contextual_reactor_v0_membrane_to_flow_seed20260708.json`  
Summary CSV: `data/contextual/contextual_reactor_v0_membrane_to_flow_seed20260708_summary.csv`  
Run command: `python scripts/contextual/contextual_reactor_v0_membrane_to_flow.py --seed 20260708 --steps 512 --out data/contextual/contextual_reactor_v0_membrane_to_flow_seed20260708.json --csv data/contextual/contextual_reactor_v0_membrane_to_flow_seed20260708_summary.csv`  
Layer: CLASSICAL_COMPONENT  
Verdict: PASS_MEMBRANE_TO_FLOW_PROPAGATION  
Claim boundary: component-level membrane-to-flow propagation only; no quantum-specific promotion.

## Summary

`contextual_reactor_v0_membrane_to_flow` tests whether contextual membrane PASS/BLOCK decisions propagate into a downstream reactor.

The result is:

```text
PASS_MEMBRANE_TO_FLOW_PROPAGATION
```

The key result is that removing memory, counterfactual residue, order structure, joint boundary structure, or membrane coupling changes downstream reactor release, quality, reservoir, and persistence.

## Main metrics

| Variant | Pass rate | Mean membrane signal | Mean release | Final reactor | Final quality | Final persistence | Final cumulative release | Event match to full | Release MAE | Final state distance |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| full_membrane_to_reactor | 0.575892857 | 0.358252384 | 0.076012142 | 3.635224935 | 0.872971146 | 5.769240129 | 38.849451729 | n/a | n/a | n/a |
| no_memory_membrane_to_reactor | 0.430803571 | 0.143927288 | 0.014909755 | 2.271417020 | 0.480087700 | 1.090516857 | 8.940490852 | 0.823660714 | 0.061174546 | 0.732881567 |
| no_counterfactual_membrane_to_reactor | 0.524553571 | 0.295143213 | 0.060539907 | 4.075688242 | 0.763749719 | 3.376836905 | 31.869441381 | 0.850446429 | 0.024497468 | 0.286002838 |
| order_scrambled_membrane_to_reactor | 0.593750000 | 0.352095400 | 0.064806876 | 2.164061360 | 0.676459236 | 2.944674958 | 30.472556495 | 0.504464286 | 0.054292158 | 0.460422353 |
| additive_boundary_membrane_to_reactor | 0.245535714 | -0.107925124 | 0.005073211 | 2.111065530 | 0.433170930 | 0.784523923 | 2.583046640 | 0.665178571 | 0.070938931 | 0.816300114 |
| reactor_without_membrane | 0.441964286 | 0.176339286 | 0.020368390 | 1.886229561 | 0.330734173 | 0.894988371 | 10.431454452 | 0.745535714 | 0.059995399 | 0.857159196 |

## Criteria

| Criterion | Result |
|---|---|
| no_memory_release_mae_to_full_ge_0_05 | True |
| no_counterfactual_release_mae_to_full_ge_0_02 | True |
| order_scrambled_final_state_distance_ge_0_20 | True |
| additive_boundary_event_match_to_full_le_0_90 | True |
| reactor_without_membrane_cumulative_release_delta_abs_ge_25 | True |
| full_final_persistence_ge_5 | True |

## Key result

The full membrane produces much stronger downstream persistence and release than the ablations.

```text
full_membrane_to_reactor final_persistence = 5.769240129
no_memory_membrane_to_reactor final_persistence = 1.090516857
no_counterfactual_membrane_to_reactor final_persistence = 3.376836905
order_scrambled_membrane_to_reactor final_persistence = 2.944674958
additive_boundary_membrane_to_reactor final_persistence = 0.784523923
reactor_without_membrane final_persistence = 0.894988371
```

The cumulative release also separates:

```text
full_membrane_to_reactor final_cumulative_release = 38.849451729
no_memory_membrane_to_reactor final_cumulative_release = 8.940490852
no_counterfactual_membrane_to_reactor final_cumulative_release = 31.869441381
order_scrambled_membrane_to_reactor final_cumulative_release = 30.472556495
additive_boundary_membrane_to_reactor final_cumulative_release = 2.583046640
reactor_without_membrane final_cumulative_release = 10.431454452
```

## Interpretation

This result supports the component-level claim that the implemented membrane does not merely make local PASS/BLOCK decisions. Its structure propagates into downstream reactor flow.

The important distinction is:

```text
memory removal weakens downstream release
counterfactual-residue removal changes downstream release and persistence
order scrambling changes the final reactor state
additive boundary replacement strongly suppresses release
removing membrane coupling changes the reactor trajectory
```

This is the first bridge from contextual membrane behavior to a downstream flow component.

## Limitations

```text
1. This is a designed component, not a natural discovery.
2. This is classical component propagation, not quantum-specific behavior.
3. The reactor mechanism is explicit and engineered.
4. This does not establish formal measurement contextuality.
5. No biological, consciousness, metabolism, self-repair, or physical matter synthesis claim is made.
```

## Next local lesson

The next step can be one of two routes:

```text
contextual_reactor_v1_flow_controls:
  stress-test propagation with more controls, multiple seeds, and stronger reactor-without-membrane baselines

contextual_membrane_quantum_anchor_probe:
  begin a separate, cautious probe connecting membrane boundary structure to PM/KCBS-like contextuality witnesses
```

The quantum-anchor probe should remain separate from the component propagation claim.
