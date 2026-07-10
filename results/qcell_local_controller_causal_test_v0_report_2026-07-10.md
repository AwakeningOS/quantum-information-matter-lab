# Q-cell local controller causal test v0

Date: 2026-07-10 JST

## Scope

This experiment tests whether a budgeted local state-dependent controller can beat the fixed-circuit envelope. It is not a quantum/classical advantage test and does not claim purpose, agency, optimization, life, metabolism, repair, or homeostasis.

Raw outputs are stored outside the repository:

```text
/home/youthk/work/qcell_experiment_outputs/qcell_local_controller_causal_test_v0_pilot_outputs
/home/youthk/work/qcell_experiment_outputs/qcell_local_controller_causal_test_v0_confirm_outputs
```

## Design

- Pilot: 6 selected grids, 20 seeds, 16 variants including fixed, internal, output, shuffled-signal, time-shift, and matched-central pairs.
- Confirmation: 3 GO grids, 100 seeds, internal-only variants plus fixed and matched central.
- Primary metric: `resource_attributable_W = W_resource - W_no_resource`.
- Internal controller angle budget was constrained below the fixed internal angle budget.
- Switching cost remains `not_modeled`, so efficiency/optimization claims are not promoted.

## 20-seed pilot summary

| grid_id | fixed_resource_attributable_W_mean | internal_resource_attributable_W_mean | internal_gain_over_fixed_mean | internal_n_gain_over_fixed_positive | internal_gain_over_shuffled_signal_mean | internal_n_gain_over_shuffled_signal_positive | internal_gain_over_time_shift_mean | internal_n_gain_over_time_shift_positive | output_gain_over_fixed_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QFCBM_0399 | 0.007940 | 0.017881 | 0.009941 | 20.000000 | 0.016849 | 20.000000 | 0.000821 | 14.000000 | 1.733e-05 |
| QFCBM_0408 | 0.233334 | 0.207726 | -0.025608 | 0.000000 | 0.198788 | 20.000000 | 0.010148 | 20.000000 | -0.225898 |
| QFCBM_0441 | 0.048930 | 0.039976 | -0.008954 | 0.000000 | 0.020467 | 20.000000 | 0.004815 | 20.000000 | -0.045662 |
| QFCBM_0488 | 17.581467 | 16.360956 | -1.220511 | 0.000000 | 13.826299 | 20.000000 | 2.143658 | 20.000000 | -1.561792 |
| QFCBM_0496 | 0.055585 | 0.258068 | 0.202482 | 20.000000 | 0.216946 | 20.000000 | 0.038508 | 20.000000 | 0.025563 |
| QFCBM_0988 | 15.814952 | 25.895871 | 10.080919 | 20.000000 | 10.933892 | 20.000000 | 2.527884 | 20.000000 | -3.744686 |

Pilot GO grids for internal-only 100-seed confirmation:

```text
QFCBM_0399  marginal but positive over fixed/shuffled/time-shift in pilot
QFCBM_0496  strong-output suppression region; internal controller robustly improved
QFCBM_0988  ring high-output region; internal controller robustly improved
```

## 100-seed confirmation summary

| grid_id | fixed_resource_attributable_W_mean | central_resource_attributable_W_mean | internal_resource_attributable_W_mean | internal_gain_over_fixed_mean | internal_n_gain_over_fixed_positive | internal_gain_over_shuffled_signal_mean | internal_n_gain_over_shuffled_signal_positive | internal_gain_over_time_shift_mean | internal_n_gain_over_time_shift_positive | internal_W_resource_delta_vs_fixed_mean | internal_W_no_resource_delta_vs_fixed_mean | internal_no_resource_trick_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QFCBM_0399 | 0.007974 | 0.195749 | 0.017535 | 0.009561 | 100.000000 | 0.016375 | 100.000000 | 0.000527 | 64.000000 | 0.012512 | 0.002951 | 0.000000 |
| QFCBM_0496 | 0.055903 | 0.353956 | 0.258512 | 0.202609 | 100.000000 | 0.215405 | 100.000000 | 0.037659 | 100.000000 | 0.213229 | 0.010620 | 0.000000 |
| QFCBM_0988 | 15.840497 | 38.404064 | 26.024037 | 10.183540 | 100.000000 | 14.554753 | 100.000000 | 2.575167 | 100.000000 | 10.386552 | 0.203012 | 0.000000 |

## Budget check

| grid_id | internal budget mean | fixed internal budget | max link angle |
| --- | ---: | ---: | ---: |
| QFCBM_0399 | 152.595265 | 160.000000 | 0.400000 |
| QFCBM_0496 | 281.196119 | 320.000000 | 0.800000 |
| QFCBM_0988 | 348.806035 | 400.000000 | 0.800000 |

## Readout

- `QFCBM_0988`: internal controller remained above fixed, shuffled-signal, and time-shift controls across all 100 seeds. Mean gain over fixed: `10.183540`.
- `QFCBM_0496`: internal controller remained above fixed, shuffled-signal, and time-shift controls across all 100 seeds. Mean gain over fixed: `0.202609`.
- `QFCBM_0399`: internal controller remained above fixed and shuffled-signal across all 100 seeds, but only 64/100 seeds exceeded the time-shift action control. Treat as marginal/timing-sensitive, not clean.
- No confirmed internal-controller gain was produced by lowering `W_no_resource` alone; `internal_no_resource_trick_count = 0` in all confirmation grids.

## Current claim ceiling

Allowed:

```text
In selected fixed-circuit regions, a budgeted local-gradient internal controller increased resource-attributable W over the fixed circuit, and in two regions also beat shuffled-signal and time-shift action controls across all 100 seeds.
```

Not allowed:

```text
optimization
purpose
agency
life/metabolism/homeostasis/repair
quantum advantage
efficiency improvement after controller switching work
```
