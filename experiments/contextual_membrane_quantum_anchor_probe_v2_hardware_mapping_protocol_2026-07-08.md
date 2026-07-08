# Protocol: contextual_membrane_quantum_anchor_probe_v2_hardware_mapping

Date: 2026-07-08

## Question

Can the explicit witness-table anchor be mapped to existing PM/KCBS hardware-backed result formats without mixing simulated evidence and real QPU evidence?

This follows:

```text
contextual_membrane_quantum_anchor_probe_v1 = explicit witness-table audit candidate
contextual_membrane_quantum_anchor_probe_v2_hardware_mapping = hardware-format compatibility audit
```

## Layer

```text
QUANTUM_AUDIT
```

## Motivation

The v1 anchor audit produced explicit PM/KCBS-shaped probability tables that passed deterministic-bound and no-disturbance checks.

The v2 audit does not claim new quantum evidence. It asks only whether those table-level margins can be aligned with the existing hardware-backed PM/KCBS witness formats.

The core separation is:

```text
simulated table margin != hardware witness result
```

They are compared but not pooled.

## Inputs

### Simulated table audit values from v1

```text
KCBS table S = 2.256568549
KCBS bound = 2
KCBS table violation = 0.256568549

PM table parity accuracy = 0.921974446
PM parity bound = 5/6
PM chi-equivalent = 12 * accuracy - 6 = 5.063693352
PM chi bound = 4
PM chi-equivalent violation = 1.063693352
```

### Existing hardware-backed witness values

```text
KCBS hardware S = 2.2232666015625
KCBS hardware violation = 0.2232666015625
KCBS hardware SE = 0.008678203935971344
KCBS hardware z = 25.727...

PM hardware xplus chi = 5.049805
PM hardware xplus violation = 1.049805
PM hardware xplus SE = 0.028808
PM hardware xplus z = 36.44

PM hardware yplus chi = 4.857422
PM hardware yplus violation = 0.857422
PM hardware yplus SE = 0.031218
PM hardware yplus z = 27.47

PM hardware z0 chi = 4.644531
PM hardware z0 violation = 0.644531
PM hardware z0 SE = 0.034165
PM hardware z0 z = 18.87
```

## Checks

```text
1. Convert v1 PM parity accuracy into PM chi-equivalent convention.
2. Compare simulated KCBS margin with hardware KCBS margin.
3. Compare simulated PM chi-equivalent margin with hardware PM margins.
4. Add finite-shot Gaussian survival estimates using the hardware SE scale.
5. Require margins to have the same sign.
6. Require simulated/hardware margin ratios to remain in a broad compatibility range.
7. Keep all quantum-specific promotion disabled.
```

## Success criteria

```text
kcbs_sim_and_hardware_margins_same_sign
pm_sim_and_all_hardware_margins_same_sign
kcbs_margin_ratio_between_0_5_and_2_0
pm_margin_ratios_between_0_5_and_2_0
kcbs_sim_finite_shot_survival_ge_0_999
kcbs_hardware_finite_shot_survival_ge_0_999
pm_sim_finite_shot_survival_min_ge_0_999
pm_hardware_finite_shot_survival_min_ge_0_999
simulated_and_hardware_evidence_not_pooled
no_quantum_specific_claim_promoted
```

## Run command

```bash
python scripts/contextual/contextual_membrane_quantum_anchor_probe_v2_hardware_mapping.py \
  --seed 20260708 \
  --out data/contextual/contextual_membrane_quantum_anchor_probe_v2_hardware_mapping_seed20260708.json \
  --csv data/contextual/contextual_membrane_quantum_anchor_probe_v2_hardware_mapping_seed20260708_summary.csv
```

## Claim boundary

This experiment can support only a hardware-format compatibility audit claim.

It does not establish a new quantum result, a new hardware result, formal measurement contextuality of the component, biological organization, self-repair, metabolism, consciousness, or physical matter synthesis.
