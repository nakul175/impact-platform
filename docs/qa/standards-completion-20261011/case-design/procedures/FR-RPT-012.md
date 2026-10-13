## QA v1.3 — source-bound case design (proposed)

Story `FR-RPT-012` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-RPT-012-001` / `TC-IMPRANA-FR-RPT-012-001` | `REV_0d9ed836778154e951ef99f13044048b6f191735759e776dfd12d32bf908f421` / `REV_c32f5be2909ada26e0a43138e2b48e243b258fe1b9d4661482eafe06d7a8571d` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-RPT-012-002` / `TC-IMPRANA-FR-RPT-012-002` | `REV_405b578c735621df3ec8b397725ad9e3d4c0a7ea95476c564c33e12e07f49c12` / `REV_eefac2724c17002c76e72acd763a4e979ae547c34de7be3acef553e3c27f1000` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-RPT-012-003` / `TC-IMPRANA-FR-RPT-012-003` | `REV_867f217647e10c498d129213c1c686db64a798178d79782b19612b3780aa94f9` / `REV_0368cbf3ef990261ae1bbb8ae5c23864d3a0cc451e83a3cbfffd25eb26283453` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-RPT-012-001 — Reconstruct a published pooled ratio from the package

Source persona: Funder Portfolio Manager. Proposed fixture `FIX-FR-RPT-012-001` is not created. Verification duty `TASK-FR-RPT-012-03` (qualification); source `docs/backlog/backlog.csv` record 302, exact block `0d9ed836778154e951ef99f13044048b6f191735759e776dfd12d32bf908f421`.

**Original preconditions**

1. an audit package for a published report within the permitted scope

**Original actions**

1. the Funder Portfolio Manager uses its contents

**Exact source oracles — all required**

1. the published pooled ratio can be reconstructed
2. file integrity and the content inventory allow completeness to be verified

Legacy same-requirement reuse candidates: `TC-RPT-012-01`, `TC-RPT-012-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-RPT-012-002 — Withheld materials are listed without content

Source persona: Funder Portfolio Manager. Proposed fixture `FIX-FR-RPT-012-002` is not created. Verification duty `TASK-FR-RPT-012-03` (qualification); source `docs/backlog/backlog.csv` record 302, exact block `405b578c735621df3ec8b397725ad9e3d4c0a7ea95476c564c33e12e07f49c12`.

**Original preconditions**

1. an attachment has been lawfully withheld

**Original actions**

1. the package is generated

**Exact source oracles — all required**

1. the withheld attachment is identified in the inventory
2. its private data is not included

Legacy same-requirement reuse candidates: `TC-RPT-012-01`, `TC-RPT-012-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-RPT-012-003 — Reject download without current export authority

Source persona: Funder Portfolio Manager. Proposed fixture `FIX-FR-RPT-012-003` is not created. Verification duty `TASK-FR-RPT-012-03` (qualification); source `docs/backlog/backlog.csv` record 302, exact block `867f217647e10c498d129213c1c686db64a798178d79782b19612b3780aa94f9`.

**Original preconditions**

1. a user whose export authority was removed after the package was generated

**Original actions**

1. they attempt to download the package

**Exact source oracles — all required**

1. the download is refused
2. evidence restrictions remain enforced

Legacy same-requirement reuse candidates: `TC-RPT-012-01`, `TC-RPT-012-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
