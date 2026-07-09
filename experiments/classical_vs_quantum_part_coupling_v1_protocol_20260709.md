# Protocol: classical_vs_quantum_part_coupling_v1_measurable_witness

Date: 2026-07-09

Layer: QUANTUM_OBSERVATION -> QUANTUM_AUDIT candidate

Status: PRE-REGISTERED

Generator planned:

```text
scripts/quantum_observation/classical_vs_quantum_part_coupling_v1_measurable_witness.py
```

Raw log planned:

```text
data/quantum_observation/classical_vs_quantum_part_coupling_v1_seed20260709.json
```

Summary CSV planned:

```text
data/quantum_observation/classical_vs_quantum_part_coupling_v1_seed20260709_summary.csv
```

## P0: correction to v0

```text
v0 phase_context_sensitivity injected Rz phase on ALL FOUR qubits M,C,R,W.
Therefore v0 is NOT a clean M-to-W phase-propagation witness: phase could reach W locally without traversing any link.
v1 corrects this by locking phase injection to M only and readout to W only.
This is a self-correction of a v0 weakness, not a new positive-hunting run.
```

## Scope

```text
This experiment separates constructed metrics from measurable witness candidates.
It does NOT claim quantum advantage, biological organization, or matter synthesis.
It is a NumPy ideal density-matrix simulation with shot bootstrap.
No noise model and no QPU submission in v1.
```

## Fixed circuit structure

```text
qubits: M, C, R, W  (membrane, conversion, recycler, waste-outlet)
phase injection point = M only        Rz(phase) on M
local perturbation    = M and/or C    Ry(theta) per mask
readout point         = W only        P1(W) in Z basis; also <Z_R Z_W>
coupling path         = M-C, C-R, R-W entangling evolution (XX + ZZ), arm-dependent
```

Phase MUST NOT be injected on C, R, or W in any arm.

## Arms

```text
classical_if             : rule/threshold controller, no density matrix
classical_coupled        : numeric coupled dynamics, no density matrix
quantum_field_only       : common global drive, NO link-specific XX/ZZ
quantum_no_entangle      : same singles family as direct, link gates REMOVED
quantum_direct_coupled   : M-C / C-R / R-W XX+ZZ links present
quantum_dephased_control : direct coupling with dephase inserted during propagation
```

Keep BOTH field_only and no_entangle:

```text
field_only   = common drive is insufficient
no_entangle  = directional link is required
```

## Dephased arm lock

```text
Use option (b): dephase the link chain during propagation.

Sequence:
  M-only phase injection
  M/C local perturbation
  link evolution layer 1: M-C, C-R, R-W
  Z-dephase all four qubits M,C,R,W
  link evolution layer 2: M-C, C-R, R-W
  Z-dephase all four qubits M,C,R,W
  ...
  readout P1_W and ZZ_RW

Do NOT use only final readout-preceding dephase. That would kill off-diagonals after population conversion and could fail to test propagation coherence.
```

## Witnesses

```text
MAIN:
  phase_sens_P1W = | P1_W(phaseM=pi/2, M perturb) - P1_W(phaseM=0, M perturb) |

SECONDARY:
  output_nonadditivity_P1W =
    | P1_W(M+C) - P1_W(M) - P1_W(C) + P1_W(base) |

DIAGNOSTIC:
  output_nonadditivity_ZZRW =
    | <Z_R Z_W>(M+C) - <Z_R Z_W>(M) - <Z_R Z_W>(C) + <Z_R Z_W>(base) |

RETIRED / AUXILIARY ONLY:
  link_negativity_integral
```

## Why phase_sens_P1W resists the constructed objection

```text
Rz(theta) commutes with Z. A phase on M cannot change any W Z-basis population unless it is routed through a non-commuting path to W.
So phase_sens_P1W > 0 is not guaranteed merely by placing a link-negativity-producing gate.
```

## Pre-registered predictions

```text
P1: quantum_direct_coupled phase_sens_P1W > quantum_field_only by margin
P2: quantum_dephased_control reduces phase_sens_P1W AND output_nonadditivity_P1W by >= 50%
P3: quantum_no_entangle phase_sens_P1W ~= 0
P4: quantum_direct_coupled output_nonadditivity_P1W > {no_entangle, dephased}
P5: classical_if and classical_coupled = 0 on all three quantum witnesses
```

## Keep / discard rule

```text
shots = 4096
bootstrap resamples = 1000
seed = 20260709

KEEP a witness if the bootstrap CI of direct - control excludes 0.
DISCARD a witness if it collapses to noise-floor when moved off negativity.

noise-floor reference:
  single-probability SE at 4096 shots: sqrt(0.25/4096) ~= 0.0078
  difference-of-two SE: sqrt(2) * 0.0078 ~= 0.011
```

Do NOT move any threshold after seeing results. Log the raw counts.

## Explicitly out of scope for v1

```text
no noise model
no QPU submission
no advantage / organization / synthesis claim
```

## Verdict labels

```text
PASS_MEASURABLE_WITNESS_SURVIVES
PARTIAL_WITNESS_SURVIVES
WITNESS_COLLAPSED_ON_REPLACEMENT
```
