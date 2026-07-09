# Q-cell battery-powered controller v0

Date: 2026-07-10 JST

## Scope

Finite actuator-budget test for the evolved local controller. This replaces post-hoc cost subtraction with an explicit monotone-depleting controller reservoir `M` during the simulation.

This is not a physical thermodynamic actuator model. Signal acquisition, controller computation, and coupling-switching costs remain unmodeled.

## Run Facts

- grids: QFCBM_0988, QFCBM_0496, QFCBM_0399
- seeds per grid: 60
- rows: 43380
- wall seconds: 1775.885
- maximum energy-balance residual: `8.726e-14`
- zero-battery dynamic angle maximum: `0.000000`
- starved-cycle emitted-action maximum: `0.000000`

## Readout

- `QFCBM_0988` is the robust result. The evolved controller remains positive under finite controller reservoirs; at `kappa=0.03`, `M=1.0` gives mean W_attr `3.108766`, spent `1.000000`, positive `60/60` and `M=5.0` gives mean W_attr `14.723283`, spent `5.000000`, positive `60/60`.
- `QFCBM_0496` is weaker but still survives finite reservoirs in selected settings; at `kappa=0.03`, `M=1.0` gives mean W_attr `0.027613`, spent `1.000000`, positive `60/60`.
- `QFCBM_0399` remains fragile; at `kappa=0.03`, `M=0.2` is not mean-positive, while `M=1.0` gives mean W_attr `0.002277`, spent `1.000000`, positive `60/60`.
- `M=0` correctly shuts off dynamic controller action. This supports that the result is not a free-action artifact.

## Claim Ceiling

Allowed:

```text
Under an explicit finite controller-reservoir accounting model, the evolved local controller remains resource-attributable-output positive in selected regions, especially QFCBM_0988.
```

Not allowed:

```text
real thermodynamic work
complete actuator physics
metabolism/homeostasis/life/agency
quantum advantage
```
