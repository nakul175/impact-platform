## QA v1.3 — source-bound case design (proposed)

Story `VF-PRV-001` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-VF-PRV-001-001` / `TC-IMPRANA-VF-PRV-001-001` | `REV_0dceb3b29735cf03db8f617fb81b303db7c3277932cddcb303463c8b4dedc852` / `REV_668df61a772ab2a3237efb0e2d924bb72adf784a7a927046e24dfce0a55b54aa` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-PRV-001-002` / `TC-IMPRANA-VF-PRV-001-002` | `REV_b02e3c360f942a43189b7760f6a9d12fc35ab385116476a5ee03b3b63c4eaee5` / `REV_bf7b2064c1af264e6212d741e673adcb9fb71e18ba1dda8a8a2a2b9f3e5fa87d` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-PRV-001-003` / `TC-IMPRANA-VF-PRV-001-003` | `REV_3a7919c10158599fab8fc3301f6d092345dac8c3ca63f3dd3c09b016e88fcb9e` / `REV_d71e5ea6129ca0d58c3bb3c2d5c5326e6c6be9fb6ae38c9beb871551f5b1c14d` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-PRV-001-004` / `TC-IMPRANA-VF-PRV-001-004` | `REV_e77321b1ae36239ecad1964b446f0bdf06fb46211ef131caf332ef0fe8e349d5` / `REV_42c2e1a0c64e4eb1bb90ea6bd194946369b01400fc5dd5f115925f6311e244fe` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-VF-PRV-001-001 — Active stores are cleared within 24 hours

Source persona: Privacy Officer. Proposed fixture `FIX-VF-PRV-001-001` is not created. Verification duty `TASK-VF-PRV-001-02` (qualification); source `docs/backlog/backlog.csv` record 135, exact block `0dceb3b29735cf03db8f617fb81b303db7c3277932cddcb303463c8b4dedc852`.

**Original preconditions**

1. an authorised deletion has become executable and no hold applies

**Original actions**

1. 24 hours have passed

**Exact source oracles — all required**

1. primary records, caches, indexes, search, AI and platform-generated derivatives are removed or effectively restricted

Legacy same-requirement reuse candidates: `TC-VF-PRV-001`, `TC-AT15`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-PRV-001-002 — Backup expiry and external recipients are tracked separately

Source persona: Privacy Officer. Proposed fixture `FIX-VF-PRV-001-002` is not created. Verification duty `TASK-VF-PRV-001-02` (qualification); source `docs/backlog/backlog.csv` record 135, exact block `b02e3c360f942a43189b7760f6a9d12fc35ab385116476a5ee03b3b63c4eaee5`.

**Original preconditions**

1. the active-store deletion is complete

**Original actions**

1. backup and external status is reviewed

**Exact source oracles — all required**

1. backup expiry follows the approved schedule, normally within 35 days
2. external recipient actions are tracked separately

Legacy same-requirement reuse candidates: `TC-VF-PRV-001`, `TC-AT15`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-PRV-001-003 — Reject labelling a partial deletion complete

Source persona: Privacy Officer. Proposed fixture `FIX-VF-PRV-001-003` is not created. Verification duty `TASK-VF-PRV-001-02` (qualification); source `docs/backlog/backlog.csv` record 135, exact block `3a7919c10158599fab8fc3301f6d092345dac8c3ca63f3dd3c09b016e88fcb9e`.

**Original preconditions**

1. a deletion with a partial hold or a failed derivative store

**Original actions**

1. the deletion manifest is produced

**Exact source oracles — all required**

1. the manifest is not labelled complete

Legacy same-requirement reuse candidates: `TC-VF-PRV-001`, `TC-AT15`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-PRV-001-004 — Reject exposing restored content before deletion is verified

Source persona: Privacy Officer. Proposed fixture `FIX-VF-PRV-001-004` is not created. Verification duty `TASK-VF-PRV-001-03` (qualification); source `docs/backlog/backlog.csv` record 135, exact block `e77321b1ae36239ecad1964b446f0bdf06fb46211ef131caf332ef0fe8e349d5`.

**Original preconditions**

1. an old backup containing deleted data is restored

**Original actions**

1. restored content would be exposed

**Exact source oracles — all required**

1. deletion is verified before any restored content is exposed

Legacy same-requirement reuse candidates: `TC-VF-PRV-001`, `TC-AT15`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
