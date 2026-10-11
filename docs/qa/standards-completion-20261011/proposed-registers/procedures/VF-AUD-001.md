## QA v1.3 — source-bound case design (proposed)

Story `VF-AUD-001` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-VF-AUD-001-001` / `TC-IMPRANA-VF-AUD-001-001` | `REV_1a32e1c46b8c518c52b322c85a9f7c21957ba541f479c81367cb094dff74de6a` / `REV_95eb027675bc1618a7175f058b0a79fa23a612040997a53837478e4f6b8a00e1` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-AUD-001-002` / `TC-IMPRANA-VF-AUD-001-002` | `REV_2794e6b530ecacd52c2e40fb5ee0ee6fdb52ab33e0225a782e317235fff6c3fe` / `REV_f81b28d2e08a8cfeb8b36352b192e7e531d8e56b3b070c1bf4773d096f9c9acf` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-AUD-001-003` / `TC-IMPRANA-VF-AUD-001-003` | `REV_db4f7d3353d21f5b3ee99651855480e93c85a20a32c114143df0ae522e5764b1` / `REV_fc4bab081bdf4a96a36cf1b77b98d19bbe585371a9533ae0fbf49856c5cc2c48` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-VF-AUD-001-001 — Every audit event class is captured and searchable

Source persona: Organisation Administrator. Proposed fixture `FIX-VF-AUD-001-001` is not created. Verification duty `TASK-VF-AUD-001-03` (qualification); source `docs/backlog/backlog.csv` record 108, exact block `1a32e1c46b8c518c52b322c85a9f7c21957ba541f479c81367cb094dff74de6a`.

**Original preconditions**

1. every defined audit event class is executed, including denied operations, restricted reads and privileged actions

**Original actions**

1. an authorised reviewer searches the audit log

**Exact source oracles — all required**

1. each event is found
2. command receipts reconcile to immutable events and a permitted audit export

Legacy same-requirement reuse candidates: `TC-VF-AUD-001`, `SEC-039`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_audit_export.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-AUD-001-002 — Retention defaults are applied and verified separately

Source persona: Organisation Administrator. Proposed fixture `FIX-VF-AUD-001-002` is not created. Verification duty `TASK-VF-AUD-001-03` (qualification); source `docs/backlog/backlog.csv` record 108, exact block `2794e6b530ecacd52c2e40fb5ee0ee6fdb52ab33e0225a782e317235fff6c3fe`.

**Original preconditions**

1. security event metadata and business audit events

**Original actions**

1. retention is applied

**Exact source oracles — all required**

1. security event metadata expires by default after 365 days
2. longer business audit retention follows tenant policy and is verified separately

Legacy same-requirement reuse candidates: `TC-VF-AUD-001`, `SEC-039`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_audit_export.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-AUD-001-003 — Reject secrets or unnecessary personal payloads in audit events

Source persona: Organisation Administrator. Proposed fixture `FIX-VF-AUD-001-003` is not created. Verification duty `TASK-VF-AUD-001-03` (qualification); source `docs/backlog/backlog.csv` record 108, exact block `db4f7d3353d21f5b3ee99651855480e93c85a20a32c114143df0ae522e5764b1`.

**Original preconditions**

1. captured audit events

**Original actions**

1. they are inspected

**Exact source oracles — all required**

1. any secret value fails the check
2. any unnecessary personal payload fails the check

Legacy same-requirement reuse candidates: `TC-VF-AUD-001`, `SEC-039`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_audit_export.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
