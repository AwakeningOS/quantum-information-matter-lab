# Migration Note

Source repository:

```text
AwakeningOS/AwakeningOS-Quantum-lattice
```

Target repository:

```text
AwakeningOS/quantum-information-matter-lab
```

## Migration policy

Only generic, reusable material was migrated. The new repository should start as a clean lab, not as a dump of the old result chain.

## Migrated or adapted

```text
SKILLS.md discipline:
  no code + no raw log = no result
  layer separation
  raw-log/report/status workflow

scripts/phenomenology/information_microreactor_sandbox.py:
  migrated as a reusable baseline component sandbox
  date/seed updated for the new repo
  evidence-layer wording adapted

scripts/check_raw_logs.py:
  rebuilt as a bootstrap checker for this repository

README.md / results/STATUS.md:
  rebuilt for the contextual information matter direction
```

## Not migrated

```text
old raw logs
old result reports
paper-specific PM/KCBS hardware logs
old unverified phenomenology tables
quarantined claims
```

## Why

The old repository produced the audit discipline. This repository is for the next constructive phase: build new components, combine them, and audit only the claims that need support.

The intended workflow is:

```text
1. keep reusable baselines useful
2. build contextual components as design targets
3. audit only the claims that need quantum/contextual support
4. promote only code-backed and raw-log-backed results
```
