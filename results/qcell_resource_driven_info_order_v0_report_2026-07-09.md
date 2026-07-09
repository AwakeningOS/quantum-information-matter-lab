# Qセル資源駆動型・情報秩序維持実験 v0

Status: OBSERVATION_LOG  
Purpose: external-resource driven nonequilibrium information-order observation with thermodynamic ledger.

## Scope actually materialized

This bundle materializes a compact exact-channel ledger grid.

```text
conditions: 569
cyclewise metric rows: 114369
ledger rows: 113800
cycles per condition: 200
full-sweep resources: R1_max_mixed, R2_pure_0, R3_pure_1, R4_plus, R5_gibbs_beta_1
noise conditions: N0 plus N1/N2/N3/N4 over p=0.01,0.03,0.06,0.10,0.18
theta values: [0.05, 0.1, 0.2, 0.4]
```

Density matrices are saved at checkpoint cycles:

```text
0, 1, 2, 5, 10, 20, 50, 100, 150, 199, 200
```

Cyclewise scalar metrics and thermodynamic ledger rows are saved for every included cycle. This is not a claim that every possible condition in the instruction sheet was exhaustively run; it is the materialized v0 observation bundle.

## Converter energy check

```text
[U_converter, H_C + H_R] norm:
theta=0.05 -> 0
theta=0.10 -> 0
theta=0.20 -> 0
theta=0.40 -> 0
```

Maximum absolute energy-balance residual across the materialized ledger:

```text
2.664535e-15
```

Balance used:

```text
Delta E_S + Delta E_R - Q_noise - W_gate
```

## Resource comparison under C7, N4 dephase+amplitude_damping p=0.06, theta=0.20

| resource | condition_id | E_R_in_total | E_R_out_total | F_consumed_nat | coh_49 | coh_99 | coh_149 | collapse_cycles_after_stop | recovery_cycles_after_restart | purity_200 | max_residual |
|---|---|---:|---:|---:|---:|---:|---:|---|---|---:|---:|
| R1_max_mixed | QRIOMC00075 | 75 | 72.6009 | 2.32189 | 0.0947986 | 0.000235442 | 0.0957641 | 5.0 | 6.0 | 0.582183 | 4.996e-16 |
| R2_pure_0 | QRIOMC00159 | 12.5 | 12.1783 | 0.459416 | 0.00175306 | 7.039e-07 | 0.000468 | 4 | not_reached | 0.768703 | 2.498e-16 |
| R3_pure_1 | QRIOMC00243 | 137.5 | 133.021 | 20.1044 | 0.186532 | 0.000471 | 0.189312 | 5.0 | 6.0 | 0.442442 | 3.331e-16 |
| R4_plus | QRIOMC00327 | 75 | 69.7216 | 10.2367 | 1.4071 | 0.0002355 | 1.4281 | 4.0 | 6.0 | 0.492582 | 3.886e-16 |
| R5_gibbs_beta_1 | QRIOMC00411 | 46.1177 | 44.6789 | 0.29393 | 0.0513279 | 0.000110 | 0.051792 | 5.0 | 6.0 | 0.661841 | 2.220e-16 |

## Converter / control comparison under R4_plus, N4 p=0.06, theta=0.20

| variant | resource | condition_id | coh_49 | coh_99 | coh_149 | coh_199 | F_consumed_nat | max_residual |
|---|---|---|---:|---:|---:|---:|---:|---:|
| C7_coupled_Qcell_fresh_schedule | R4_plus | QRIOMC00327 | 1.4071 | 0.0002355 | 1.4281 | 0.780359 | 10.2367 | 3.886e-16 |
| C2_converter_only_maxmixed | R1_max_mixed | QRIOMC00501 | 0.0947986 | 0.0957468 | 0.0957834 | 0.0957845 | 3.07193 | 4.441e-16 |
| C4_reuse_spent_resource | R4_plus | QRIOMC00519 | 0.0700183 | 0.00431628 | 0.000712543 | 0.000153285 | 0.505394 | 2.359e-16 |
| C5_qcell_internal_coupling_off | R4_plus | QRIOMC00540 | 0.255438 | 0.000106557 | 0.254192 | 0.252169 | 9.15147 | 4.441e-16 |
| C6_single_C_only | R4_plus | QRIOMC00561 | 0.255438 | 0.000106557 | 0.254192 | 0.252169 | 9.15147 | 4.441e-16 |

## Theta sweep under R4_plus, N4 p=0.06

| theta | condition_id | coh_49 | coh_99 | coh_149 | F_consumed_nat | purity_200 |
|---:|---|---:|---:|---:|---:|---:|
| 0.05 | QRIOMC00325 | 0.090042 | 0.000019 | 0.091501 | 1.18474 | 0.642319 |
| 0.10 | QRIOMC00326 | 0.356894 | 0.000067 | 0.362861 | 4.12552 | 0.588706 |
| 0.20 | QRIOMC00327 | 1.4071 | 0.0002355 | 1.4281 | 10.2367 | 0.492582 |
| 0.40 | QRIOMC00328 | 5.27968 | 0.001056 | 5.36034 | 13.8592 | 0.341801 |

## Coherence stop/restart numbers

For C7 + R4_plus + N4 p=0.06 + theta=0.20:

```text
coherence at cycle 49  = 1.407101
coherence at cycle 99  = 0.000236
coherence at cycle 149 = 1.428103
collapse after stop to 50% = 4.0 cycles
recovery after restart to 90% = 6.0 cycles
```

## Non-claims

```text
No energy generation claim.
No life claim.
No metabolism claim.
No self-repair claim.
No homeostasis claim.
No quantum advantage claim.
No PASS/FAIL.
No ranking.
```

## Exact wording constraint

The recorded observation is only:

```text
external-resource-dependent nonequilibrium information-order maintenance was observed in selected materialized conditions with a closed numerical energy ledger.
```

Do not convert this into a claim of life, metabolism, self-repair, or general quantum advantage.
