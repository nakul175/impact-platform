## QA v1.3 — source-bound case design (proposed)

Story `FR-PRV-006` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-PRV-006-001` / `TC-IMPRANA-FR-PRV-006-001` | `REV_f65c579344ec6bea895acee7940c9464153fe09f08002b8f44cb527e3f47c241` / `REV_bda943746c43d254c416ac9b9ee48b63134660e5f6d87185cc6a5dd7c8204727` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRV-006-002` / `TC-IMPRANA-FR-PRV-006-002` | `REV_65598660207865077fd5dc63d4733d2db402b0213ca3254fb55fa6f1b680788b` / `REV_ad45503b827d859e0d6daaeac33a91b841bf475bf536f34d119e6aa4795bbd36` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRV-006-003` / `TC-IMPRANA-FR-PRV-006-003` | `REV_741e4afb7bc5bcfb71c5b0108030f4607ebd417c489a762cf09cf6dd0945c681` / `REV_109d49df6047f3675c6afbb990c4ccfcc76d7a782e992b1eb03f969434175f6b` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRV-006-004` / `TC-IMPRANA-FR-PRV-006-004` | `REV_f9bbe84ce4f85f70e9a5035b098cfa4e4c8f4686c743326509beb2f7d30059ee` / `REV_4315cdcd965b8db3d4641cd1e932f14d5c6281f0804998ba0f9012e9ad6076f9` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-PRV-006-001 — Restored backup keeps a deleted participant unavailable

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-006-001` is not created. Verification duty `TASK-FR-PRV-006-04` (qualification); source `docs/backlog/backlog.csv` record 131, exact block `f65c579344ec6bea895acee7940c9464153fe09f08002b8f44cb527e3f47c241`.

**Original preconditions**

1. a participant deleted after a backup was taken

**Original actions**

1. a Platform Operator restores that backup

**Exact source oracles — all required**

1. the restore stays closed to ordinary users until deletion instructions and current grants are reapplied and verified
2. the participant is unavailable before any user or AI query is admitted

Legacy same-requirement reuse candidates: `TC-PRV-006-01`, `TC-PRV-006-02`, `TC-AT15`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRV-006-002 — Deletion ledger holds only what is needed

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-006-002` is not created. Verification duty `TASK-FR-PRV-006-04` (qualification); source `docs/backlog/backlog.csv` record 131, exact block `65598660207865077fd5dc63d4733d2db402b0213ca3254fb55fa6f1b680788b`.

**Original preconditions**

1. a completed deletion

**Original actions**

1. the deletion ledger is inspected

**Exact source oracles — all required**

1. it records only the minimal object identifiers and restriction instructions needed to prevent restoration
2. backup expiry is recorded separately

Legacy same-requirement reuse candidates: `TC-PRV-006-01`, `TC-PRV-006-02`, `TC-AT15`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRV-006-003 — Reject reopening revoked access through a restored grant

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-006-003` is not created. Verification duty `TASK-FR-PRV-006-04` (qualification); source `docs/backlog/backlog.csv` record 131, exact block `741e4afb7bc5bcfb71c5b0108030f4607ebd417c489a762cf09cf6dd0945c681`.

**Original preconditions**

1. a backup containing a historic grant that has since been revoked

**Original actions**

1. the backup is restored

**Exact source oracles — all required**

1. the historic grant does not reopen access

Legacy same-requirement reuse candidates: `TC-PRV-006-01`, `TC-PRV-006-02`, `TC-AT15`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRV-006-004 — Reject a claim of instant erasure from immutable backups

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-006-004` is not created. Verification duty `TASK-FR-PRV-006-04` (qualification); source `docs/backlog/backlog.csv` record 131, exact block `f9bbe84ce4f85f70e9a5035b098cfa4e4c8f4686c743326509beb2f7d30059ee`.

**Original preconditions**

1. backups that support only bounded expiry

**Original actions**

1. the deletion outcome is reported

**Exact source oracles — all required**

1. it does not claim instant physical erasure from those backups

Legacy same-requirement reuse candidates: `TC-PRV-006-01`, `TC-PRV-006-02`, `TC-AT15`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
