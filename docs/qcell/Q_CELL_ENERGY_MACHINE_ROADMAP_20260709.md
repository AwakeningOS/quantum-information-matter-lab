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

## Active experiment

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

## Next experiment order

### Step 1 — Finish and validate the fixed-circuit map

Required:

```text
1,000/1,000 complete markers
no NaN/Inf
closed energy ledger
commutator check
paired resource/no-resource attribution
matched central comparison
```

Then extract representative regions rather than one universal winner.

### Step 2 — Stage 2 confirmation

Rerun representative regions with 100 initial states:

```text
high attributed output
high resource-to-W efficiency
central-control-nearest
outlet narrow
internal transport slow
ring circulation
strong-output overswap/suppression
chain-best
ring-best
```

Commit compact Stage 1/2 summaries and a result report, not raw cycle logs.

### Step 3 — Local coordination causal test

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

### Step 4 — Battery-powered actuator

Require stored energy in `E` to decrease when an output action occurs.
Separate:

```text
energy-only |1> resource
coherence-injecting |+> resource
mixed/thermal controls
```

Include switching work. Demonstrate supply, storage, action, depletion,
stopping, and restarting without free control energy.

### Step 5 — Fair quantum/classical comparison

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

### Step 6 — Selected hardware observations

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
