# Q-Cell Scenario 47 Recurrent Feedback Final Probe v0 Protocol

Date: 2026-07-09
Layer: QUANTUM_OBSERVATION
Status: OBSERVATION_LOG
Experiment: `qcell_scenario47_recurrent_feedback_final_probe_v0`

## Purpose

Repeat scenario 47's same operation sequence on each initial state without reinitialization, then judge convergence using full quantum-state distances rather than coherence alone.

## Conditions

```text
A_baseline_dephase_AD_p018:
  scenario 47 operation with AD dephase p=0.18

B_no_dephase_unitary:
  same operation with dephase removed

C_uniform_all_dephase_p018:
  same operation with all-part uniform dephase p=0.18
```

## Initial states

```text
100 random_product initial states
integer seed IDs: 20260710..20260809
```

## Repetition schedule

```text
100 repeated applications
saved checkpoints: 0, 1, 2, 3, 5, 10, 20, 50, 50_after_stimulus, 100
```

At iteration 50, after recording the checkpoint, apply the same small stimulus to every state:

```text
touch_B strength = 0.10
```

Then continue to iteration 100. Also save a no-stimulus counterfactual branch from iteration 50 to 100.

## Primary numbers

```text
1. pairwise trace distance between all initial-state trajectories
2. trace distance from previous iteration
3. variance of l1 coherence across seeds
```

The primary state distance is trace distance:

```text
0.5 * ||rho_i - rho_j||_1
```

Frobenius distance is saved as a secondary distance.

## Required saved quantities

```text
complete quantum state at checkpoints
l1 coherence
full computational-basis population
all pair ZZ
all pair negativity
purity
entropy
all seed-pair trace/Frobenius distances
previous-iteration trace/Frobenius distances
stimulus jump distances
stimulated vs no-stimulus distance at iteration 100
```

## Non-claims

```text
No QPU claim.
No life/consciousness claim.
No biological adjustment claim.
Do not judge by coherence alone.
```
