# Q-cell controller cost accounting v0 protocol

Date: 2026-07-10 JST

Status: post-hoc accounting experiment using existing controller-evolution
holdout detail rows.

## Purpose

The evolved controller improved held-out attributed output, but controller
switching/decision work was not modeled. This experiment asks:

```text
How much per-angle controller cost can be charged before the evolved
controller's gain over fixed disappears?
```

This does not add a physical actuator yet. It is a conservative accounting
sweep.

## Input

Use:

```text
/home/youthk/work/qcell_experiment_outputs/qcell_controller_evolution_v0_outputs/qcell_controller_evolution_v0_holdout_detail_rows.csv
```

Committed compact source:

```text
data/quantum_observation/qcell_controller_evolution_v0_holdout_grid_breakdown.csv
data/quantum_observation/qcell_controller_evolution_v0_holdout_summary.csv
```

## Cost model

Use a conservative gross controller cost:

```text
net_gain_after_cost =
  gain_over_fixed - cost_per_angle * angle_budget
```

This charges the controller for all internal controlled angle budget. It does
not subtract any equivalent cost from the fixed circuit. Therefore it is a
strict accounting screen, not a final thermodynamic actuator model.

Break-even:

```text
break_even_cost_per_angle = gain_over_fixed / angle_budget
```

If this is high, the controller effect survives larger hypothetical switching
cost. If this is near zero, the apparent gain is fragile.

## Cost sweep

Evaluate:

```text
cost_per_angle:
  0
  1e-5
  3e-5
  1e-4
  3e-4
  1e-3
  3e-3
  1e-2
  3e-2
  1e-1
```

## Outputs

```text
qcell_controller_cost_accounting_v0_seed_cost_sweep.csv
qcell_controller_cost_accounting_v0_grid_summary.csv
qcell_controller_cost_accounting_v0_manifest.json
qcell_controller_cost_accounting_v0_report_2026-07-10.md
```

## Guardrails

Do not claim:

```text
physical actuator
real work reservoir
thermodynamic closure for controller switching
life/metabolism/homeostasis
quantum advantage
```

Allowed if supported:

```text
under a conservative gross per-angle cost accounting model, the evolved
controller remains net-positive up to approximately X cost per angle in a
given region
```

