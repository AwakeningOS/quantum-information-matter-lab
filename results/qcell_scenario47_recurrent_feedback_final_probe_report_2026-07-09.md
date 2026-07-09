# Q-cell scenario 47 recurrent feedback final probe v0

Status: OBSERVATION_LOG

## Run shape

```text
scenario: 47
conditions: A baseline dephase_AD p=0.18 / B no dephase unitary / C all-part uniform dephase p=0.18
initial states: 100 random_product seeds, integer IDs 20260710..20260809
repetitions: 100 without reinitialization
checkpoints: 0, 1, 2, 3, 5, 10, 20, 50, 50_after_stimulus, 100
small stimulus: touch_B strength=0.10 after iteration 50
counterfactual: no-stimulus branch from iteration 50 to 100
```

## Primary numbers: state distances and coherence variance

| condition | iteration_label | mean_pair_trace_distance | max_pair_trace_distance | coherence_var | coherence_mean | purity_mean |
|---|---|---|---|---|---|---|
| A_baseline_dephase_AD_p018 | 0 | 0.461998 | 0.795588 | 3.80886 | 5.16167 | 1 |
| A_baseline_dephase_AD_p018 | 1 | 0.427136 | 0.786965 | 0.457084 | 7.95141 | 0.640272 |
| A_baseline_dephase_AD_p018 | 2 | 0.382522 | 0.694273 | 0.185611 | 6.61098 | 0.338998 |
| A_baseline_dephase_AD_p018 | 3 | 0.314269 | 0.598773 | 0.153036 | 4.56584 | 0.207904 |
| A_baseline_dephase_AD_p018 | 5 | 0.218929 | 0.435948 | 0.0328477 | 2.65507 | 0.107391 |
| A_baseline_dephase_AD_p018 | 10 | 0.121567 | 0.269984 | 0.0147639 | 1.16997 | 0.0728427 |
| A_baseline_dephase_AD_p018 | 20 | 0.0515396 | 0.120417 | 0.00318387 | 0.386835 | 0.0642225 |
| A_baseline_dephase_AD_p018 | 50 | 0.00446177 | 0.0102198 | 3.17596e-05 | 0.0342276 | 0.0625125 |
| A_baseline_dephase_AD_p018 | 50_after_stimulus | 0.00446177 | 0.0102198 | 3.23247e-05 | 0.0342143 | 0.0625125 |
| A_baseline_dephase_AD_p018 | 100 | 7.86942e-05 | 0.000179611 | 4.86756e-09 | 0.000618934 | 0.0625 |
| B_no_dephase_unitary | 0 | 0.461998 | 0.795588 | 3.80886 | 5.16167 | 1 |
| B_no_dephase_unitary | 1 | 0.461998 | 0.795588 | 0.882508 | 10.6359 | 1 |
| B_no_dephase_unitary | 2 | 0.461998 | 0.795588 | 0.366354 | 12.3506 | 1 |
| B_no_dephase_unitary | 3 | 0.461998 | 0.795588 | 0.977562 | 11.4585 | 1 |
| B_no_dephase_unitary | 5 | 0.461998 | 0.795588 | 0.634392 | 11.5937 | 1 |
| B_no_dephase_unitary | 10 | 0.461998 | 0.795588 | 0.380028 | 12.3828 | 1 |
| B_no_dephase_unitary | 20 | 0.461998 | 0.795588 | 0.47106 | 11.0637 | 1 |
| B_no_dephase_unitary | 50 | 0.461998 | 0.795588 | 0.186771 | 13.1439 | 1 |
| B_no_dephase_unitary | 50_after_stimulus | 0.461998 | 0.795588 | 0.19484 | 13.146 | 1 |
| B_no_dephase_unitary | 100 | 0.461998 | 0.795588 | 0.567752 | 12.1668 | 1 |
| C_uniform_all_dephase_p018 | 0 | 0.461998 | 0.795588 | 3.80886 | 5.16167 | 1 |
| C_uniform_all_dephase_p018 | 1 | 0.369906 | 0.71513 | 0.261922 | 5.8414 | 0.350406 |
| C_uniform_all_dephase_p018 | 2 | 0.225493 | 0.441612 | 0.0403971 | 3.33855 | 0.136235 |
| C_uniform_all_dephase_p018 | 3 | 0.130606 | 0.248889 | 0.00962975 | 1.5567 | 0.0796734 |
| C_uniform_all_dephase_p018 | 5 | 0.0406423 | 0.0757025 | 0.00117521 | 0.453647 | 0.0638474 |
| C_uniform_all_dephase_p018 | 10 | 0.00305686 | 0.00641122 | 8.09289e-06 | 0.0238003 | 0.0625047 |
| C_uniform_all_dephase_p018 | 20 | 2.52371e-05 | 5.9633e-05 | 8.91509e-10 | 0.000166068 | 0.0625 |
| C_uniform_all_dephase_p018 | 50 | 2.59717e-11 | 6.89114e-11 | 1.00963e-21 | 1.12601e-10 | 0.0625 |
| C_uniform_all_dephase_p018 | 50_after_stimulus | 2.59717e-11 | 6.89114e-11 | 1.01479e-21 | 1.12473e-10 | 0.0625 |
| C_uniform_all_dephase_p018 | 100 | 2.89561e-16 | 1.35308e-15 | 9.47989e-33 | 2.88325e-15 | 0.0625 |

## Previous-iteration distance

| condition | iteration | mean_prev_trace_distance | max_prev_trace_distance | mean_prev_frobenius | max_prev_frobenius |
|---|---|---|---|---|---|
| A_baseline_dephase_AD_p018 | 1 | 0.923808 | 0.982901 | 1.17845 | 1.28712 |
| A_baseline_dephase_AD_p018 | 10 | 0.354156 | 0.447593 | 0.188786 | 0.234313 |
| A_baseline_dephase_AD_p018 | 20 | 0.151066 | 0.188653 | 0.0778647 | 0.0992422 |
| A_baseline_dephase_AD_p018 | 50 | 0.0129204 | 0.0159983 | 0.00664274 | 0.00841764 |
| A_baseline_dephase_AD_p018 | 100 | 0.000211578 | 0.000264076 | 0.000108618 | 0.000135988 |
| B_no_dephase_unitary | 1 | 0.929898 | 0.990013 | 1.31507 | 1.40009 |
| B_no_dephase_unitary | 50 | 0.929898 | 0.990013 | 1.31507 | 1.40009 |
| B_no_dephase_unitary | 100 | 0.928666 | 0.990376 | 1.31333 | 1.4006 |
| C_uniform_all_dephase_p018 | 1 | 0.869441 | 0.935811 | 1.01498 | 1.10003 |
| C_uniform_all_dephase_p018 | 10 | 0.00686535 | 0.00972605 | 0.00392966 | 0.00530445 |
| C_uniform_all_dephase_p018 | 20 | 5.92131e-05 | 7.73986e-05 | 3.18237e-05 | 4.06743e-05 |
| C_uniform_all_dephase_p018 | 50 | 2.5382e-11 | 3.26759e-11 | 1.45736e-11 | 1.88701e-11 |
| C_uniform_all_dephase_p018 | 100 | 6.90073e-16 | 7.35523e-16 | 3.52623e-16 | 3.74938e-16 |

## Stimulus jump at iteration 50

| condition | mean_trace_distance_stimulus_jump | max_trace_distance_stimulus_jump | mean_delta_coherence_stimulus | max_abs_delta_coherence_stimulus |
|---|---|---|---|---|
| A_baseline_dephase_AD_p018 | 0.000233586 | 0.000312314 | -1.32981e-05 | 0.000340658 |
| B_no_dephase_unitary | 0.0254676 | 0.0257357 | 0.00212417 | 0.0984928 |
| C_uniform_all_dephase_p018 | 4.22116e-13 | 5.26849e-13 | -1.28064e-13 | 5.79758e-13 |

## Stimulus branch vs no-stimulus counterfactual at iteration 100

| condition | mean_trace_distance_100_stim_vs_no | max_trace_distance_100_stim_vs_no | mean_abs_delta_coherence_stim_vs_no | max_abs_delta_coherence_stim_vs_no |
|---|---|---|---|---|
| A_baseline_dephase_AD_p018 | 2.43749e-06 | 3.88285e-06 | 2.03377e-06 | 5.7547e-06 |
| B_no_dephase_unitary | 0.0254676 | 0.0257357 | 0.0360574 | 0.0744404 |
| C_uniform_all_dephase_p018 | 2.01674e-16 | 6.80012e-16 | 9.21485e-17 | 4.44089e-16 |

## Mechanical classification by the predeclared criteria

```text
A_baseline_dephase_AD_p018:
  state pair distance: 0.461998 -> 0.0000786942
  previous-iteration distance: 0.923808 at iter1 -> 0.000211578 at iter100
  coherence variance: 3.80886 -> 4.86756e-09
  stimulated vs no-stim at iter100 mean trace distance: 2.43749e-06
  mechanical status: fixed-attractor candidate under full-state criteria; endpoint is near maximally mixed (purity 0.0625)

B_no_dephase_unitary:
  state pair distance: 0.461998 -> 0.461998
  previous-iteration distance: ~0.929898 through the unitary block, ~0.928666 after stimulus
  coherence variance: 3.80886 -> 0.567752
  stimulated vs no-stim at iter100 mean trace distance: 0.0254676
  mechanical status: not a fixed attractor under full-state criteria

C_uniform_all_dephase_p018:
  state pair distance: 0.461998 -> 2.89561e-16
  previous-iteration distance: 0.869441 at iter1 -> 6.90073e-16 at iter100
  coherence variance: 3.80886 -> 9.47989e-33
  stimulated vs no-stim at iter100 mean trace distance: 2.01674e-16
  mechanical status: fixed-attractor candidate under full-state criteria; endpoint is near maximally mixed (purity 0.0625)
```

No claim of life, consciousness, QPU readiness, or biological adjustment is made.
