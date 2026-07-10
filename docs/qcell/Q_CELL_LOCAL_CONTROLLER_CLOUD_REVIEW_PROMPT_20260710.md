# Cloud GPT review prompt — Q-cell local controller causal test v0

Use this with the compact Stage 2 CSV/report only. Do not provide raw
multi-gigabyte logs.

## Context

We have completed the corrected fixed-circuit output bottleneck map.

Stage 2 facts:

```text
28 representative grids
100 initial states per grid
4 paired variants:
  local_resource
  local_no_resource
  central_resource
  central_no_resource
200 cycles
max energy-balance residual = 1.394440e-13
output switching cost = not_modeled
```

Primary metric:

```text
resource_attributable_W = W(local_resource) - W(local_no_resource)
```

Key Stage 2 results:

```text
highest fixed output:
  QFCBM_0488 / QFCBM_0497
  resource_attributable_W = 17.632414
  matched central = 38.374395
  fixed/central = 0.459473
  efficiency_resource_to_W = 0.521259

highest fixed efficiency:
  QFCBM_0408
  resource_attributable_W = 0.234025
  efficiency_resource_to_W = 0.560834

strong-output suppression:
  QFCBM_0496
  resource_attributable_W = 0.055903
```

## Task

Design and review the next experiment:

```text
qcell_local_controller_causal_test_v0
```

Goal:

```text
Test whether a controller that reads only local Q-cell state quantities can
beat the fixed-circuit envelope.
```

This is not the final quantum/classical comparison. It is the causal gate
before that.

## Required variants

Use matched resource/no-resource pairs.

```text
fixed_local
internal_controller
internal_shuffled_signal_controller
internal_time_shift_action_controller
output_controller
output_shuffled_signal_controller
output_time_shift_action_controller
matched_central
classical_local_controller
```

For each variant:

```text
resource
no_resource
```

## Constraints

The local controller may read only local/per-part quantities:

```text
E_E, E_A, E_B, E_C, E_D
neighbor gradients
D population
recent local flow signs if available
```

It may not read:

```text
future W output
seed identity
matched central result
global optimum
full state eigenspectrum
```

If switching work is not modeled, mark it explicitly:

```text
controller_switching_cost_status = not_modeled
```

## Ask

Please return:

1. A minimal local-controller policy family worth testing first.
2. The exact shuffled-signal and time-shuffled-action controls.
3. Whether the 6 pilot grids are sufficient:
   `QFCBM_0488`, `QFCBM_0408`, `QFCBM_0496`, `QFCBM_0988`,
   `QFCBM_0399`, `QFCBM_0441`.
4. A stop/go rule for expanding from 20 seeds to 100 seeds.
5. The exact summary columns needed for a paper-ready result.
6. Failure modes that would make an apparent gain invalid.

Do not write a full physics engine. The local Codex runner will reuse the
existing full 2^7 GPU implementation.

Do not claim purpose, life, metabolism, homeostasis, optimization, or quantum
advantage.
