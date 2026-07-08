# Paper A Design Lessons for the Next Lab

This document records the reusable design lesson from Paper A without importing the old paper's full result chain.

## Main lesson

```text
Quantum-looking downstream behavior is not enough.
The next lab must separate component construction from quantum/audit claims.
```

Paper A showed a useful split:

```text
CLASSICAL_EFFECTIVE_TRANSPORT:
  transport, membrane, reservoir, release, terrain behavior can be useful
  even when classical-effective.

CONSTRUCTED_BELL_FEEDBACK:
  if a Bell/CHSH witness is explicitly routed into a downstream variable,
  the downstream positive is constructed.

NEGATIVE_BY_OBSERVABLE_CLASS:
  a local one-body observable negative does not rule out all joint-observable
  structure.

MEASUREMENT_CONTEXTUALITY:
  non-routed contextual witnesses are the layer where nonclassical structure
  survived the audit.
```

## Next design principle

```text
Do not build the next system by merely adding more flow.
Build components whose interfaces depend on context/question structure.
```

## Component targets

### contextual membrane

A boundary whose passage rule depends on the question/context being asked.

### contextual converter

A converter whose A -> P/Q mapping changes with compatible/incompatible question pairs.

### contextual memory

A memory that stores observed outputs and unmeasured alternatives separately.

### contextual terrain

A terrain written by question history, not only reaction history.

### contextual self-register

An internal state that records which context the system uses to read itself.

## Promotion path

A component becomes a result through:

```text
protocol -> generator script -> raw log -> report -> STATUS.md -> reproducibility check
```

The research direction is constructive: build the parts, compose them, audit the claims, and keep what survives.
