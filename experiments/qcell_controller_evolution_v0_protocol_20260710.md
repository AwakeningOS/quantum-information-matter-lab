# Q-cell controller evolution v0 protocol

Date: 2026-07-10 JST

Status: protocol draft after local-controller causal test v0.

## Purpose

Search for better local controller parameters by trial-and-error, while
preventing the usual reward hacks:

```text
no_resource subtraction trick
extra action budget
resource over-consumption
output-only overswap tuning
training-seed overfit
unmodeled switching-work efficiency claim
```

This is not deep reinforcement learning. It is a small evolutionary /
random-search controller-parameter experiment using the existing full 2^7
GPU simulation.

## Starting evidence

The hand-coded budgeted local-gradient internal controller already beat the
fixed circuit in selected regions.

100-seed confirmation:

```text
QFCBM_0988:
  fixed attributed W = 15.840497
  local internal attributed W = 26.024037
  gain over fixed = 10.183540
  beat shuffled-signal/time-shift controls = 100/100 seeds

QFCBM_0496:
  fixed attributed W = 0.055903
  local internal attributed W = 0.258512
  gain over fixed = 0.202609
  beat shuffled-signal/time-shift controls = 100/100 seeds

QFCBM_0399:
  fixed attributed W = 0.007974
  local internal attributed W = 0.017535
  gain over fixed = 0.009561
  beat time-shift action = 64/100 seeds
```

## Controller parameterization

Use a small interpretable parameter vector. Do not use a neural network in v0.

```text
gain              # gradient sharpness
leak              # minimum uniform background allocation
downstream_bias   # extra preference for later links
ad_gate           # ring AD bypass multiplier
d_block           # penalty when downstream D is already high
max_angle_mult    # cap relative to g_internal
```

Initial hand-coded controller corresponds approximately to:

```text
gain = 1.0
leak = 0.0
downstream_bias = 1.0
ad_gate = 1.0
d_block = 1.0
max_angle_mult = 2.0
```

Budget constraint:

```text
sum internal angles per cycle <= fixed internal angle budget per cycle
max link angle <= min(max_angle_mult * g_internal, 0.8)
```

In v0, optimize internal links only. Keep `RE` inlet and `DW` outlet fixed.

## Search grids

Use the two clean local-controller wins plus the marginal internal-transport
case:

```text
QFCBM_0988  clean high-output ring win
QFCBM_0496  clean strong-output-suppression win
QFCBM_0399  marginal timing-sensitive case
```

## Train / validation / holdout split

Do not evaluate final claims on the same seeds used for selection.

```text
train seeds:      20260710-20260729  # 20 seeds
validation seeds: 20260730-20260749  # 20 seeds
holdout seeds:    20260750-20260809  # 60 seeds
```

## Evolution schedule

Keep v0 small.

```text
population = 24 controllers
generations = 5
parents kept = 6
mutations per generation = 18
grids during training = QFCBM_0988, QFCBM_0496, QFCBM_0399
train seeds per candidate = 20
```

Total training evaluations:

```text
24 initial + 4 * 18 mutations = 96 candidate evaluations
```

Each candidate evaluation runs resource/no_resource pairs and compares against
cached fixed baselines.

## Objective

Primary score:

```text
score =
  mean_over_grids_and_train_seeds(
    resource_attributable_W(candidate)
    - resource_attributable_W(fixed)
  )
```

Penalties:

```text
if W_resource_delta_vs_fixed <= 0 and W_no_resource_delta_vs_fixed < 0:
  subtract no_resource_trick_penalty

if internal_angle_budget > fixed_internal_angle_budget:
  reject candidate

if net_resource_transfer increases but efficiency does not:
  record as output-only/resource-use gain, not conversion gain
```

Tie-breaks:

```text
1. positive median gain
2. positive seed count
3. lower angle budget
4. stronger validation score
```

## Validation and holdout

After evolution:

```text
top 6 candidates -> validation seeds
best 2 candidates + hand-coded baseline -> holdout seeds
```

A candidate is interesting only if:

```text
holdout gain over fixed is positive
holdout gain over hand-coded local controller is positive
gain is not due to lowering W_no_resource
angle budget remains <= fixed budget
```

## Saved compact artifacts

```text
qcell_controller_evolution_v0_candidate_history.csv
qcell_controller_evolution_v0_validation_summary.csv
qcell_controller_evolution_v0_holdout_summary.csv
qcell_controller_evolution_v0_best_params.json
qcell_controller_evolution_v0_manifest.json
qcell_controller_evolution_v0_report_2026-07-10.md
```

Raw per-seed logs stay outside the repository under:

```text
/home/youthk/work/qcell_experiment_outputs/
```

## Guardrails

Do not claim:

```text
purpose
understanding
autonomous agency
life
metabolism
homeostasis
quantum advantage
global optimum
efficiency improvement while switching work is not modeled
```

Allowed if supported:

```text
evolutionary search found a parameterized local controller that improved
resource-attributable W over the hand-coded local controller on held-out seeds
```

