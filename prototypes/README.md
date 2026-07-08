# Prototypes

## Q-Cell: Assimilation v2 mutation/evolution

File:

```text
prototypes/qcell_absorb_v2_mutation_evolution.html
```

Open it directly in a browser. It has no external dependencies and does not use localStorage.

Why v2 exists:

```text
v1 made button effects readable, but mutation still felt like a log line.
v2 makes absorption change the visible organism: form, organs, wave, and future behavior.
```

Added game-state features:

```text
visible form changes: 幼体 / 境界型 / 共鳴型 / 回復型 / 暴走型 / 吸収型 / 休眠殻型
new organ acquisition after absorption
wave-pattern changes after rare/interference mutation
absorption count and generation counter
cultivation failure state with operation lock
re-cultivation button
stabilization action after risky absorption
```

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
