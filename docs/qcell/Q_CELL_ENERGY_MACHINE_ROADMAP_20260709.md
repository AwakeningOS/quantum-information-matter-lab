# Q-Cell Energy-Machine Research Roadmap

Last evidence refresh: 2026-07-09 JST

## Human question

Can locally quantum-coupled parts receive an external resource, retain and
transport usable energy/information order, produce an output, and eventually
improve whole-system performance using only local state?

This roadmap does not assume life, purpose, metabolism, self-repair,
homeostasis, autonomous optimization, or quantum advantage.

## What has been learned

### 1. Scenario 47: apparent attraction was information loss

Repeated scenario-47 operations with dephasing made initially different
states converge. The endpoint purity approached:

```text
1 / 16 = 0.0625
```

for the four-qubit system, which is the maximally mixed value. With no
dephasing, trace distance between initial states did not contract. The
observed recurrence was therefore modeled information erasure, not evidence
of emergent regulation.

### 2. Passive noise-tolerance component: specific calibration only

The encoding

```text
|0L> = |01>
|1L> = |10>
```

preserved logical coherence under the specifically matched collective
dephasing channel and failed under independent dephasing. This is a
decoherence-free-subspace calibration, not general Q-cell noise resistance
and not a new phenomenon.

### 3. Resource-driven information order

Fresh external resource states maintained non-equilibrium information order
while supplied; stopping supply reduced the maintained quantities and
restarting supply restored them. The strongest `|+>` behavior included
direct coherence injection, so it cannot be interpreted as energy-only
conversion. This motivated separating `R3=|1>` from `R4=|+>`.

### 4. Single-excitation local energy machine

The reduced hard-core model showed energy-only `R3=|1>` resource reaching
internal parts and `W` under fixed local coupling. The reduction allowed at
most one excitation, so it was not sufficient to establish full battery,
saturation, or multi-excitation behavior.

### 5. Full 2^7 local energy machine

The full model used `R,E,A,B,C,D,W` during every cycle and retained
`E,A,B,C,D` without resetting the body.

Verified run:

```text
37 conditions
100 initial states
200 cycles
743,700 state-metric rows
740,000 thermodynamic-ledger rows
maximum absolute energy-balance residual = 1.154632e-13
```

Main `R3=|1>`, ring, `p=0.06`, `g=0.10`, `theta=0.20`:

```text
net resource transfer = 4.866583
cumulative W output = 0.458287
modeled noise loss = 6.681873
```

Structure/output comparison:

```text
matched central-control comparison = 1.027726
ring baseline = 0.458287
classical probability transport = 0.388945
chain baseline = 0.361389
middle cut = 0.244341
```

This verifies resource-dependent local transport in the full model. It does
not show that parts know a global objective or adapt their behavior.

### 6. Fixed-circuit output bottleneck map

`qcell_fixed_circuit_output_bottleneck_map_v0`

Purpose:

> Establish the fixed-circuit output envelope before adding local adaptive
> control.

The corrected design runs 1,000 grid points with matched:

```text
local_resource
local_no_resource
central_resource
central_no_resource
```

Primary attributed output:

```text
resource_attributable_W
= W(local_resource) - W(local_no_resource)
```

Raw multi-gigabyte logs remain local. Only compact validated summaries,
manifests, protocols, code, and final reports should be committed.

Stage 1 completed the full 1,000-grid map with 10 initial states. Stage 2
confirmed 28 representative regions with 100 initial states.

Stage 2 verified facts:

```text
selected grids = 28
initial states per grid = 100
variants per grid = 4
cycles = 200
maximum absolute energy-balance residual = 1.394440e-13
max [U_DW, H_D+H_W] norm = 0
output switching cost = not_modeled
```

Stage 2 high-output region:

```text
QFCBM_0488 / QFCBM_0497
structure = chain
g_internal = 0.4
theta_in_RE = 0.8
effective outlet angle = 0.8
resource_attributable_W_mean = 17.632414
matched central = 38.374395
fixed/central ratio = 0.459473
efficiency_resource_to_W = 0.521259
```

Stage 2 high-efficiency region:

```text
QFCBM_0408
structure = chain
g_internal = 0.4
theta_in_RE = 0.05
effective outlet angle = 0.8
resource_attributable_W_mean = 0.234025
efficiency_resource_to_W = 0.560834
```

The high-output and high-efficiency regions are not the same. Strong output
coupling still shows overswap/suppression: in the high-input chain family,
attributed W drops from `17.632414` at effective outlet `0.8` to `0.055903`
at effective outlet `3.2`.

This closes the fixed-circuit envelope baseline before local adaptive control.

## Next experiment order

### Step 1 — Fixed-circuit map

Done for Stage 1 and Stage 2 in compact committed form. Raw logs remain local
and should not be committed.

### 7. Local coordination causal test

Active planning artifact:

```text
experiments/qcell_local_controller_causal_test_v0_protocol_20260710.md
docs/qcell/Q_CELL_LOCAL_CONTROLLER_CLOUD_REVIEW_PROMPT_20260710.md
data/quantum_observation/qcell_local_controller_causal_test_v0_pilot_grid_ids.txt
```

Division of work:

```text
Cloud GPT:
  review local-controller policy family
  review shuffled-signal and time-shuffled-action controls
  identify failure modes and stop/go rules from compact Stage 2 facts

Local Codex/GPU:
  reuse the existing full 2^7 GPU engine
  implement the pilot runner
  run only 5 grids x 20 seeds first
  store raw logs under /home/youthk/work/qcell_experiment_outputs/
  commit only compact summaries, manifest, protocol, and report
```

Compare under matched resources, noise, time, and switching-work accounting:

```text
fixed circuit
local-state controller
shuffled local signals
time-shuffled controller actions
matched central controller
classical local controller
```

Use unseen faults and outlet relocation. For every component action, compute
the counterfactual output when that action is removed.

Claim ceiling:

> Local state-dependent actions causally improved whole-system output.

Do not call this purpose, understanding, or autonomous optimization.

Verified v0 result:

```text
pilot:
  6 grids
  20 seeds
  fixed/internal/output/shuffled/time-shift/central paired variants

confirmation:
  3 grids
  100 seeds
  internal-only controller with fixed/shuffled/time-shift/central pairs

max residual:
  <= 7.33e-14
```

100-seed confirmation:

```text
QFCBM_0988:
  fixed attributed W = 15.840497
  internal controller attributed W = 26.024037
  gain over fixed = 10.183540
  gain over shuffled signal = 14.554753
  gain over time-shift action = 2.575167
  positive over all controls = 100/100 seeds

QFCBM_0496:
  fixed attributed W = 0.055903
  internal controller attributed W = 0.258512
  gain over fixed = 0.202609
  gain over shuffled signal = 0.215405
  gain over time-shift action = 0.037659
  positive over all controls = 100/100 seeds

QFCBM_0399:
  fixed attributed W = 0.007974
  internal controller attributed W = 0.017535
  gain over fixed = 0.009561
  gain over shuffled signal = 0.016375
  gain over time-shift action = 0.000527
  positive over time-shift = 64/100 seeds
```

Readout:

```text
The local-gradient internal controller produced selected-region causal gains
over fixed circuits. Two regions survived shuffled-signal and time-shift
controls cleanly. One internal-transport region remained marginal and timing
sensitive.
```

Claim ceiling remains:

```text
local state-dependent controller improved attributed output in selected regions
```

Do not promote:

```text
optimization
purpose
agency
homeostasis
quantum advantage
efficiency improvement after controller switching work
```

### 8. Controller evolution v0

The next step tested whether trial-and-error parameter search could improve the
hand-coded local controller.

Protocol:

```text
experiments/qcell_controller_evolution_v0_protocol_20260710.md
```

Run shape:

```text
grids = QFCBM_0988, QFCBM_0496, QFCBM_0399
population = 12
generations = 4
train seeds = 20
validation seeds = 20
holdout seeds = 60
switching cost = not_modeled
```

Best evolved parameters:

```text
gain = 0.895497
leak = 0.0
downstream_bias = 1.616854
ad_gate = 1.272455
d_block = 1.241107
max_angle_mult = 1.911673
```

Holdout comparison:

```text
best evolved mean gain over fixed = 4.553862
hand-coded mean gain over fixed = 3.324505
```

Grid breakdown:

```text
QFCBM_0988:
  evolved attributed W = 29.307286
  fixed attributed W = 15.857558
  evolved gain = 13.449729
  hand-coded gain = 9.784250

QFCBM_0496:
  evolved attributed W = 0.259866
  fixed attributed W = 0.056039
  evolved gain = 0.203827
  hand-coded gain = 0.179294

QFCBM_0399:
  evolved attributed W = 0.016027
  fixed attributed W = 0.007995
  evolved gain = 0.008031
  hand-coded gain = 0.009971
```

Readout:

```text
Trial-and-error improved the controller overall, mainly by improving the
high-output ring and strong-output-suppression regions. It did not improve the
marginal internal-transport region over the hand-coded controller.
```

Claim ceiling:

```text
small evolutionary search improved a parameterized local controller on
held-out seeds
```

Still not allowed:

```text
global optimum
autonomous agency
purpose
life/metabolism/homeostasis
quantum advantage
efficiency improvement while switching cost is not modeled
```

### 9. Controller cost accounting v0

Before building a physical actuator, a conservative post-hoc cost accounting
was applied to the controller-evolution holdout rows.

Cost model:

```text
net_gain_after_cost =
  gain_over_fixed - cost_per_angle * angle_budget
```

This charges the controller for all controlled internal angle budget and does
not subtract any equivalent fixed-circuit operation cost. It is conservative,
but not a physical switching-work model.

Break-even results:

```text
QFCBM_0988 evolved:
  mean gain before cost = 13.449729
  mean angle budget = 302.139762
  min break-even cost_per_angle = 0.042163
  all-seed positive through swept cost_per_angle = 0.03

QFCBM_0496 evolved:
  mean gain before cost = 0.203827
  mean angle budget = 290.232737
  min break-even cost_per_angle = 0.000673
  all-seed positive through swept cost_per_angle = 0.0003

QFCBM_0399 evolved:
  mean gain before cost = 0.008031
  mean angle budget = 152.298233
  min break-even cost_per_angle = 0.000039
  all-seed positive through swept cost_per_angle = 0.00003
```

Readout:

```text
QFCBM_0988 has enough margin to survive nonzero hypothetical controller cost.
QFCBM_0496 survives small cost.
QFCBM_0399 is fragile.
```

Next step if pursuing physicality:

```text
replace post-hoc cost with an explicit actuator/battery model
```

### 10. Battery-powered controller v0

The next experiment replaced post-hoc controller-cost subtraction with an
explicit finite controller reservoir `M`.

Protocol:

```text
experiments/qcell_battery_powered_controller_v0_protocol_20260710.md
```

Run shape:

```text
grids = QFCBM_0988, QFCBM_0496, QFCBM_0399
seeds = 60
kappa = 0, 0.00003, 0.0001, 0.0003, 0.001, 0.003, 0.01, 0.03
M_initial = unlimited, 20, 5, 1, 0.2, 0
controllers = fixed, evolved, hand_coded, shuffled signal, time shift,
              random budget
```

Validation facts:

```text
seed rows = 43,380
max residual = 8.73e-14
zero-battery dynamic angle max = 0
starved-cycle emitted action max = 0
```

Readout:

```text
QFCBM_0988:
  robust finite-reservoir result
  at kappa = 0.03 and M = 1.0:
    mean attributed W = 3.10877
    positive seeds = 60/60
  at kappa = 0.03 and M = 5.0:
    mean attributed W = 14.7233
    positive seeds = 60/60

QFCBM_0496:
  finite-reservoir effect survives selected settings, but with smaller margin
  at kappa = 0.03 and M = 1.0:
    mean attributed W = 0.02761
    positive seeds = 60/60

QFCBM_0399:
  remains fragile
  kappa = 0.03 and M = 0.2 is not mean-positive
  kappa = 0.03 and M = 1.0 remains small but positive
```

Claim ceiling:

```text
finite controller-reservoir accounting supports that the QFCBM_0988 evolved
controller gain is not a free-action artifact
```

Still not allowed:

```text
complete thermodynamic actuator
signal acquisition or computation cost closure
metabolism/homeostasis/life/agency
quantum advantage
```

### Step 3 — Stored-power actuator

Executed minimum-run artifacts:

```text
experiments/qcell_stored_power_actuator_v0_protocol_20260710.md
docs/qcell/Q_CELL_STORED_POWER_ACTUATOR_CLOUD_REVIEW_PROMPT_20260710.md
docs/qcell/Q_CELL_STORED_POWER_ACTUATOR_CLOUD_REVIEW_RESPONSE_20260710.md
scripts/quantum_observation/qcell_stored_power_actuator_v0_gpu.py
scripts/quantum_observation/qcell_stored_power_actuator_v0_postprocess.py
results/qcell_stored_power_actuator_v0_report_2026-07-10.md
```

Target:

```text
external supply -> internal store -> controller action -> store decreases
store empty -> action stops
supply resumes -> store refills -> action resumes
```

The first GPU run was kept small: `QFCBM_0988` only, 60 seeds, 5 supply/store
conditions.

Cloud review sharpened the requirement:

```text
store_before_action must causally gate controller_action_allowed
```

The minimum run logged the cyclewise store trace before and after action. It
found zero zero-store action violations, zero action-without-spend violations,
zero insufficient-store action violations, and max accounting residual
`5.285e-14`.

Readout:

```text
supply_never_on_initial_zero: allowed cycles 0.00, W_attr ~ 0
supply_always_on_initial_zero: allowed cycles 200.00, W_attr 30.348654
supply_stop_midway_initial_zero: allowed 101.67, starved 98.33, W_attr 14.415770
supply_restart_after_stop_initial_zero: allowed 158.08, starved 41.92, W_attr 22.478503
supply_never_on_initial_positive: allowed 21.57, starved 178.43, W_attr 3.042161
```

This supports only a model-level finite internal store gating claim. The
store-shuffle, supply-label-only, equal-total-supply timing, no-controller-drain,
and fixed-controller controls remain required before promoting a broader
stored-power claim.

First anti-bookkeeping controls:

```text
scripts/quantum_observation/qcell_stored_power_actuator_v0_controls_gpu.py
results/qcell_stored_power_actuator_v0_controls_report_2026-07-10.md
```

Readout:

```text
real restart W_attr = 22.478503
supply-label-only restart W_attr ~ 0
no-controller-drain W_attr ~ 0
equal-total early W_attr = 14.415770
equal-total late W_attr = 12.061025
equal-total pulsed W_attr = 23.281421
equal-total continuous W_attr = 23.729508
store-shuffle restart W_attr = 25.042978
```

Interpretation:

```text
supply label alone is not enough
store fill alone without action is not enough
timing/history changes output
store-shuffle is not yet defeated
```

The store-shuffle result is the current weak point. A stronger trajectory-matched
shuffle control is required before claiming that correct store timing is
necessary.

Strict trajectory-matched shuffle:

```text
scripts/quantum_observation/qcell_stored_power_actuator_v0_strict_shuffle_gpu.py
results/qcell_stored_power_actuator_v0_strict_shuffle_report_2026-07-10.md
```

Readout:

```text
real restart W_attr = 22.478503
reverse shuffled store W_attr = 20.989177
roll-73 shuffled store W_attr = 21.436209
block-swap shuffled store W_attr = 20.683934
```

Interpretation:

```text
trajectory-matched store shuffling does not collapse the effect
exact store timing is only a modest effect in this setup
the current claim must stay at finite store gating of action
do not claim time-specific stored-power dynamics yet
```

Delayed-use test:

```text
scripts/quantum_observation/qcell_stored_power_delayed_use_v0_gpu.py
results/qcell_stored_power_delayed_use_v0_report_2026-07-10.md
```

Readout:

```text
no supply late action W_attr ~ 0
early supply, action only after cycle 120: W_attr = 4.196372
initial store, action only after cycle 120: W_attr = 4.195732
late supply, action only after cycle 120: W_attr = 12.061033
continuous supply, action only after cycle 120: W_attr = 12.030517
```

Interpretation:

```text
stored budget can be held while action is blocked, then spent later
early stored supply behaves like initial stored budget
late/continuous supply is stronger in this setup
```

### Step 3b — Battery-powered actuator

Require stored energy in `E` to decrease when an output action occurs.
Separate:

```text
energy-only |1> resource
coherence-injecting |+> resource
mixed/thermal controls
```

Include switching work. Demonstrate supply, storage, action, depletion,
stopping, and restarting without free control energy.

### Step 4 — Fair quantum/classical comparison

Hold constant:

```text
resource input
topology
noise
wall-clock interaction time
controller information
controller work
output definition
```

Compare coherent quantum, dephased matched, classical stochastic, and central
upper-bound models. No quantum-advantage claim before this comparison.

First current-Q-cell comparison:

```text
experiments/qcell_classical_vs_quantum_coupling_v0_protocol_20260710.md
scripts/quantum_observation/qcell_classical_vs_quantum_coupling_v0_gpu.py
results/qcell_classical_vs_quantum_coupling_v0_report_2026-07-10.md
```

Readout on `QFCBM_0988`:

```text
quantum_direct:
  W_attr = 15.857558
  mean link negativity = 0.001741
  mean coherence = 1.669012

quantum_no_internal_links:
  W_attr ~ 0

quantum_post_internal_dephased:
  W_attr = 7.810684
  link negativity = 0
  coherence = 0

quantum_dephase_after_each_link:
  W_attr = 8.309966
  link negativity = 0
  coherence = 0

classical_probability_transport:
  W_attr = 25.919585
  link negativity = 0
  coherence = 0

central_upper_quantum:
  W_attr = 38.424002
```

Interpretation:

```text
the linkage types differ
quantum direct preserves quantum-link signatures
classical probability transport gives larger W in this setting
dephased quantum arms keep some W without quantum-link signatures
central upper is a positive control, not a fair competitor
this is not quantum advantage
```

### Step 4b — Quantum-structure maintenance cost

Draft artifacts:

```text
experiments/qcell_quantum_structure_maintenance_cost_v0_protocol_20260710.md
scripts/quantum_observation/qcell_quantum_structure_maintenance_cost_v0_gpu.py
experiments/qcell_repair_actuator_audit_v0_protocol_20260710.md
```

Status:

```text
prototype only
full run intentionally halted after smoke
no result claim
```

Reason:

```text
the prototype repair actuator used a nonunitary blend toward the pre-noise state
the blend changed internal energy
therefore W loss cannot cleanly be called structure-maintenance cost
```

Next:

```text
run repair actuator audit first
require energy_delta ~ 0
require diagonal population change ~ 0
charge explicit store cost separately
then rerun structure-maintenance-cost experiment
```

Repair actuator audit v0:

```text
scripts/quantum_observation/qcell_repair_actuator_audit_v0_gpu.py
results/qcell_repair_actuator_audit_v0_report_2026-07-10.md
```

Readout:

```text
population_fixed_offdiag_restore pass_rate = 0.933333
phase_only_alignment pass_rate = 0.967083
diagonal_phase_unitary_alignment pass_rate = 0.130417
```

Interpretation:

```text
no candidate fully passed
population/phase restore candidates can violate positivity
diagonal unitary is clean but does not reliably improve structure
structure-maintenance-cost full run remains blocked
```

Resource partition counterfactual:

```text
scripts/quantum_observation/qcell_resource_partition_counterfactual_v0_gpu.py
results/qcell_resource_partition_counterfactual_v0_report_2026-07-10.md
```

Readout:

```text
same-population W_loss_to_structure = 0 for all arms
quantum_keep_structure W_attr = 15.857558
dephase_25 W_attr = 12.383500
dephase_50 W_attr = 9.765229
dephase_75 W_attr = 8.282828
full_dephase W_attr = 7.810684
classical_same_graph_transport W_attr = 25.919585
```

Interpretation:

```text
the proposed "quantum structure consumes W at fixed population" hypothesis was not supported
deleting structure at the same population did not increase W
dephasing reduced W instead of increasing it
classical transport's higher W is likely a population-routing effect, not a structure-discard effect
```

### Step 5 — Selected hardware observations

Do not send the full map to a QPU. Select a small preregistered subset after
simulation, use measurable observables rather than full tomography where
possible, and record device noise and shot uncertainty.

## Stop conditions

Pause interpretation if any of the following occurs:

```text
trace drift
negative density-matrix eigenvalues beyond tolerance
NaN/Inf
energy-balance residual beyond preregistered tolerance
resource/no-resource pairing mismatch
unaccounted control work presented as generated energy
```
