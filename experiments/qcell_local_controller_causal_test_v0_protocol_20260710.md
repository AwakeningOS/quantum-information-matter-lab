# Q-cell local controller causal test v0 protocol

Date: 2026-07-10 JST

Status: protocol draft for the next experiment after fixed-circuit Stage 2.

## Purpose

Test whether local state-dependent controller actions improve resource-driven
Q-cell output beyond the fixed-circuit envelope.

This is not a quantum/classical advantage test. It is the causal gate before
the later fair quantum/classical comparison.

## Background fixed-circuit baseline

The corrected fixed-circuit bottleneck map established the baseline envelope.

Stage 2 facts:

```text
selected grids = 28
seeds per grid = 100
variants per grid = 4
cycles = 200
max energy-balance residual = 1.394440e-13
```

High-output fixed region:

```text
QFCBM_0488 / QFCBM_0497
structure = chain
g_internal = 0.4
theta_in_RE = 0.8
effective outlet angle = 0.8
resource_attributable_W_mean = 17.632414
matched central = 38.374395
fixed/central ratio = 0.459473
efficiency_resource_to_W = 0.521259
```

High-efficiency fixed region:

```text
QFCBM_0408
structure = chain
g_internal = 0.4
theta_in_RE = 0.05
effective outlet angle = 0.8
resource_attributable_W_mean = 0.234025
efficiency_resource_to_W = 0.560834
```

Strong-output suppression example:

```text
QFCBM_0496
structure = chain
g_internal = 0.4
theta_in_RE = 0.8
effective outlet angle = 3.2
resource_attributable_W_mean = 0.055903
```

## Core question

```text
Does a controller that reads only local part/state information produce higher
resource_attributable_W than the matched fixed circuit?
```

## Required comparison variants

Each selected grid must be run with the same seeds, resource schedule, noise,
cycle count, and output definition.

```text
fixed_local_resource
fixed_local_no_resource

local_controller_resource
local_controller_no_resource

shuffled_signal_controller_resource
shuffled_signal_controller_no_resource

time_shuffled_action_controller_resource
time_shuffled_action_controller_no_resource

matched_central_resource
matched_central_no_resource

classical_local_controller_resource
classical_local_controller_no_resource
```

Minimum variants for a smoke run:

```text
fixed_local_resource
fixed_local_no_resource
local_controller_resource
local_controller_no_resource
shuffled_signal_controller_resource
shuffled_signal_controller_no_resource
matched_central_resource
matched_central_no_resource
```

## Controller information limits

The local controller may read only per-cycle quantities already available from
the Q-cell body, such as:

```text
E_E, E_A, E_B, E_C, E_D
local gradients between neighbors
D_population / E_D
recent local flow signs if computed from local links
```

It must not read:

```text
future W output
global optimum over the state
seed identity
matched central-control result
raw full density matrix eigenstructure unless explicitly routed as a separate diagnostic
```

## Initial pilot grids

Use a small pilot before any wide run.

```text
QFCBM_0488  high fixed output
QFCBM_0408  high efficiency, low output
QFCBM_0496  strong-output suppression
QFCBM_0988  best ring representative
QFCBM_0441  bad ratio example
```

Pilot scale:

```text
5 grids
20 seeds
200 cycles
matched resource/no-resource pairs
compact summaries only
```

Expansion scale if pilot is numerically stable:

```text
5-10 grids
100 seeds
same variants
compact summaries plus selected cyclewise diagnostics
```

## Primary metric

Use paired attribution:

```text
resource_attributable_W =
  W(variant_resource) - W(variant_no_resource)
```

Controller improvement:

```text
controller_gain_over_fixed =
  resource_attributable_W(local_controller)
  - resource_attributable_W(fixed_local)
```

Matched central fraction:

```text
controller_to_central_ratio =
  resource_attributable_W(local_controller)
  / resource_attributable_W(matched_central)
```

## Causal checks

The local controller is not credited unless it beats the causal controls.

Required comparisons:

```text
local_controller > fixed_local
local_controller > shuffled_signal_controller
local_controller > time_shuffled_action_controller
local_controller approaches matched_central without using global state
```

If local controller beats fixed but not shuffled/time-shuffled controls, the
effect is treated as extra actuation or schedule artifact, not local
state-dependent coordination.

## Energy and switching-work caveat

If controller actions change coupling strengths or output openings, the report
must record:

```text
controller_action_count
controller_angle_budget
controller_switching_cost_status
```

If switching work is not modeled, report:

```text
controller_switching_cost_status = not_modeled
```

Do not call the behavior efficient, autonomous, or optimized until controller
work is accounted for.

## Minimal saved outputs

Per seed/variant summary:

```text
grid_id
controller_variant
seed
structure
g_internal
theta_in_RE
theta_out_DW
out_layers
n_cycles

E_R_in_cum
E_R_out_cum
net_resource_transfer
E_W_out_cum
resource_free_energy_consumed_cum
Delta_E_Qcell_cum
Q_noise_cum
W_external_cum
energy_balance_residual_max_abs

D_population_mean
D_population_peak
D_to_W_flow_cum
residence_E
residence_A
residence_B
residence_C
residence_D

controller_action_count
controller_angle_budget
controller_switching_cost_status
```

Paired grid summary:

```text
fixed_resource_attributable_W
local_controller_resource_attributable_W
shuffled_signal_resource_attributable_W
time_shuffled_resource_attributable_W
matched_central_resource_attributable_W
classical_controller_resource_attributable_W

controller_gain_over_fixed
controller_gain_over_shuffled_signal
controller_gain_over_time_shuffled
controller_to_central_ratio
```

## Report guardrails

Do not claim:

```text
purpose
understanding
optimization
autonomous agency
life
metabolism
homeostasis
repair
quantum advantage
```

Allowed if supported:

```text
local state-dependent controller improved attributed output over fixed circuit
local controller effect survived shuffled-signal/action controls
fixed-circuit envelope was or was not exceeded
```

