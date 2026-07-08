# Agent Handoff

Updated: 2026-07-08

## Repository role

This repository is a clean lab for contextual information-matter components.

The operating rule remains:

```text
No code + no raw log = no result.
```

## Current experiment state

The first post-bootstrap experiment added by this agent is:

```text
contextual_membrane_v0
```

Files currently added on branch `agent/contextual-membrane-v0-20260708-final`:

```text
experiments/contextual_membrane_v0_protocol_2026-07-08.md
scripts/contextual/contextual_membrane_v0.py
data/contextual/contextual_membrane_v0_seed20260708.json
results/contextual_membrane_v0_report_2026-07-08.md
```

## Result

```text
Verdict: PASS_COMPONENT_BEHAVIOR
Layer: CONTEXTUAL_COMPONENT
```

Main observed metrics from the raw JSON:

```text
full_contextual pass_rate = 0.3125
full_contextual object_conditioned_context_score_range_mean = 0.333906636
full_contextual compatibility_score_gap = 0.285508247
object_only object_conditioned_context_score_range_mean = 0.0
object_marginal_replay event_match_to_full = 0.828125
shuffled_context_full event_match_to_full = 0.75
```

## Important interpretation

The v0 component expresses designed context-conditioned membrane behavior against object-only and object-marginal replay controls.

The strongest signal is not memory necessity yet. The context-no-memory variant remains very close to full:

```text
context_no_memory event_match_to_full = 0.984375
context_no_memory score_mae_to_full = 0.008596154
```

So v0 mainly demonstrates context bias and compatibility effects. Memory exists in the mechanism, but v0 does not yet prove memory is necessary.

## Recommended next experiment

```text
contextual_membrane_v1_memory_ablation
```

Core idea:

```text
keep context compatibility fixed
vary memory_decay and memory_gain
add same-context replay control
require memory ablation to reduce event-level fit or delayed context effects
```

## Claim boundary

The current result is a contextual component result only.

It does not establish quantum-specific behavior, measurement contextuality, life, metabolism, self-repair, consciousness, or physical matter synthesis.
