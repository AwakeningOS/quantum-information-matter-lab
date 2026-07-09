# Qセル・局所連動型エネルギー機械 観察実験 v0

Status: OBSERVATION_LOG

## Important limitation

This materialized v0 uses a single-excitation hard-core internal basis:

```text
[vac,E,A,B,C,D]
```

It is not a full 2^7 Hilbert-space run. It keeps 100 initial states and 200 cycles, and saves complete density matrices at checkpoints in the truncated basis.

The full 5-qubit density implementation was attempted first but was too slow in this environment. This v0 is therefore a fixed reduced observation grid, not a final exhaustive run.

## Run scale

```text
conditions: 36
initial states per condition: 100
cycles: 200
cyclewise metric rows: 7236
ledger rows: 7200
checkpoint density arrays: 266
max energy balance residual: 2.210e-05
```

## Battery resource separation

R3_pure_1 is the coherence-free excited resource and is the main battery condition.

R4_plus is recorded separately as a coherence-injecting resource. A strong R4_plus effect is not described as battery-energy-only behavior.

## Ring, N4 p=0.06, g=0.10, theta=0.20

| resource | coh@49 | coh@99 | coh@149 | Wout@49 | Wout@149 | Eint@49 | Eint@149 | collapse | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R3_pure_1 | 0.340633 | 0.373405 | 0.514721 | 0.001085 | 0.001427 | 0.372824 | 0.532969 | 11.0 | 13.0 |
| R1_max_mixed | 0.184488 | 0.192047 | 0.276843 | 0.000636 | 0.000771 | 0.208600 | 0.298265 | 11.0 | 15.0 |
| R5_gibbs_beta_1 | 0.105934 | 0.104674 | 0.154194 | 0.000411 | 0.000430 | 0.123690 | 0.169144 | 11.0 | 16.0 |
| R5_gibbs_beta_0.5 | 0.143374 | 0.146027 | 0.212918 | 0.000518 | 0.000593 | 0.164344 | 0.231600 | 11.0 | 15.0 |
| R5_gibbs_beta_2 | 0.052779 | 0.046808 | 0.069934 | 0.000260 | 0.000195 | 0.065405 | 0.077609 | 11.0 | 53.0 |
| R4_plus | 1.039335 | 1.104263 | 0.774739 | 0.001556 | 0.001776 | 0.510888 | 0.592585 | 11.0 | 6.0 |

## Chain vs ring under R3_pure_1

| structure | coh@49 | coh@99 | coh@149 | Wout@49 | Wout@149 | Eint@149 |
|---|---:|---:|---:|---:|---:|---:|
| chain | 0.281943 | 0.301086 | 0.421208 | 0.000673 | 0.000780 | 0.537376 |
| ring | 0.340633 | 0.373405 | 0.514721 | 0.001085 | 0.001427 | 0.532969 |
| middle_cut | 0.187011 | 0.209653 | 0.276975 | 0.000111 | 0.000000035 | 0.542484 |
| shuffled | 0.278605 | 0.297598 | 0.416850 | 0.000860 | 0.001103 | 0.535370 |

## Required controls under R3_pure_1, N4 p=0.06

| variant | coh@49 | coh@99 | coh@149 | Wout@49 | Wout@149 | recovery |
|---|---:|---:|---:|---:|---:|---:|
| ring | 0.340633 | 0.373405 | 0.514721 | 0.001085 | 0.001427 | 13.0 |
| coupling_off | 0.005555 | 0.000030 | 0.000000063 | 0.000046 | 0.000000002 | not reached |
| converter_off | 0.017728 | 0.000237 | 0.000005 | 0.000161 | 0.000000184 | not reached |
| output_off | 0.275851 | 0.299468 | 0.416087 | 0 | 0 | 14.0 |
| central_control | 0.259260 | 0.275331 | 0.389609 | 0.003800 | 0.005606 | 7.0 |
| strong_dephase | 0 | 0 | 0 | 0.000203 | 0.000175 | not reached |

## Fault response at cycle 100, R3_pure_1 ring

| fault | coh@149 | Wout@149 | Eint@149 |
|---|---:|---:|---:|
| remove_A_excitation | 0.514769 | 0.001423 | 0.532908 |
| overexcite_C | 0.509805 | 0.001460 | 0.533765 |
| cut_BC | 0.492211 | 0.001653 | 0.531418 |
| weaken_AB | 0.384761 | 0.002323 | 0.527281 |
| close_DW | 0.513870 | 0.001432 | 0.533049 |
| empty_E | 0.516625 | 0.001417 | 0.532683 |

## p/g/noise sweep snippets for R3_pure_1 ring

| condition | coh@49 | coh@149 | Wout@149 | recovery |
|---|---:|---:|---:|---:|
| g=0.05 | 0.239724 | 0.354895 | 0.000501 | 22.0 |
| g=0.20 | 0.313545 | 0.450489 | 0.002214 | 7.0 |
| p=0.01 | 0.881464 | 0.852470 | 0.002873 | 16.0 |
| p=0.18 | 0.061454 | 0.105228 | 0.000166 | 11.0 |
| N0 none | 2.156800 | 1.578433 | 0.002719 | 0.0 |
| N1 dephase | 0.281532 | 0.301020 | 0.005248 | 14.0 |
| N3 amplitude_damping | 0.689648 | 0.940172 | 0.001022 | 14.0 |

## Non-claims

```text
No purpose.
No decision-making.
No life.
No metabolism.
No self-repair.
No homeostasis.
No optimization claim.
No quantum advantage claim.
No PASS/FAIL.
No ranking.
```
