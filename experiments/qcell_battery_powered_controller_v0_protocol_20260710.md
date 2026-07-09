# Q-cell battery-powered controller v0 protocol

Date: 2026-07-10 JST

Status: design-review protocol, not yet executed.

## Purpose

Replace post-hoc controller-cost accounting with an explicit controller-energy
model.

Core question:

```text
If the local controller must pay for its own adjustments from a finite
battery/control reservoir, does the evolved controller still produce net
resource-attributable W gain?
```

## Starting point

Use the best evolved controller from `qcell_controller_evolution_v0`:

```text
gain = 0.895497
leak = 0.0
downstream_bias = 1.616854
ad_gate = 1.272455
d_block = 1.241107
max_angle_mult = 1.911673
```

Cost accounting result:

```text
QFCBM_0988:
  min break-even cost_per_angle ≈ 0.042163
  all-seed positive through swept cost_per_angle = 0.03

QFCBM_0496:
  min break-even cost_per_angle ≈ 0.000673
  all-seed positive through swept cost_per_angle = 0.0003

QFCBM_0399:
  fragile; min break-even cost_per_angle ≈ 0.000039
```

## Proposed explicit actuator model

Add a controller battery/reservoir `M` as an accounting object first, not a new
coherent qubit.

At each cycle:

```text
controller computes intended internal link angles
controller_angle_budget_this_cycle = sum(abs(dynamic_angles))
controller_cost = kappa * controller_angle_budget_this_cycle
M_energy -= controller_cost
```

If `M_energy` is insufficient:

```text
scale all dynamic internal angles by M_energy / controller_cost
M_energy -> 0
```

This makes controller action resource-limited.

## Conditions

Primary grids:

```text
QFCBM_0988  robust high-output ring
QFCBM_0496  moderate-cost strong-output-suppression region
QFCBM_0399  fragile negative control / marginal region
```

Seeds:

```text
holdout seeds 20260750-20260809
```

Cost levels:

```text
kappa = 0
kappa = 0.0001
kappa = 0.0003
kappa = 0.001
kappa = 0.003
kappa = 0.01
kappa = 0.03
```

Battery levels:

```text
M_initial_energy = unlimited
M_initial_energy = 20
M_initial_energy = 5
M_initial_energy = 1
M_initial_energy = 0.2
```

## Required controls

```text
fixed circuit
evolved controller with M battery
hand-coded controller with M battery
zero-battery controller
resource/no_resource paired variants
```

## Primary outputs

```text
W_resource
W_no_resource
resource_attributable_W
controller_energy_spent
M_energy_final
controller_starved_cycles
net_gain_after_controller_cost
gain_over_fixed
gain_over_hand_coded
```

## Failure conditions

Stop or do not promote if:

```text
gain exists only when M is unlimited
gain disappears for realistic kappa near cost-accounting break-even
gain is caused by lowering W_no_resource
controller consumes more energy than added W gain
QFCBM_0988 only succeeds while QFCBM_0496/QFCBM_0399 collapse
```

## Guardrails

Do not claim:

```text
real thermodynamic work
physical metabolism
homeostasis
life
agency
quantum advantage
```

Allowed if supported:

```text
under an explicit finite controller-energy accounting model, the controller
remained net-positive in selected regions
```

