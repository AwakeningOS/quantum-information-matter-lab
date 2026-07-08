# Research Repository Operating Skills

This repository is a research workspace for contextual information-matter experiments. The operating rule is strict:

```text
No code + no raw log = no result.
```

Markdown reports are explanations, not primary data. A result becomes citeable only when the repository contains:

```text
1. a committed generator script
2. a fixed seed/config
3. a committed raw log or equivalent artifact
4. a report pointing to script, command, and raw log
5. a status entry in results/STATUS.md
6. a reproducibility check when possible
```

## Layer separation

Keep these layers separate.

```text
CLASSICAL_COMPONENT:
  useful phenomenological components such as membrane, source, sink,
  reservoir, converter, road, buffer, terrain.

CONTEXTUAL_COMPONENT:
  components whose behavior depends on question/context structure.
  These are design targets, not automatic quantum claims.

QUANTUM_AUDIT:
  witness/control tests used only when making quantum-specific claims.
  Examples: contextuality witness, dephase control, marginal matching,
  Bell/CHSH control, readout/control comparisons.

PAPER_ANALYSIS:
  interpretation, limitations, figure mapping, manuscript material.

QUARANTINED:
  old or failed claims retained only as historical notes.
```

Do not let quantum/audit vocabulary leak into component reports unless the controls exist.

## Vocabulary guard

Allowed component-layer words:

```text
classical, phenomenological, stochastic, component, throughput,
selectivity, retention, release, conversion, fidelity, promiscuity,
gating, hysteresis, poisoning, stress, buffering, source, sink,
reservoir, converter, membrane, road, terrain, memory
```

Audit words require controls:

```text
quantum, contextuality, negativity, entanglement, coherence,
dephase, measurement backaction, Bell, CHSH, nonclassical,
quantum advantage
```

If those words appear in a component report, the report must state whether it is a design target, a tested witness, or a forbidden claim.

## Required layout

```text
README.md
SKILLS.md
requirements.txt
.gitignore
.github/workflows/reproducibility.yml

scripts/
  check_raw_logs.py
  phenomenology/
  contextual/
  audit/

configs/
data/
results/
experiments/
docs/
paper/
archive/
```

## Experiment lifecycle

### 1. Protocol first

Before any major run, create:

```text
experiments/<experiment_name>_protocol_YYYY-MM-DD.md
```

The protocol must state:

```text
question
layer
model
metrics
controls
success/failure criteria
seeds
raw outputs
known limitations
forbidden claims
```

### 2. Generator script

Script requirements:

```text
accept seed/config/output path arguments
write deterministic raw data for fixed seed when possible
save machine-readable outputs
state its layer in a docstring
avoid hard-coded report tables as the only source of truth
```

### 3. Raw log

Save raw data under `data/` with seed/config metadata.

### 4. Report

Reports live under `results/`. Header must include:

```text
Status:
Generator script:
Raw log:
Run command:
Layer:
Verdict:
Limitations:
```

### 5. Status index

Update `results/STATUS.md` whenever a result is added or changed.

### 6. Reproducibility check

Run:

```bash
python scripts/check_raw_logs.py
```

Do not mark a result `RAW_LOG_BACKED` if the canonical check fails.

## Component-development workflow

For reusable information-material parts, each component should define:

```text
role
state variables
inputs
outputs
control parameters
material-property curves
failure modes
composition interfaces
```

Useful starting roles:

```text
membrane: access/filtering
source-sink: injection/removal
reservoir: timing/storage/leak/overflow
converter: identity/meaning transformation
road: transport bias
buffer: stress/flux stabilization
terrain: history-written environment
memory: retained observed/unobserved alternatives
self-register: internal record of reading context
```

## Contextual-component workflow

A contextual component must specify:

```text
question/context set
compatibility relation
state update rule
observed output
unobserved alternative state
classical/replay control
forbidden interpretation
```

Contextual behavior alone is not a quantum claim. Quantum-specific status requires a separate audit.

## Quantum/audit workflow

Audit reports must include:

```text
witness or control definition
classical probability control
marginal matching if relevant
dephase or replay control where relevant
success and failure criteria
systematic-error caveats
```

Accept negative results. Showing that a behavior is classical-effective is useful.

## Never do this

```text
Do not paste AI-made tables into results/ as raw data.
Do not call a behavior quantum-specific without controls.
Do not call anything life/cell/metabolism/self-repair unless directly defined and measured.
Do not hide stale logs after changing scripts.
Do not mix component-building claims and witness claims.
Do not promote a design metaphor into a physical claim.
```
