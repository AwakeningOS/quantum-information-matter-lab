# Cloud review prompt — Q-cell battery-powered controller v0

Review the attached protocol:

```text
experiments/qcell_battery_powered_controller_v0_protocol_20260710.md
```

Context:

```text
Fixed circuit envelope is complete.
Local controller causal test showed selected-region gains.
Evolution v0 improved the local controller on held-out seeds.
Cost accounting v0 showed:
  QFCBM_0988 robust to cost_per_angle up to 0.03
  QFCBM_0496 robust to 0.0003
  QFCBM_0399 fragile
```

Question:

```text
Is the proposed finite-M controller battery model a fair next step, or does it
still leave a loophole where control is effectively free?
```

Please return:

1. Whether `M_energy -= kappa * angle_budget` is an acceptable v0 actuator
   accounting model.
2. Whether action scaling under insufficient M energy is the right starvation
   behavior.
3. Which kappa/M_initial grid is minimal but decisive.
4. Which controls are mandatory.
5. What would count as a clean positive result.
6. What would invalidate the result.

Do not introduce life, metabolism, homeostasis, agency, quantum advantage, or
QPU claims.

