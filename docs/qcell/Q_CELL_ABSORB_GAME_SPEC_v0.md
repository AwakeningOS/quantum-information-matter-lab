# Q-Cell Absorb Game Specification v0

Date: 2026-07-08

## Purpose

This document turns the Q-Cell observation line into a small game loop.

The game direction is:

```text
grow -> battle -> destabilize opponent homeostasis -> absorb one trait/wave -> transform -> stabilize -> battle again
```

The important rule is:

```text
stronger does not simply mean more stable
stronger means changed, loaded, and sometimes unstable
```

## Scientific / design boundary

This is a game prototype. It is not a biological claim and not a quantum-hardware claim.

The behavior is based on the qualitative patterns observed in `quantum-information-matter-lab`:

```text
correlation wave lags across M-C -> C-R -> R-W
internal boundary feedback vs external reflex
protect/exchange tradeoff
measurement-like sensing leaves fatigue/bias
strong repair can become overdrive
```

The browser prototype does not implement density matrices. It uses a time-lag wave model that preserves the visible behavior.

## Core difference from ordinary monster games

Ordinary monster games often say:

```text
win -> gain exp -> become stronger
```

Q-Cell Absorb says:

```text
win -> absorb trait/wave -> trait interacts with current internal state -> transform
```

The transformation must not be pure random mutation. It is context-dependent.

## Absolute rule: mutation is not pure dice

Absorption outcome is computed from:

```text
incoming_trait_load
incoming_wave_pattern
receiver_fatigue
receiver_toxicity
receiver_damage
receiver_overdrive_risk
receiver_assimilation_stability
wave_compatibility
```

Examples:

```text
fatigued receiver + high-load trait -> overdrive / rejection risk
stable receiver + compatible trait -> stable integration
opposed wave patterns -> destructive interference -> rejection or rare wave
compatible wave patterns -> constructive interference -> strengthened or new wave
```

Small noise may be used only as a tie-breaker. The dominant cause must be the interaction between incoming trait and receiver state.

## Q-Cell unit model

Each Q-Cell has:

```text
energy              0..1
toxicity            0..1
pressure            0..1
damage              0..1
fatigue             0..1
bias                0..1
boundary_integrity  0..1
openness            0..1
health              0..1
state_name          healthy / hungry / toxified / pressured / fatigued / overdrive / dormant
```

Battle traits:

```text
toxin_resistance
repair_core
pressure_wave
boundary_shell
overdrive_light
absorption_mouth
resonance_core
waste_gate
```

Wave patterns:

```text
left_to_right
right_to_left
simultaneous
double_pulse
rebound_wave
damped_oscillatory
spiral
```

## Correlation wave model

M/C/R/W are connected as:

```text
M -- C -- R -- W
```

The visible wave is the heart of the game.

A touch or attack schedules time-lag pulses:

```text
M excitation:
  M-C at +0
  C-R at +13 ticks
  R-W at +27 ticks

W excitation:
  R-W at +0
  C-R at +13 ticks
  M-C at +27 ticks

C or R excitation:
  adjacent links first, farther link later
```

Toxicity, pressure, fatigue, and bias increase dephasing, so high-load cells lose waves faster.

## Battle model

Battle is not HP damage. Battle is homeostasis disruption.

Winning means causing one of these states in the opponent:

```text
health < 0.25
boundary_integrity < 0.25
toxicity > 0.75
pressure > 0.85
damage > 0.70
overdrive envelope grows beyond threshold
```

Minimum actions:

```text
correlation_wave:
  sends a wave attack that raises opponent fatigue/damage depending on wave reach

boundary_shell:
  raises own boundary integrity and lowers intake/openness temporarily

purge_toxin:
  lowers own toxicity and pressure at energy cost

rest_cycle:
  lowers own fatigue and bias, but lets opponent recover slightly

overdrive_flash:
  high immediate disruption, raises own overdrive risk/fatigue

absorb:
  available after opponent becomes dormant/unstable; takes one trait/wave from opponent
```

## Absorption outcome model

Inputs:

```text
receiver_state
incoming_trait
incoming_wave
wave_compatibility
trait_load
```

Derived values:

```text
receiver_instability = fatigue + toxicity + damage + overdrive_risk - assimilation_stability
compatibility = wave compatibility score between receiver wave and incoming wave
trait_load = predefined load for incoming trait
absorption_pressure = trait_load + receiver_instability - compatibility
```

Outcome bands:

```text
absorption_pressure < 0.35:
  stable_integration

0.35 <= absorption_pressure < 0.65:
  altered_integration

0.65 <= absorption_pressure < 0.90:
  rejection_or_fatigue_spike

absorption_pressure >= 0.90:
  overdrive_or_dormancy
```

Rare waves can appear when destructive or constructive interference is strong but the receiver is not fully collapsed.

## Prototype scope

The first prototype should be a single HTML file:

```text
prototypes/qcell_absorb_v0.html
```

It must include:

```text
player Q-cell
enemy Q-cell
visible M-C-R-W correlation waves
battle buttons
state bars
state-dependent absorption
transformation log
```

It should not include:

```text
account system
localStorage
external libraries
large asset files
```

## What makes it fun

The fun is not just winning. The fun is deciding when to absorb.

```text
absorb while stable -> safer integration
absorb while exhausted -> possible overdrive
absorb compatible wave -> stronger pattern
absorb opposed wave -> possible rare pattern or rejection
```

The player should feel:

```text
I can win now, but should I absorb this trait right now?
Should I rest first?
Will this trait make the Q-cell stronger or ruin its balance?
```

## Prototype title

```text
Q-Cell: Assimilation
```

Japanese title:

```text
Qセル・アブソーブ
```

Catch phrase:

```text
勝て。取り込め。変質しろ。
```
