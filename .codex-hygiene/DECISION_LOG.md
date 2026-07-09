# Decision Log

## Exclude raw logs from Git

- Context: Full run is about 2.84 GB; bottleneck map also produces multi-GB logs.
- Options considered: commit all logs; Git LFS; compact evidence only.
- Decision: commit code, protocols, manifests, compact summaries, and reports.
- Reason: explicit user request and repository usability.
- Evidence: user instruction; measured output sizes.
- Reversible: Yes, raw archives can be published separately later.

## Use paired attribution in the bottleneck map

- Context: Initial Q-cell energy can reach W even without external resource.
- Options considered: raw W output; subtract no-resource baseline.
- Decision: use `W(resource)-W(no_resource)` as attributed output.
- Reason: separates initial-state discharge from external-resource transport.
- Evidence: full-run converter-off/no-resource behavior and corrected protocol.
- Reversible: No for primary interpretation; raw values remain available.

## Treat fixed-map run as prerequisite

- Context: Local adaptive control could appear better merely because outlet
  parameters changed.
- Options considered: begin local control immediately; establish fixed envelope.
- Decision: finish fixed-circuit bottleneck map first.
- Reason: gives a matched baseline for causal local-control claims.
- Evidence: explicit user-approved experiment ordering.
- Reversible: Yes, but skipping it weakens later attribution.
