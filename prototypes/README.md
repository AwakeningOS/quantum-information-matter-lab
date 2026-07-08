# Prototypes

## Q-Cell: Assimilation v1 battle readability

File:

```text
prototypes/qcell_absorb_v1_battle_readability.html
```

Open it directly in a browser. It has no external dependencies and does not use localStorage.

Why v1 exists:

```text
v0 moved the parameters, but the player could not tell what the button press meant.
v1 translates numeric changes into immediate action feedback.
```

Added readability features:

```text
current objective banner
large action-result message
action delta log: health/fatigue/damage/pressure/toxicity changes
absorption prediction panel
live absorption-pressure formula
absorbable state banner
small reaction codex
```

## Q-Cell: Assimilation v0

File:

```text
prototypes/qcell_absorb_v0.html
```

Open it directly in a browser. It has no external dependencies and does not use localStorage.

Prototype loop:

```text
player Q-cell vs enemy Q-cell
correlation-wave battle
opponent homeostasis disruption
trait absorption after opponent collapse
state-dependent mutation / transformation
```

Core design rule:

```text
unexpected change is not pure random mutation
unexpected change comes from absorbed trait load × current receiver state × wave compatibility
```

The visible heart is the M-C-R-W correlation wave.
