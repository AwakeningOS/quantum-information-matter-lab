# Q-cell controller cost accounting v0

Date: 2026-07-10 JST

## Scope

Post-hoc conservative controller-cost accounting for controller evolution v0. This is not a physical actuator model. It asks how much gross per-angle cost can be charged before controller gains disappear.

Cost model:

```text
net_gain_after_cost = gain_over_fixed - cost_per_angle * angle_budget
```

This charges the controller for all internal controlled angle budget and does not credit the fixed circuit with any equivalent operation cost, so it is conservative.

## Run facts

- input rows after de-duplication: 360
- costs swept: [0.0, 1e-05, 3e-05, 0.0001, 0.0003, 0.001, 0.003, 0.01, 0.03, 0.1]

## Break-even summary

| candidate_id | grid_id | mean_gain_before_cost | mean_angle_budget | min_break_even_cost_per_angle | mean_break_even_cost_per_angle | max_swept_cost_all_seed_positive | no_resource_trick_count | max_budget_excess |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gen2_mut008_from_gen1_mut008_from_hand_coded | QFCBM_0399 | 0.008031 | 152.298233 | 3.899e-05 | 5.271e-05 | 3.000e-05 | 0.000000 | 0.000000 |
| gen2_mut008_from_gen1_mut008_from_hand_coded | QFCBM_0496 | 0.203827 | 290.232737 | 0.000673 | 0.000702 | 0.000300 | 0.000000 | 0.000000 |
| gen2_mut008_from_gen1_mut008_from_hand_coded | QFCBM_0988 | 13.449729 | 302.139762 | 0.042163 | 0.044493 | 0.030000 | 0.000000 | 0.000000 |
| hand_coded | QFCBM_0399 | 0.009971 | 152.406800 | 3.772e-05 | 6.541e-05 | 3.000e-05 | 0.000000 | 0.000000 |
| hand_coded | QFCBM_0496 | 0.179294 | 282.695469 | 0.000607 | 0.000634 | 0.000300 | 0.000000 | 0.000000 |
| hand_coded | QFCBM_0988 | 9.784250 | 351.766476 | 0.026620 | 0.027809 | 0.010000 | 0.000000 | 0.000000 |

## Readout

- `QFCBM_0988` is robust to controller cost. The evolved controller remains positive for every holdout seed up to swept `cost_per_angle = 0.03`; its minimum seed-level break-even is about `0.04216`.
- `QFCBM_0496` is moderately cost-sensitive. The evolved controller remains all-seed positive up to swept `0.0003`; minimum break-even is about `0.000673`.
- `QFCBM_0399` is fragile. It remains all-seed positive only up to swept `0.00003`; minimum break-even is about `0.000039`.
- The evolved controller is more cost-robust than hand-coded on `QFCBM_0988` and slightly more robust on `QFCBM_0496`, but not on `QFCBM_0399`.

## Claim ceiling

Allowed:

```text
Under a conservative gross per-angle accounting model, the evolved controller remains net-positive at nonzero hypothetical controller costs in selected regions, especially QFCBM_0988.
```

Not allowed:

```text
physical controller work has been modeled
thermodynamic closure for controller switching
metabolism/homeostasis
quantum advantage
```
