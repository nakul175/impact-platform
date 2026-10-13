## QA v1.3 — source-bound case design (proposed)

Story `FR-IND-015` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-IND-015-001` / `TC-IMPRANA-FR-IND-015-001` | `REV_5fb306954f1b0a066bcecf891f47d5005e1f520e8e05634f85f878451b69e875` / `REV_56ffb86936d49fb838ccac2371182982f603bfb06a3d9c53f2f1825ce7449e9c` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IND-015-002` / `TC-IMPRANA-FR-IND-015-002` | `REV_7fc43e299ee4116f8a2d25ee199cf5f1a0cf482a7faeb8df738255e13356da46` / `REV_fbe3fa333d0959b0b23bca02e99cf454a2f9bff4bf6d9550568f53dec9ff18ae` | manual → MANUAL recommendation; UNRESOLVED; Not run |
| `AC-FR-IND-015-003` / `TC-IMPRANA-FR-IND-015-003` | `REV_e1ad78eeb492e5a18776d19bd2b2dd31df4a41c22829e4e59f3ebb28ca3911a9` / `REV_d61f69d7e0bc601be3aa163089e5f183455007bdc5372682f30137bbc8026677` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-IND-015-001 — Export reference sheets

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-015-001` is not created. Verification duty `TASK-FR-IND-015-03` (qualification); source `docs/backlog/backlog.csv` record 247, exact block `5fb306954f1b0a066bcecf891f47d5005e1f520e8e05634f85f878451b69e875`.

**Original preconditions**

1. selected indicator versions

**Original actions**

1. the MEL Manager exports reference sheets

**Exact source oracles — all required**

1. the export includes human readable definitions and a machine readable dictionary
2. it covers units, eligibility, dimensions, time semantic, formula, source, roles, missingness rules and version references

Legacy same-requirement reuse candidates: `TC-IND-015-01`, `TC-IND-015-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IND-015-002 — Evaluator understands a ratio

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-015-002` is not created. Verification duty `TASK-FR-IND-015-03` (qualification); source `docs/backlog/backlog.csv` record 247, exact block `7fc43e299ee4116f8a2d25ee199cf5f1a0cf482a7faeb8df738255e13356da46`.

**Original preconditions**

1. an evaluator who receives a ratio reference sheet

**Original actions**

1. they read it

**Exact source oracles — all required**

1. they can identify numerator population, denominator, multiplier and period without consulting the application's private settings

Legacy same-requirement reuse candidates: `TC-IND-015-01`, `TC-IND-015-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IND-015-003 — Reject leaking restricted content or losing precision

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-015-003` is not created. Verification duty `TASK-FR-IND-015-03` (qualification); source `docs/backlog/backlog.csv` record 247, exact block `e1ad78eeb492e5a18776d19bd2b2dd31df4a41c22829e4e59f3ebb28ca3911a9`.

**Original preconditions**

1. an export scope that excludes restricted definitions or source names

**Original actions**

1. the export is produced

**Exact source oracles — all required**

1. those items are redacted and marked withheld
2. display rounding does not replace calculation precision metadata

Legacy same-requirement reuse candidates: `TC-IND-015-01`, `TC-IND-015-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
