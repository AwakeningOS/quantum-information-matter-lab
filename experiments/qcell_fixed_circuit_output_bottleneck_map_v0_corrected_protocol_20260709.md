# Q-cell fixed-circuit output bottleneck map v0 — corrected protocol

Status: OBSERVATION_LOG / PRE-REGISTERED_MAP

## Purpose

Before adding any local adaptive control, map the fixed-circuit upper envelope for output, efficiency, and bottleneck structure.

This protocol fixes three confounds:

1. Matched central-control reference is rerun for each grid point.
2. Initial-internal-energy-derived W output is subtracted using a no-resource baseline.
3. D-W output-layer energy conservation is checked by `[U_DW, H_D + H_W]`; switching cost is explicitly marked unaccounted unless a time-dependent coupling-work model is added.

## Main condition

```text
resource: R3 = |1>
noise: N4 dephase + amplitude damping
p: 0.06
cycles: 200
initial states stage1: 10
initial states stage2: 100
```

`R4 = |+>` is not used as the main battery condition.

## Fixed-grid sweep

```text
g_internal: 0.025, 0.05, 0.10, 0.20, 0.40
theta_in_RE: 0.05, 0.10, 0.20, 0.40, 0.80
theta_out_DW: 0.05, 0.10, 0.20, 0.40, 0.80
out_layers: 1, 2, 4, 8
structure: chain, ring
```

Total grid points:

```text
5 * 5 * 5 * 4 * 2 = 1000
```

## Required paired variants per grid point

Each grid point must be run with the exact same initial states and same noise/resource schedule.

```text
A_local_resource:
  fixed local circuit + R3 |1>

B_local_no_resource:
  same fixed local circuit + no resource

C_central_resource:
  matched central-control upper-bound circuit + R3 |1>
  same theta_in_RE, theta_out_DW, out_layers, resource schedule, noise, initial states

D_central_no_resource:
  matched central-control upper-bound circuit + no resource
```

The old central-control value `W = 1.028` is only a historical reference, not the denominator for this grid.

## Primary corrected quantities

For each seed and grid point:

```text
W_with_resource
W_without_resource
resource_attributable_W = W_with_resource - W_without_resource

central_W_with_resource
central_W_without_resource
central_resource_attributable_W = central_W_with_resource - central_W_without_resource

fixed_to_matched_central_ratio = resource_attributable_W / central_resource_attributable_W
```

If `central_resource_attributable_W` is near zero, the ratio is reported as undefined, not clipped.

## Energy/resource ledger

Save per cycle and cumulative:

```text
E_R_in
E_R_out
net_resource_transfer = E_R_in - E_R_out
E_W_out
resource_attributable_W
Delta_E_Qcell
initial_internal_energy_change = E_Qcell_initial - E_Qcell_final
Q_noise
W_external
energy_balance_residual
resource_free_energy_consumed
output_switching_cost_status
U_DW_commutator_norm
```

Balance convention:

```text
E_R_in + W_external = Delta_E_Qcell + E_R_out + E_W_out + Q_noise
```

For paired attribution, compare:

```text
resource_attributable_W = E_W_out(resource) - E_W_out(no_resource)
```

## Main efficiency

The main efficiency is:

```text
efficiency_resource_to_W = resource_attributable_W / net_resource_transfer
```

Also save:

```text
efficiency_input_to_W = resource_attributable_W / E_R_in
efficiency_free_energy_to_W = resource_attributable_W / resource_free_energy_consumed
```

If `efficiency_resource_to_W > 1`, do not mark it anomalous automatically. Decompose it by ledger terms:

```text
initial_internal_energy_change
W_external
net_resource_transfer
Q_noise
Delta_E_Qcell
energy_balance_residual
```

## Output-layer commutator check

For every `theta_out_DW` and `out_layers`, record:

```text
[U_DW(theta_out), H_D + H_W] norm
```

Expected value for ideal excitation-exchange output gate:

```text
approximately 0
```

Opening/closing the coupling is not automatically included in `W_external`. Unless an explicit time-dependent coupling-work model is implemented, record:

```text
output_switching_cost_status = "not_modeled"
```

Do not interpret the output layer as energetically free beyond the commutator check.

## Bottleneck classifications

These are map labels, not PASS/FAIL.

```text
Outlet narrow:
  D_population high, D_to_W_flow low, resource_attributable_W low, internal residual energy high

Internal transport slow:
  E/A residence high, D_population low, resource_attributable_W low

Ring circulation / trapping:
  ring residence high, D_to_W flow not proportional to internal energy,
  flow signs alternate or circulation measure high,
  resource_attributable_W lower than matched chain or matched central

Strong-output coherent overswap / output suppression:
  theta_out_DW or out_layers increases, resource_attributable_W decreases,
  D_to_W flow oscillates, D population fails to drain monotonically
```

Do not call strong-output suppression Zeno unless a measurement mechanism is explicitly modeled.

## Stage 1 to Stage 2 selection

Stage 1:

```text
1000 grid points * 10 initial states
paired variants A/B/C/D for every grid point
```

Stage 2 selects representative regions, not a single winner:

```text
top resource_attributable_W
top efficiency_resource_to_W
best fixed_to_matched_central_ratio
outlet-narrow examples
internal-transport-slow examples
ring-circulation examples
strong-output-suppression examples
chain-best region
ring-best region
```

Then rerun selected regions with:

```text
100 initial states
same paired A/B/C/D design
```

## Report first numbers

Report raw numbers before interpretation:

```text
best fixed resource_attributable_W
matched central resource_attributable_W at same grid point
fixed_to_matched_central_ratio
best efficiency_resource_to_W
no_resource_baseline_W for best points
net_resource_transfer
initial_internal_energy_change
Q_noise
max_abs_energy_balance_residual
U_DW_commutator_norm max
output_switching_cost_status
D bottleneck examples
internal transport bottleneck examples
ring circulation examples
strong-output suppression examples
```

## Non-claims

```text
No optimization claim.
No local control claim.
No purpose.
No decision-making.
No life.
No metabolism.
No self-repair.
No homeostasis.
No quantum advantage.
No PASS/FAIL.
No ranking as final truth.
```
