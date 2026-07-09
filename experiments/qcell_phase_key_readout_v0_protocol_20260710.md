# Q-cell phase-key readout v0 protocol

Date: 2026-07-10 JST

## Question

Does the internal structure retained by the quantum-linked Q-cell become
readable later when a phase-sensitive key is applied before W readout?

## Design

Prep:

```text
120 cycles
resource on
no W readout during prep
```

Readout:

```text
80 cycles
resource off
branch from the same prepared state
```

Source arms:

```text
quantum
classical
full_dephase
no_internal_links
```

Keys:

```text
no_key
correct_key
wrong_key
phase_shuffled_correct_key
```

The key contains a C-D inverse exchange plus local C/D basis conversion before
D-W readout. A same-population diagonal shadow is run for every branch so that
plain population routing can be subtracted.

## Main Readout

The raw key gain is not specific: all arms gain large W after the key because
the key also routes D population to W.

The useful readout is:

```text
coherence_attributable_readout_W =
  readout_W(actual state) - readout_W(same-population diagonal shadow)
```

Results:

```text
quantum correct_key:
  coherence_attributable_W = +0.000312
  positive seeds = 60/60

quantum wrong_key:
  coherence_attributable_W = -0.000312
  positive seeds = 0/60

quantum phase_shuffled_correct_key:
  coherence_attributable_W = -0.000080
  positive seeds = 25/60

classical correct_key:
  coherence_attributable_W = 0
  positive seeds = 0/60

full_dephase correct_key:
  coherence_attributable_W = 0
  positive seeds = 0/60
```

## Interpretation

The broad W increase is just a population-routing effect and cannot support the
phase-key claim.

After subtracting the diagonal shadow, there is a small but clean
key-directional signal only in the quantum arm: the correct key is positive in
all seeds, the wrong key flips sign, and phase shuffling removes the effect.

Allowed claim:

```text
This is a small model-level phase-key readout candidate: quantum-retained
off-diagonal structure produced a tiny key-directional W contribution after
population-only routing was subtracted.
```

Limit:

```text
effect size is tiny compared with population-routed W
needs a stronger/readout-optimized key before promotion
```

Forbidden claims:

```text
quantum advantage
physical energy storage
thermodynamic proof
life
metabolism
homeostasis
agency
```
