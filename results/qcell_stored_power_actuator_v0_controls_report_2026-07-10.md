# Q-cell stored-power actuator v0 controls

Date: 2026-07-10 JST

## Scope

Anti-bookkeeping controls for the QFCBM_0988 stored-power actuator run.

## Run Facts

- seeds: 60
- cycle rows: 96000
- conditions: 8
- max zero-store action violations: 0
- max action-without-spend violations: 0
- max insufficient-store action violations: 0
- max residual: `5.285e-14`

## Readout

- real restart W_attr: `22.478503`
- supply-label-only restart W_attr: `-0.000000`
- store-shuffle restart W_attr: `25.042975`

## Compact Table

- equal_total_continuous: W_attr 23.729512, allowed 137.65, starved 62.35, spent 6.382800, S_final 0.017200
- equal_total_early: W_attr 14.415770, allowed 101.67, starved 98.33, spent 4.680865, S_final 0.003169
- equal_total_late: W_attr 12.061033, allowed 80.00, starved 120.00, spent 3.526155, S_final 0.961703
- equal_total_pulsed: W_attr 23.281416, allowed 135.43, starved 64.57, spent 6.381369, S_final 0.018631
- no_controller_drain_always: W_attr -0.000000, allowed 0.00, starved 200.00, spent 0.000000, S_final 1.000000
- real_restart: W_attr 22.478503, allowed 158.08, starved 41.92, spent 7.189434, S_final 0.960246
- store_shuffle_restart: W_attr 25.042975, allowed 160.25, starved 39.75, spent 7.525023, S_final 0.956351
- supply_label_only_restart: W_attr -0.000000, allowed 0.00, starved 200.00, spent 0.000000, S_final 0.000000

## Claim Ceiling

These controls test whether the previous result is just a supply label or post-hoc bookkeeping. They do not establish physical energy storage.
