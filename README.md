# Quantum Information Matter Lab

A research workspace for building and evolving **contextual information matter**: information-material components whose behavior depends on context, question structure, memory, and composition.

## Core direction

Paper A separated four layers:

```text
1. classical-effective transport / storage / membrane behavior
2. constructed Bell/CHSH feedback
3. observable-class-limited negatives
4. non-routed measurement contextuality
```

The next design hypothesis is:

```text
Do not treat quantum structure as ordinary flow.
Treat measurement/contextual structure as a component interface.
```

The target is a new experimental sandbox where information-material parts can be built, tested, combined, and gradually made more contextual. The point is not to keep the system small and safe forever. The point is to grow it without losing the evidence discipline learned from the audit.

## Initial component roadmap

```text
contextual_membrane:
  passage depends on question/context, not only object type

contextual_converter:
  A -> P/Q conversion depends on the measurement/query context

contextual_memory:
  stores observed outputs and unmeasured alternatives separately

contextual_terrain:
  terrain is written by question history, not only reaction history

contextual_self_register:
  internal state that records how the system reads itself
```

## Repository rules

This repository is for construction, not apology. The discipline is simple:

```text
No code + no raw log = no result.
```

Reports must identify their layer:

```text
CLASSICAL_COMPONENT
CONTEXTUAL_COMPONENT
QUANTUM_AUDIT
PAPER_ANALYSIS
QUARANTINED
```

## Current status

```text
Status: BOOTSTRAP
Valid claims: scaffold migration and starter code only.
Copied from old repo: generic operating discipline and reusable sandbox baseline code.
Excluded: old raw logs, paper-specific result claims, and unverified historical notes.
```

## Quick start

```bash
pip install -r requirements.txt
python scripts/phenomenology/information_microreactor_sandbox.py
python scripts/contextual/contextual_component_skeleton.py --out data/contextual/contextual_component_seed20260708.json
python scripts/check_raw_logs.py
```

## Layout

```text
scripts/
  phenomenology/        classical-effective component baselines
  contextual/           new contextual component experiments
  audit/                witness/control tests only

data/                  raw json/csv/jsonl outputs
results/               human reports and status index
experiments/           protocols before major runs
configs/               fixed experiment configs
docs/                  design notes and migration notes
paper/                 future manuscripts and figure mappings
archive/               old/superseded material
```
