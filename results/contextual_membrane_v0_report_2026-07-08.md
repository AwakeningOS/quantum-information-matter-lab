# Result: contextual_membrane_v0

Status: RAW_LOG_BACKED  
Generator script: `scripts/contextual/contextual_membrane_v0.py`  
Raw log: `data/contextual/contextual_membrane_v0_seed20260708.json`  
Generated event rows: `data/contextual/contextual_membrane_v0_seed20260708_rows.csv`  
Run command: `python scripts/contextual/contextual_membrane_v0.py --seed 20260708 --steps 64 --out data/contextual/contextual_membrane_v0_seed20260708.json --csv data/contextual/contextual_membrane_v0_seed20260708_rows.csv`  
Layer: CONTEXTUAL_COMPONENT  
Verdict: PASS_COMPONENT_BEHAVIOR  
Claim boundary: designed contextual-component behavior only; no quantum-specific promotion.

## Summary

`contextual_membrane_v0` implements a first contextual membrane whose passage score depends on object identity, readout/question context, context compatibility, and retained observed/unobserved alternatives.

The component passed the pre-registered component-level criteria.

## Main metrics

| Variant | Pass rate | Object-conditioned context range | Compatibility score gap | Event match to full | Score MAE to full |
|---|---:|---:|---:|---:|---:|
| full_contextual | 0.312500000 | 0.333906636 | 0.285508247 | n/a | n/a |
| context_no_memory | 0.296875000 | 0.318416667 | 0.280019550 | 0.984375000 | 0.008596154 |
| object_only | 0.406250000 | 0.000000000 | 0.046764418 | 0.781250000 | 0.135082084 |
| object_marginal_replay | 0.328125000 | 0.000000000 | 0.055738863 | 0.828125000 | 0.127557338 |
| shuffled_context_full | 0.312500000 | 0.213327805 | 0.221874876 | 0.750000000 | 0.155649413 |

## Criteria

| Criterion | Result |
|---|---|
| full_object_conditioned_context_range_ge_0_15 | True |
| full_compatibility_gap_ge_0_10 | True |
| object_only_context_range_le_0_05 | True |
| object_replay_event_match_below_0_90 | True |

## Interpretation

The full contextual membrane shows a strong object-conditioned context score range and a compatibility score gap. The object-only and object-marginal replay controls remove the context-conditioned structure by construction and do not reproduce the full event sequence.

The context-no-memory variant remains close to the full model. This means the first v0 effect is driven mainly by context compatibility and context-object bias, while retained observed/unobserved memory is present but not yet the dominant causal factor.

The shuffled-context full variant still shows contextual behavior but has a lower event match to the original full run. This indicates that context order and compatibility history contribute to the component trajectory.

## Limitations

```text
1. This is a designed component, not a natural discovery.
2. The strongest v0 signal comes from context compatibility and context-object bias.
3. Memory exists in the mechanism, but v0 does not yet prove that memory is necessary.
4. n=64 is a bootstrap run, not a large stability sweep.
5. No quantum-specific claim is made.
6. No physical matter, life, cell, metabolism, self-repair, or consciousness claim is made.
```

## Next local lesson

The next version should make memory necessity sharper. A good v1 target is:

```text
contextual_membrane_v1_memory_ablation:
  keep context compatibility fixed
  vary memory_decay / memory_gain
  add same-context replay control
  require memory ablation to reduce event-level fit or delayed context effects
```
