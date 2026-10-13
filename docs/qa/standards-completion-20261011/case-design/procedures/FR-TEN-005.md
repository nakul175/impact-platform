## QA v1.3 — source-bound case design (proposed)

Story `FR-TEN-005` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-TEN-005-001` / `TC-IMPRANA-FR-TEN-005-001` | `REV_ea7336d754102029f60b6077d3a1a6f3c3f14fc468f645605b5948dd8a442910` / `REV_8c0aec3b87f788df25ee24d3dfa42283fdcbaf4c1bd2cd94d147a52846035601` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-TEN-005-002` / `TC-IMPRANA-FR-TEN-005-002` | `REV_be35e6ee66f9f19ffbe1438ed8babca2908e7f567dda949c9d9148e596ccf375` / `REV_f9677fa3a7a22cb40550a56d615e7a13e6745b5e3805ef476b71be0ac97d0a6a` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-TEN-005-003` / `TC-IMPRANA-FR-TEN-005-003` | `REV_3a85f6d5bbbb577c95788d17577f91eb8ec9dccde60a4bb7bf9af765a9e4afc1` / `REV_8f7ce9bab068aa165104e33ab41fc4d86038ba8b09ad2ee353c18079c19dd90a` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-TEN-005-004` / `TC-IMPRANA-FR-TEN-005-004` | `REV_b2dd075723a4136822f976e1af786e60f1c36dbb88fc1a76ace53eae9145709b` / `REV_a8e00bb9720320d35e3b7105965cc0167561faf32a5ff852e23f990b0ff1d286` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-TEN-005-001 — Preview and publish a custom field

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-TEN-005-001` is not created. Verification duty `TASK-FR-TEN-005-03` (qualification); source `docs/backlog/backlog.csv` record 311, exact block `ea7336d754102029f60b6077d3a1a6f3c3f14fc468f645605b5948dd8a442910`.

**Original preconditions**

1. an Organisation Administrator selects a field type, stable code, permitted object types, required condition, validation and classification

**Original actions**

1. they preview the field

**Exact source oracles — all required**

1. the preview shows its availability in forms, imports, search and reports
2. publishing creates a field definition version that templates reference

Legacy same-requirement reuse candidates: `TC-TEN-005-01`, `TC-TEN-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-TEN-005-002 — Use a restricted conditional field

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-TEN-005-002` is not created. Verification duty `TASK-FR-TEN-005-03` (qualification); source `docs/backlog/backlog.csv` record 311, exact block `be35e6ee66f9f19ffbe1438ed8babca2908e7f567dda949c9d9148e596ccf375`.

**Original preconditions**

1. a published restricted decimal field required only for active grants

**Original actions**

1. an authorised import supplies values for the field

**Exact source oracles — all required**

1. the import succeeds
2. an external viewer sees neither the value nor a search facet for the field

Legacy same-requirement reuse candidates: `TC-TEN-005-01`, `TC-TEN-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-TEN-005-003 — Retire a field

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-TEN-005-003` is not created. Verification duty `TASK-FR-TEN-005-03` (qualification); source `docs/backlog/backlog.csv` record 311, exact block `3a85f6d5bbbb577c95788d17577f91eb8ec9dccde60a4bb7bf9af765a9e4afc1`.

**Original preconditions**

1. a field with historical values

**Original actions**

1. the Organisation Administrator retires it

**Exact source oracles — all required**

1. new entry is no longer possible
2. historical values and their restricted visibility are preserved

Legacy same-requirement reuse candidates: `TC-TEN-005-01`, `TC-TEN-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-TEN-005-004 — Reject a type change without a migration mapping

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-TEN-005-004` is not created. Verification duty `TASK-FR-TEN-005-03` (qualification); source `docs/backlog/backlog.csv` record 311, exact block `b2dd075723a4136822f976e1af786e60f1c36dbb88fc1a76ace53eae9145709b`.

**Original preconditions**

1. a field that already has values

**Original actions**

1. the Organisation Administrator changes its type without an explicit migration mapping

**Exact source oracles — all required**

1. the change is rejected
2. they must supply a migration mapping or create a new field

Legacy same-requirement reuse candidates: `TC-TEN-005-01`, `TC-TEN-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
