# Q-cell stored-power actuator v0

Date: 2026-07-10 JST

## Scope

QFCBM_0988-only causal trace test for a model-level finite internal store. The store is updated before controller action and `store_before_action` strictly gates dynamic action.

This is not a physical energy reservoir or thermodynamic work claim.

## Run Facts

- seeds: 60
- cycle rows: 60000
- kappa: `0.03`
- store capacity: `1.0`
- supply gain: `0.08`
- max zero-store action violations: `0`
- max action-without-spend violations: `0`
- max insufficient-store action violations: `0`
- max accounting residual: `5.285e-14`

## Readout

- `supply_never_on_initial_zero`: allowed cycles `0.00`, starved `200.00`, mean W_attr `-0.000000`.
- `supply_always_on_initial_zero`: allowed cycles `200.00`, starved `0.00`, mean W_attr `30.348654`.
- `supply_stop_midway_initial_zero`: allowed cycles `101.67`, starved `98.33`, final store `0.003169`, mean W_attr `14.415770`.
- `supply_restart_after_stop_initial_zero`: allowed cycles `158.08`, starved `41.92`, final store `0.960246`, mean W_attr `22.478503`.
- `supply_never_on_initial_positive`: allowed cycles `21.57`, starved `178.43`, final store `0.007305`, mean W_attr `3.042161`.

## Claim Ceiling

Allowed: model-level finite internal store gating of controller action.

Not allowed: metabolism, homeostasis, life, agency, quantum advantage, or real thermodynamic work.
