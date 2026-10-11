## QA v1.3 — source-bound case design (proposed)

Story `FR-CAL-012` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-CAL-012-001` / `TC-IMPRANA-FR-CAL-012-001` | `REV_fdd371ed018734bc976e605efa0349178a864309ec373fe5f27620578b1063d3` / `REV_20389f922872defbf8babd1ae35d83a7b3314ae38f5fe2dacc88d4197be0d353` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-012-002` / `TC-IMPRANA-FR-CAL-012-002` | `REV_e51449ddd581ab54253d7e0c9e4db59d9376e27bfaf7ee89ffd5320caa30da88` / `REV_154e8c190f748eeb2d8c9c361acf2a648b7068fb076b8ff8a95da86a994b7fa4` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-012-003` / `TC-IMPRANA-FR-CAL-012-003` | `REV_1f087ebf2e05113954d44ecacbedee96470bdc676454c0f69088a697a5213c78` / `REV_0237169a6718bccfb85e6e8dc9003c0ea11b7732520a75c4c901b70ca3823b82` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-CAL-012-001 — Preview validates a formula before review

Source persona: MEL Manager. Proposed fixture `FIX-FR-CAL-012-001` is not created. Verification duty `TASK-FR-CAL-012-03` (qualification); source `docs/backlog/backlog.csv` record 202, exact block `fdd371ed018734bc976e605efa0349178a864309ec373fe5f27620578b1063d3`.

**Original preconditions**

1. a formula using typed references and catalogue functions such as sum and ratio

**Original actions**

1. the MEL Manager previews it

**Exact source oracles — all required**

1. permissions, dependency cycles and units are validated
2. sample outputs are shown before it is submitted for review

Legacy same-requirement reuse candidates: `TC-CAL-012-01`, `TC-CAL-012-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-012-002 — Reject inaccessible, circular and external references

Source persona: MEL Manager. Proposed fixture `FIX-FR-CAL-012-002` is not created. Verification duty `TASK-FR-CAL-012-03` (qualification); source `docs/backlog/backlog.csv` record 202, exact block `e51449ddd581ab54253d7e0c9e4db59d9376e27bfaf7ee89ffd5320caa30da88`.

**Original preconditions**

1. formulas that reference an inaccessible field, a circular indicator and an external URL call

**Original actions**

1. each is validated

**Exact source oracles — all required**

1. each is rejected before activation

Legacy same-requirement reuse candidates: `TC-CAL-012-01`, `TC-CAL-012-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-012-003 — Reject scripts and unsupported functions

Source persona: MEL Manager. Proposed fixture `FIX-FR-CAL-012-003` is not created. Verification duty `TASK-FR-CAL-012-03` (qualification); source `docs/backlog/backlog.csv` record 202, exact block `1f087ebf2e05113954d44ecacbedee96470bdc676454c0f69088a697a5213c78`.

**Original preconditions**

1. a formula containing an unsupported function, an arbitrary script, a filesystem reference or a dynamically broadened query

**Original actions**

1. it is validated

**Exact source oracles — all required**

1. it fails validation

Legacy same-requirement reuse candidates: `TC-CAL-012-01`, `TC-CAL-012-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
