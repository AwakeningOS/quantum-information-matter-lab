# Where Quantum Structure Survives

**Subtitle:** A Measurement-Boundary Audit of Classical Transport, Constructed Bell Feedback, and Contextuality  
**Author:** Yusuke Maeda  
**Version:** Draft v1.4 - 2026-07-08

> This file is a local reference copy for the next-stage lab. It preserves the design lesson that future agents must read before proposing new contextual information-matter experiments.

## Abstract

This paper asks where quantum-specific structure survives once positive-looking downstream effects are audited against reduced, replay, and witness-routing controls. Across the tested probes, results fell into three audited cases: downstream transport-like outputs were classical-effective in the measured variables, Bell/CHSH feedback positives were constructed by witness routing, and local one-body inverted tests were negative only within that observable class. Non-routed contextuality witnesses remained the surviving boundary: a Peres-Mermin witness exceeded the noncontextual bound for three hardware preparations, and a KCBS embedded-qutrit witness exceeded its bound with $S_{\mathrm{KCBS}}=2.2233$ and statistical $z=25.73$. The result is not a quantum transport advantage; it is a measurement-boundary audit in which quantum structure survived as contextuality, not as ordinary downstream flow.

## Design lesson for this repository

```text
Quantum structure did not survive as ordinary downstream transport.
It survived at the measurement-context boundary.
Therefore, this lab treats contextual structure as a component interface.
```

This means future agents should not assume that adding more flow, storage, membrane filtering, or terrain feedback will automatically make a component quantum-specific. Those structures can be useful, but Paper A showed that the tested downstream variables were classical-effective or replayable unless the quantum witness was explicitly routed into them.

The constructive direction is therefore:

```text
1. keep transport / membrane / reservoir / terrain components useful
2. avoid mistaking CHSH-routed feedback for natural downstream quantum transport
3. treat local one-body negatives as observable-class-limited, not universal no-go results
4. build contextual interfaces where compatibility, incompatibility, question history, and measurement context affect the component state
5. audit any quantum-specific claim separately
```

## Four audit classes

### Class A: classical-effective downstream behavior

Transport, reservoir/storage, membrane/boundary filtering, terrain feedback, and local one-body outputs did not provide affirmative evidence for quantum-specific transport in the tested sandbox. They were reproduced by reduced-state controls, replay controls, or were negative only for the tested observable class.

### Class B: constructed Bell/CHSH feedback

Bell/CHSH-driven downstream positives were real inside the implemented apparatus, but constructed by witness routing. If a term of the form

```text
lambda * max(0, S_CHSH - 2)
```

is explicitly added to a downstream update variable, the downstream positive follows from the definition of the update rule. It is not independent evidence that quantum structure naturally survived as ordinary transport.

### Class C: observable-class-limited negative

The CHSH-free local one-body natural observable probe was negative only for its observable class. It does not rule out future joint-observable tests. This matters for future experiments: a failed local observable does not end the design program; it identifies the wrong readout class.

### Class D: measurement contextuality

The surviving nonclassical layer was measurement contextuality. Peres-Mermin and KCBS witnesses measure contextual correlation directly against noncontextual bounds. These witnesses are not routed into release, terrain, membrane, or transport variables.

## Hardware reference values

### Peres-Mermin witness

IBM backend: `ibm_kingston`  
Job: `d96pilcqp3as739qt2kg`  
Verdict label: `STATE_INDEPENDENT_HARDWARE_VIOLATION` in the operational sense used in Paper A.

```text
xplus: chi = 5.049805, violation = 1.049805, se = 0.028808, z = 36.44
yplus: chi = 4.857422, violation = 0.857422, se = 0.031218, z = 27.47
z0:    chi = 4.644531, violation = 0.644531, se = 0.034165, z = 18.87
```

Context-level caveat: contexts containing `ZZ`, especially `R3=[XY,YX,ZZ]` and `C3=[XX,YY,ZZ]`, were shallower than the other contexts. This is a robustness caveat, not a change to the pre-registered verdict criterion.

### KCBS witness

IBM backend: `ibm_kingston`  
Job: `d96qg82f47jc73a5tm6g`  
Verdict label: `HARDWARE_KCBS_VIOLATION`.

```text
S_KCBS = 2.2232666015625
violation = 0.2232666015625
se = 0.008678203935971344
z = 25.72728218993046
max_unused_11 = 0.003173828125
mean_unused_11 = 0.0024169921875
```

The KCBS implementation embeds a qutrit into a two-qubit subspace. It is a selected three-dimensional subspace implementation, not a native-qutrit platform.

## Key conclusion

```text
In this audit, quantum structure did not survive as ordinary transport.
It survived where quantum theory says it should: in the algebra of compatible and incompatible measurements.
```

## How this should guide future experiments

Future agents should read this before designing new components.

The correct inheritance from Paper A is not:

```text
make a bigger transport sandbox and call it quantum
```

The correct inheritance is:

```text
make contextual components whose behavior depends on question structure,
compatibility, memory, and unobserved alternatives;
then audit which effects are classical-effective, constructed, contextual,
or quantum-specific.
```

## References

Bell, J. S. (1964). On the Einstein Podolsky Rosen paradox. *Physics Physique Fizika*, 1, 195-200. DOI: 10.1103/PhysicsPhysiqueFizika.1.195.

Clauser, J. F., Horne, M. A., Shimony, A., & Holt, R. A. (1969). Proposed experiment to test local hidden-variable theories. *Physical Review Letters*, 23, 880-884. DOI: 10.1103/PhysRevLett.23.880.

Peres, A. (1990). Incompatible results of quantum measurements. *Physics Letters A*, 151, 107-108. DOI: 10.1016/0375-9601(90)90172-K.

Mermin, N. D. (1990). Simple unified form for the major no-hidden-variables theorems. *Physical Review Letters*, 65, 3373-3376. DOI: 10.1103/PhysRevLett.65.3373.

Klyachko, A. A., Can, M. A., Binicioglu, S., & Shumovsky, A. S. (2008). Simple test for hidden variables in spin-1 systems. *Physical Review Letters*, 101, 020403. DOI: 10.1103/PhysRevLett.101.020403.

Howard, M., Wallman, J., Veitch, V., & Emerson, J. (2014). Contextuality supplies the magic for quantum computation. *Nature*, 510, 351-355. DOI: 10.1038/nature13460.

Krishna, A., Spekkens, R. W., & Wolfe, E. (2017). Deriving robust noncontextuality inequalities from algebraic proofs of the Kochen-Specker theorem: the Peres-Mermin square. arXiv:1704.01153.

Javadi-Abhari, A., Treinish, M., Krsulich, K., Wood, C. J., Lishman, J., Gacon, J., Martiel, S., Nation, P. D., Bishop, L. S., Cross, A. W., Johnson, B. R., & Gambetta, J. M. (2024). Quantum computing with Qiskit. arXiv:2405.08810.
