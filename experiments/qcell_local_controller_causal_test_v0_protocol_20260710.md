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

internal_controller_resource
internal_controller_no_resource

internal_shuffled_signal_resource
internal_shuffled_signal_no_resource

internal_time_shift_action_resource
internal_time_shift_action_no_resource

output_controller_resource
output_controller_no_resource

output_shuffled_signal_resource
output_shuffled_signal_no_resource

output_time_shift_action_resource
output_time_shift_action_no_resource

matched_central_resource
matched_central_no_resource

classical_local_controller_resource
classical_local_controller_no_resource
```

Minimum variants for a smoke run:

```text
fixed_local_resource
fixed_local_no_resource
internal_controller_resource
internal_controller_no_resource
internal_shuffled_signal_resource
internal_shuffled_signal_no_resource
internal_time_shift_action_resource
internal_time_shift_action_no_resource
matched_central_resource
matched_central_no_resource
```

## Controller policy families

Pilot v0 separates internal transport changes from output timing changes.
Do not combine them until each is understood separately.

### P0 fixed

The Stage 2 fixed local circuit.

```text
RE inlet: fixed
internal links: fixed
DW outlet: fixed
```

### P1 internal-only budgeted local gradient

Main causal candidate.

```text
RE inlet: fixed
DW outlet: fixed
internal links only: adjusted
```

Per link, the controller reads local part energies and adjusts only the local
link angle. The total internal angle budget must be no greater than the fixed
circuit budget for the same grid/cycle.

Initial deterministic rule family:

```text
For directed chain links E-A, A-B, B-C, C-D:
  if upstream_energy > downstream_energy:
    give that link extra budget
  else:
    reduce that link

For ring AD:
  treat A-D as an auxiliary bypass only when D is below its running median-like
  local threshold and A has higher energy than D.

Normalize all internal link angles so:
  sum(dynamic internal angles) <= sum(fixed internal angles)
  max_link_angle <= max(2 * g_internal, 0.8)
```

No RE or DW change is allowed in this variant.

### P2 output-only budgeted D gate

Separate outlet-timing diagnostic.

```text
RE inlet: fixed
internal links: fixed
DW outlet only: controlled
```

This tests whether strong-output overswap/suppression can be reduced by using
D state to time the outlet. It is not credited as internal coordination unless
it is clearly separated from P1.

Initial deterministic rule family:

```text
if D_population is above a local threshold:
  open DW for this cycle using fixed theta_out_DW/out_layers budget
else:
  skip or reduce DW outlet action

Total DW outlet angle budget over the run must be <= the fixed-circuit DW
budget for the same grid.
```

### P3 combined internal plus output

Optional later condition only. Do not use it as the main pilot decision.

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
QFCBM_0399  internal transport / wasted-transfer example
QFCBM_0441  bad ratio example
```

Pilot scale:

```text
6 grids
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
internal_controller_gain_over_fixed =
  resource_attributable_W(internal_controller)
  - resource_attributable_W(fixed_local)

output_controller_gain_over_fixed =
  resource_attributable_W(output_controller)
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
per_link_angle_budget
max_link_angle
controller_action_count_by_link
controller_angle_budget_by_link
controller_output_action_count
controller_internal_action_count
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
per_link_angle_budget
max_link_angle
controller_action_count_by_link
controller_angle_budget_by_link
controller_output_action_count
controller_internal_action_count
controller_switching_cost_status
signal_shuffle_seed
time_shift_amount
action_source_variant
```

Paired grid summary:

```text
fixed_resource_attributable_W
internal_controller_resource_attributable_W
internal_shuffled_signal_resource_attributable_W
internal_time_shift_resource_attributable_W
output_controller_resource_attributable_W
output_shuffled_signal_resource_attributable_W
output_time_shift_resource_attributable_W
matched_central_resource_attributable_W
classical_controller_resource_attributable_W

internal_gain_over_fixed
internal_gain_over_shuffled_signal
internal_gain_over_time_shift
output_gain_over_fixed
output_gain_over_shuffled_signal
output_gain_over_time_shift
controller_to_central_ratio

W_resource_delta_vs_fixed
W_no_resource_delta_vs_fixed
resource_attributable_delta_vs_fixed
```

## Shuffled controls

### Shuffled signal controller

The signal distribution is preserved but the current-state/seed pairing is
broken.

```text
same grid_id
same controller family
same resource/no_resource status
same cycle t
derangement shuffle across seeds
```

The state being acted on remains the original seed state. The controller reads
local signals from another seed in the same grid/status/cycle.

Do not shuffle across grids, resource status, cycles, or central-control runs.

### Time-shifted action controller

Primary action timing control:

```text
A_control[g, seed, t, link] = A[g, seed, (t + 37) mod 200, link]
```

This preserves total action amount and link distribution but breaks current
state/action timing. A full random time permutation may be added later but is
not the primary control.

## 20-seed pilot stop/go rule

Proceed to 100 seeds only if:

```text
all variants finite
all paired resource/no_resource rows complete
energy_balance_residual_max_abs <= 1e-4
controller_angle_budget <= fixed angle budget, or excess is explicitly labeled
median gain over fixed is positive
median gain over shuffled signal is positive
median gain over time-shift action is positive
paired seeds improved:
  >= 14/20 over fixed
  >= 13/20 over shuffled signal
  >= 13/20 over time-shift action
gain >= 5% of fixed-to-central gap
```

For low-output conditions, also require:

```text
gain >= max(0.02, 5% of fixed resource_attributable_W)
```

Stop if improvement comes only from lowering `W_no_resource`, if action budget
exceeds the fixed budget without being labeled, or if gains appear only in
`QFCBM_0496` output timing.

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
