# Q-cell controller evolution v0

Date: 2026-07-10 JST

## Scope

Small evolutionary/random search over interpretable local internal-controller parameters. This is trial-and-error parameter search, not deep RL and not a claim of agency, purpose, life, homeostasis, optimization in the strong sense, or quantum advantage.

Raw detail rows are stored outside the repository:

```text
/home/youthk/work/qcell_experiment_outputs/qcell_controller_evolution_v0_outputs
```

## Run facts

- grids: QFCBM_0988, QFCBM_0496, QFCBM_0399
- population: 12
- generations: 4
- train seeds: 20
- validation seeds: 20
- holdout seeds: 60
- GPU: NVIDIA GeForce RTX 3090
- wall seconds: 255.965
- switching cost: `not_modeled`

## Best parameters

```json
{
  "gain": 0.8954970900800753,
  "leak": 0.0,
  "downstream_bias": 1.6168544646335714,
  "ad_gate": 1.2724551382033202,
  "d_block": 1.2411067859023053,
  "max_angle_mult": 1.9116732153219738
}
```

## Training top candidates

| candidate_id | score | mean_gain | median_gain | n_positive_gain | n_eval | mean_penalty |
| --- | --- | --- | --- | --- | --- | --- |
| gen2_mut008_from_gen1_mut008_from_hand_coded | 4.607294 | 4.607294 | 0.202137 | 60.000000 | 60.000000 | 0.000000 |
| gen1_mut008_from_hand_coded | 4.544840 | 4.544840 | 0.183278 | 60.000000 | 60.000000 | 0.000000 |
| gen3_mut006_from_gen2_mut005_from_hand_coded | 4.204782 | 4.204782 | 0.134485 | 60.000000 | 60.000000 | 0.000000 |
| gen2_mut005_from_hand_coded | 3.880427 | 3.880427 | 0.187962 | 60.000000 | 60.000000 | 0.000000 |
| hand_coded | 3.333429 | 3.333429 | 0.176998 | 60.000000 | 60.000000 | 0.000000 |

## Validation top candidates

| candidate_id | score | mean_gain | median_gain | n_positive_gain | n_eval | mean_penalty |
| --- | --- | --- | --- | --- | --- | --- |
| gen2_mut008_from_gen1_mut008_from_hand_coded | 4.674135 | 4.674135 | 0.203437 | 60.000000 | 60.000000 | 0.000000 |
| gen1_mut008_from_hand_coded | 4.599517 | 4.599517 | 0.183473 | 60.000000 | 60.000000 | 0.000000 |

## Holdout summary

| candidate_id | score | mean_gain | median_gain | n_positive_gain | n_eval | mean_penalty | max_residual |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gen2_mut008_from_gen1_mut008_from_hand_coded | 4.553862 | 4.553862 | 0.203241 | 180.000000 | 180.000000 | 0.000000 | 8.504e-14 |
| hand_coded | 3.324505 | 3.324505 | 0.177810 | 180.000000 | 180.000000 | 0.000000 | 8.726e-14 |

## Holdout grid breakdown

| candidate_id | grid_id | n_seed | resource_attributable_W_mean | fixed_resource_attributable_W_mean | gain_over_fixed_mean | gain_over_fixed_median | n_positive_gain | no_resource_trick_count | max_budget_excess |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gen2_mut008_from_gen1_mut008_from_hand_coded | QFCBM_0399 | 60.000000 | 0.016027 | 0.007995 | 0.008031 | 0.007806 | 60.000000 | 0.000000 | 0.000000 |
| gen2_mut008_from_gen1_mut008_from_hand_coded | QFCBM_0496 | 60.000000 | 0.259866 | 0.056039 | 0.203827 | 0.203241 | 60.000000 | 0.000000 | 0.000000 |
| gen2_mut008_from_gen1_mut008_from_hand_coded | QFCBM_0988 | 60.000000 | 29.307286 | 15.857558 | 13.449729 | 13.282582 | 60.000000 | 0.000000 | 0.000000 |
| hand_coded | QFCBM_0399 | 60.000000 | 0.017966 | 0.007995 | 0.009971 | 0.009977 | 60.000000 | 0.000000 | 0.000000 |
| hand_coded | QFCBM_0496 | 60.000000 | 0.235333 | 0.056039 | 0.179294 | 0.177810 | 60.000000 | 0.000000 | 0.000000 |
| hand_coded | QFCBM_0988 | 60.000000 | 25.641808 | 15.857558 | 9.784250 | 9.674847 | 60.000000 | 0.000000 | 0.000000 |

## Readout

- The evolved controller beat the hand-coded controller on overall held-out mean gain: `4.553862` vs `3.324505`.
- The evolved controller improved most strongly on `QFCBM_0988`: attributed W `29.307286` vs fixed `15.857558`, gain `13.449729`.
- It also improved `QFCBM_0496`: attributed W `0.259866` vs fixed `0.056039`, gain `0.203827`.
- It did not beat the hand-coded controller on `QFCBM_0399`; evolved gain `0.008031`, hand-coded gain `0.009971`.
- No holdout row used a no-resource subtraction trick, and no budget excess was recorded.

## Current claim ceiling

Allowed:

```text
A small evolutionary search found a parameterized local internal controller that improved held-out mean attributed output over the hand-coded local controller, mainly by improving the high-output ring and strong-output-suppression regions.
```

Not allowed:

```text
global optimum
autonomous agency
purpose
life/metabolism/homeostasis
quantum advantage
efficiency improvement while switching cost is not modeled
```
