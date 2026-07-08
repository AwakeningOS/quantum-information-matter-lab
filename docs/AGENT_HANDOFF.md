# Agent Handoff

Updated: 2026-07-08

## Repository role

This repository is a clean lab for contextual information-matter components.

The operating rule remains:

```text
No code + no raw log = no result.
```

## Research positioning

The user's intended research direction is not merely to run contextuality as an external witness.

The target line is:

```text
put contextuality into the component decision boundary
```

More precisely, the intended question is:

```text
Does contextuality change a membrane decision?
Does that change depend on memory, unchosen alternatives, context order, joint boundaries, and downstream propagation?
```

Short form:

```text
v0 = context-looking membrane
v1 = memory-bearing boundary
v2 = counterfactual-residue boundary
v3 = order-sensitive boundary
v4 = joint/non-additive boundary
reactor = downstream propagation
quantum anchor = connection to real contextuality witness
```

## Completed experiments

### contextual_membrane_v0

```text
Verdict: PASS_COMPONENT_BEHAVIOR
Layer: CONTEXTUAL_COMPONENT
```

Main lesson:

```text
The membrane decision can depend on context/question structure.
Memory necessity was not established in v0.
```

### contextual_membrane_v1_memory_ablation

```text
Verdict: PASS_MEMORY_DEPENDENT_BOUNDARY
Layer: CONTEXTUAL_COMPONENT
```

Main lesson:

```text
The implemented membrane is not merely context-looking.
Under the tested ablations, dynamic memory changes membrane decisions and downstream quality/release trajectory.
```

### contextual_membrane_v2_counterfactual_residue

```text
Verdict: PASS_COUNTERFACTUAL_RESIDUE
Layer: CONTEXTUAL_COMPONENT
```

Main lesson:

```text
The implemented membrane's later decisions depend on unchosen-alternative residue under the tested ablations.
```

### contextual_membrane_v3_order_effect

```text
Verdict: PASS_ORDER_EFFECT
Layer: CONTEXTUAL_COMPONENT
```

Main lesson:

```text
The same context/object/u event multiset produces different membrane trajectories when order is changed.
Order alone changes event timing, downstream release, final membrane state, and residue distribution in the implemented component.
```

### contextual_membrane_v4_joint_boundary

```text
Verdict: PASS_JOINT_BOUNDARY
Layer: CONTEXTUAL_COMPONENT
```

Main lesson:

```text
The implemented membrane's decisions require full object/context joint state under the tested controls.
Object-only, context-only, additive object+context, static pairwise, and joint-shuffle controls fail to reproduce the full membrane.
```

### contextual_reactor_v0_membrane_to_flow

```text
Verdict: PASS_MEMBRANE_TO_FLOW_PROPAGATION
Layer: CLASSICAL_COMPONENT
```

Main lesson:

```text
The implemented membrane does not only make local PASS/BLOCK decisions.
Its structure propagates into downstream reactor release, quality, reservoir, and persistence under the tested controls.
```

Key reactor comparison:

```text
full_membrane_to_reactor final_persistence = 5.769240129
no_memory_membrane_to_reactor final_persistence = 1.090516857
no_counterfactual_membrane_to_reactor final_persistence = 3.376836905
order_scrambled_membrane_to_reactor final_persistence = 2.944674958
additive_boundary_membrane_to_reactor final_persistence = 0.784523923
reactor_without_membrane final_persistence = 0.894988371

full_membrane_to_reactor final_cumulative_release = 38.849451729
no_memory_membrane_to_reactor final_cumulative_release = 8.940490852
no_counterfactual_membrane_to_reactor final_cumulative_release = 31.869441381
order_scrambled_membrane_to_reactor final_cumulative_release = 30.472556495
additive_boundary_membrane_to_reactor final_cumulative_release = 2.583046640
reactor_without_membrane final_cumulative_release = 10.431454452
```

## Recommended next experiment

Two possible routes:

```text
contextual_reactor_v1_flow_controls
```

or:

```text
contextual_membrane_quantum_anchor_probe
```

Recommendation:

```text
Run contextual_reactor_v1_flow_controls first if the goal is to harden the component propagation claim.
Keep contextual_membrane_quantum_anchor_probe separate and cautious if the goal is to begin connecting to PM/KCBS-like witnesses.
```

## Claim boundary

The current results are contextual/classical component results only.

They do not establish quantum-specific behavior, formal measurement contextuality, life, metabolism, self-repair, consciousness, or physical matter synthesis.
