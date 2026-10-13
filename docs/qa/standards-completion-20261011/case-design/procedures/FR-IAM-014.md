## QA v1.3 — source-bound case design (proposed)

Story `FR-IAM-014` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-IAM-014-001` / `TC-IMPRANA-FR-IAM-014-001` | `REV_a47bfef94ee4b5b0ba770e12a99b5b11b8c4938a421133b60779e45d05359178` / `REV_a3ca75d8d450e0cbac9ae6c4d5aa63fd0c516cbc69c18cd4ac23bfcb6df18bd8` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-014-002` / `TC-IMPRANA-FR-IAM-014-002` | `REV_1c25be798355ea1977610295d51abf3b2877bf1f25cc9c2faa8d68fb8f31662a` / `REV_2212e5d2a0476be525eb5f28f50614e621882bf8477e0e1f3c4a00a511559b6c` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-014-003` / `TC-IMPRANA-FR-IAM-014-003` | `REV_2f626fa89bdbb18b9eae9fef0bd41fee9dc4d563096d7676aa5abc46a2155bed` / `REV_bbb0814f03f1fb32fc805614663202091aad19157722518d4c3921a255c4a268` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-IAM-014-001 — Offboard a departing member

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-014-001` is not created. Verification duty `TASK-FR-IAM-014-03` (qualification); source `docs/backlog/backlog.csv` record 89, exact block `a47bfef94ee4b5b0ba770e12a99b5b11b8c4938a421133b60779e45d05359178`.

**Original preconditions**

(Absent in original source; unresolved context is recorded separately.)

**Original actions**

1. the Organisation Administrator runs the offboarding wizard for a departing member

**Exact source oracles — all required**

1. access is revoked first
2. owned sources, schedules, drafts, credentials and approval tasks are listed for an authorised successor
3. each item is reassigned, cancelled or held with an owner

**Separate proposed missing context (unapproved)**

1. given

Legacy same-requirement reuse candidates: `TC-IAM-014-01`, `TC-IAM-014-02`, `TC-AT14`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_live_idp.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-014-002 — Remove a schedule owner with an export in progress

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-014-002` is not created. Verification duty `TASK-FR-IAM-014-03` (qualification); source `docs/backlog/backlog.csv` record 89, exact block `1c25be798355ea1977610295d51abf3b2877bf1f25cc9c2faa8d68fb8f31662a`.

**Original preconditions**

1. a report schedule owner has an export in progress

**Original actions**

1. they are removed

**Exact source oracles — all required**

1. receipts are preserved
2. export and delivery jobs reauthorise before any sensitive action
3. the successor decision is recorded

Legacy same-requirement reuse candidates: `TC-IAM-014-01`, `TC-IAM-014-02`, `TC-AT14`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_live_idp.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-014-003 — Reject unapproved delivery and impersonation

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-014-003` is not created. Verification duty `TASK-FR-IAM-014-03` (qualification); source `docs/backlog/backlog.csv` record 89, exact block `2f626fa89bdbb18b9eae9fef0bd41fee9dc4d563096d7676aa5abc46a2155bed`.

**Original preconditions**

1. work from a departed member has been reassigned

**Original actions**

1. the work continues

**Exact source oracles — all required**

1. it does not run under the departed person's orphaned human session
2. the departed person's approval decision is not transferred
3. content visibility follows the successor's explicit grants
4. unapproved delivery is prevented

Legacy same-requirement reuse candidates: `TC-IAM-014-01`, `TC-IAM-014-02`, `TC-AT14`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_live_idp.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
