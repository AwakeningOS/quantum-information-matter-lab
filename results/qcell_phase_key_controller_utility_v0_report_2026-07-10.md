# Q-cell phase-key controller utility v0

Date: 2026-07-10 JST

## Summary

- classical / angle_key / angle `-1.5`: test accuracy `0.500000`, orientation `no_signal`, test abs margin `0.000000000`, correct/tie `0/30`.
- classical / angle_key / angle `-1.0`: test accuracy `0.500000`, orientation `no_signal`, test abs margin `0.000000000`, correct/tie `0/30`.
- classical / angle_key / angle `1.0`: test accuracy `0.500000`, orientation `no_signal`, test abs margin `0.000000000`, correct/tie `0/30`.
- classical / angle_key / angle `1.5`: test accuracy `0.500000`, orientation `no_signal`, test abs margin `0.000000000`, correct/tie `0/30`.
- classical / phase_shuffled_angle_key / angle `-1.5`: test accuracy `0.500000`, orientation `no_signal`, test abs margin `0.000000000`, correct/tie `0/30`.
- classical / phase_shuffled_angle_key / angle `-1.0`: test accuracy `0.500000`, orientation `no_signal`, test abs margin `0.000000000`, correct/tie `0/30`.
- classical / phase_shuffled_angle_key / angle `1.0`: test accuracy `0.500000`, orientation `no_signal`, test abs margin `0.000000000`, correct/tie `0/30`.
- classical / phase_shuffled_angle_key / angle `1.5`: test accuracy `0.500000`, orientation `no_signal`, test abs margin `0.000000000`, correct/tie `0/30`.
- full_dephase / angle_key / angle `-1.5`: test accuracy `0.500000`, orientation `no_signal`, test abs margin `0.000000000`, correct/tie `0/30`.
- full_dephase / angle_key / angle `-1.0`: test accuracy `0.500000`, orientation `no_signal`, test abs margin `0.000000000`, correct/tie `0/30`.
- full_dephase / angle_key / angle `1.0`: test accuracy `0.500000`, orientation `no_signal`, test abs margin `0.000000000`, correct/tie `0/30`.
- full_dephase / angle_key / angle `1.5`: test accuracy `0.500000`, orientation `no_signal`, test abs margin `0.000000000`, correct/tie `0/30`.
- full_dephase / phase_shuffled_angle_key / angle `-1.5`: test accuracy `0.500000`, orientation `no_signal`, test abs margin `0.000000000`, correct/tie `0/30`.
- full_dephase / phase_shuffled_angle_key / angle `-1.0`: test accuracy `0.500000`, orientation `no_signal`, test abs margin `0.000000000`, correct/tie `0/30`.
- full_dephase / phase_shuffled_angle_key / angle `1.0`: test accuracy `0.500000`, orientation `no_signal`, test abs margin `0.000000000`, correct/tie `0/30`.
- full_dephase / phase_shuffled_angle_key / angle `1.5`: test accuracy `0.500000`, orientation `no_signal`, test abs margin `0.000000000`, correct/tie `0/30`.
- quantum / angle_key / angle `-1.5`: test accuracy `1.000000`, orientation `minus_gt_plus`, test abs margin `0.000000020`, correct/tie `30/0`.
- quantum / angle_key / angle `-1.0`: test accuracy `1.000000`, orientation `minus_gt_plus`, test abs margin `0.000000043`, correct/tie `30/0`.
- quantum / angle_key / angle `1.0`: test accuracy `1.000000`, orientation `minus_gt_plus`, test abs margin `0.000000043`, correct/tie `30/0`.
- quantum / angle_key / angle `1.5`: test accuracy `1.000000`, orientation `minus_gt_plus`, test abs margin `0.000000020`, correct/tie `30/0`.
- quantum / phase_shuffled_angle_key / angle `-1.5`: test accuracy `0.466667`, orientation `plus_gt_minus`, test abs margin `0.000000020`, correct/tie `14/0`.
- quantum / phase_shuffled_angle_key / angle `-1.0`: test accuracy `0.633333`, orientation `plus_gt_minus`, test abs margin `0.000000031`, correct/tie `19/0`.
- quantum / phase_shuffled_angle_key / angle `1.0`: test accuracy `0.533333`, orientation `plus_gt_minus`, test abs margin `0.000000029`, correct/tie `16/0`.
- quantum / phase_shuffled_angle_key / angle `1.5`: test accuracy `0.600000`, orientation `plus_gt_minus`, test abs margin `0.000000023`, correct/tie `18/0`.

## Interpretation

Using the first 30 seeds to learn the residual orientation and the last 30 seeds
for evaluation, the quantum angle-key residual works as a tiny downstream branch
signal:

```text
quantum angle_key test accuracy = 1.0
classical/full_dephase = 0.5 no signal
phase-shuffled quantum = near random
```

The useful margin remains extremely small (`2e-8` to `4e-8`). The allowed claim
is therefore only small model-level downstream utility, not robust macroscopic
control, quantum advantage, or physical memory.

## Claim Ceiling

model-level downstream branch utility from delayed phase-key residuals; no quantum advantage claim
