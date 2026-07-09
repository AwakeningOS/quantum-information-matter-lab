# Q-cell local linked energy machine full 2^7 final v0 runner note

Status: OBSERVATION_LOG / RUNNER_PREPARED

## Prepared artifact

A full 2^7 local runner package was prepared for local execution.

The runner uses the full 7-qubit density matrix during each cycle:

```text
R,E,A,B,C,D,W
```

The continuing Q-cell body is:

```text
E,A,B,C,D
```

The body is not reset mid-run.

## Local execution command

Smoke:

```bash
python qcell_local_linked_energy_machine_full2q7_final_v0.py \
  --profile smoke \
  --n-seeds 2 \
  --max-conditions 2 \
  --processes 1 \
  --outdir smoke_out
```

Full run on 6-core / 64GB machine:

```bash
python qcell_local_linked_energy_machine_full2q7_final_v0.py \
  --profile final \
  --n-seeds 100 \
  --processes 6 \
  --outdir qcell_local_linked_energy_machine_full2q7_final_v0_outputs
```

## Local package checks

```text
syntax compile: OK
simulation in ChatGPT runtime: not executed to completion because this runtime hit the short execution limit during smoke execution
```

## Resource separation

Main battery resource:

```text
R3 = |1>
energy yes
coherence no
```

Coherence-injecting comparison:

```text
R4 = |+>
energy yes
coherence yes
```

Do not interpret R4-only effects as battery-energy-only behavior.

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
