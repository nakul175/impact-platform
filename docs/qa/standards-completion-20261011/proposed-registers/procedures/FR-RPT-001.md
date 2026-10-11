## QA v1.3 — source-bound case design (proposed)

Story `FR-RPT-001` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-RPT-001-001` / `TC-IMPRANA-FR-RPT-001-001` | `REV_8c73fa6dc068e0c2f155daf2222903964243c39d8e8ee07e0242301c8fb3445e` / `REV_0556192dbf86722949e7361769010caee9eebc53255fd754d6ea9182e3a9a3ef` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-RPT-001-002` / `TC-IMPRANA-FR-RPT-001-002` | `REV_55f8848aff20f359429130d6324ea7b4716fb9418e38c8ece8e73acd8a16e73b` / `REV_53ddbb32a0ed96817b2091760937922b9eb508e6e1782fa509edcfe9d6133d18` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-RPT-001-003` / `TC-IMPRANA-FR-RPT-001-003` | `REV_c52c01385cbc2c2aad888143a5b0109e56b6c307f7f4b339d055bd8cd21fdc61` / `REV_bab5b51a553e249d81976ba512c9a2c3110cb29fe1fc01250295adaee8433114` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-RPT-001-004` / `TC-IMPRANA-FR-RPT-001-004` | `REV_df1b0b981d8bb81ef65c87f4960bd16c317cab95664918b2fc5d7392e8048ed4` / `REV_8d305fa500e1913ed2be05facc9b7bd14c9ec41d4d2dc2edfb192979db28fd41` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-RPT-001-001 — Two donor reports from one snapshot reconcile

Source persona: MEL Manager. Proposed fixture `FIX-FR-RPT-001-001` is not created. Verification duty `TASK-FR-RPT-001-03` (qualification); source `docs/backlog/backlog.csv` record 297, exact block `8c73fa6dc068e0c2f155daf2222903964243c39d8e8ee07e0242301c8fb3445e`.

**Original preconditions**

1. published report templates for donor A and donor B

**Original actions**

1. the MEL Manager generates quarterly reports for both from one approved snapshot

**Exact source oracles — all required**

1. shared numeric fields in both reports reconcile to the same result IDs

Legacy same-requirement reuse candidates: `TC-RPT-001-01`, `TC-RPT-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-RPT-001-002 — Template preview validates against a snapshot

Source persona: MEL Manager. Proposed fixture `FIX-FR-RPT-001-002` is not created. Verification duty `TASK-FR-RPT-001-03` (qualification); source `docs/backlog/backlog.csv` record 297, exact block `55f8848aff20f359429130d6324ea7b4716fb9418e38c8ece8e73acd8a16e73b`.

**Original preconditions**

1. a draft report template

**Original actions**

1. the MEL Manager previews it

**Exact source oracles — all required**

1. it is validated against a representative approved snapshot

Legacy same-requirement reuse candidates: `TC-RPT-001-01`, `TC-RPT-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-RPT-001-003 — Reject zero placeholders for missing bindings

Source persona: MEL Manager. Proposed fixture `FIX-FR-RPT-001-003` is not created. Verification duty `TASK-FR-RPT-001-03` (qualification); source `docs/backlog/backlog.csv` record 297, exact block `c52c01385cbc2c2aad888143a5b0109e56b6c307f7f4b339d055bd8cd21fdc61`.

**Original preconditions**

1. a template with a required metric binding that is missing

**Original actions**

1. a report is generated

**Exact source oracles — all required**

1. the missing binding appears as an explicit gap
2. no zero placeholder is inserted

Legacy same-requirement reuse candidates: `TC-RPT-001-01`, `TC-RPT-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-RPT-001-004 — Reject silent changes to published reports

Source persona: MEL Manager. Proposed fixture `FIX-FR-RPT-001-004` is not created. Verification duty `TASK-FR-RPT-001-03` (qualification); source `docs/backlog/backlog.csv` record 297, exact block `df1b0b981d8bb81ef65c87f4960bd16c317cab95664918b2fc5d7392e8048ed4`.

**Original preconditions**

1. a report created from a published template version

**Original actions**

1. the donor template is changed

**Exact source oracles — all required**

1. a new template version is created
2. the existing report stays pinned to its original template version without being restyled or changed

Legacy same-requirement reuse candidates: `TC-RPT-001-01`, `TC-RPT-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
