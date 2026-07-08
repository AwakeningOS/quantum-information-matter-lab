# Contextual Component Lessons

## contextual_membrane_v0

Date: 2026-07-08  
Layer: CONTEXTUAL_COMPONENT  
Verdict: PASS_COMPONENT_BEHAVIOR

## Lesson 1: Context conditioning is easy to implement; memory necessity is harder

The v0 membrane passed the component-level criteria, but the strongest effect came from context-object bias and compatibility penalties.

The `context_no_memory` control stayed close to full_contextual:

```text
context_no_memory event_match_to_full = 0.984375000
context_no_memory score_mae_to_full = 0.015838863
```

This means future work should not merely include a memory variable. It should design a condition where memory is necessary.

## Lesson 2: Object-only controls are useful but insufficient

The object-only and object-marginal replay controls removed context-conditioned score range and did not perfectly reproduce the full event sequence:

```text
object_only event_match_to_full = 0.781250000
object_marginal_replay event_match_to_full = 0.828125000
```

These controls are good first checks, but future experiments need stronger replay controls.

## Lesson 3: Keep the claim layer strict

This is a designed contextual component result. It is not a quantum-specific result.

Future agents should keep the promotion path:

```text
component behavior -> replay controls -> audit witness -> quantum/contextuality claim
```
