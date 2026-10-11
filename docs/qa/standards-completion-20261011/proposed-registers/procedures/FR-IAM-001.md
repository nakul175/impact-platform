## QA v1.3 — source-bound case design (proposed)

Story `FR-IAM-001` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-IAM-001-001` / `TC-IMPRANA-FR-IAM-001-001` | `REV_8d69ddbd626cb8470c0a0d3da6751afa235a76d4b38a94e359682fd5e6de42f4` / `REV_60be4d4cc08486c1ee9caac165bfd982f392efe883e97b3e4dded34605f0768d` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-001-002` / `TC-IMPRANA-FR-IAM-001-002` | `REV_8253b49f31db253890983a7879e84141595d977e21650e418ef41970b58b72dc` / `REV_870d61ae7f58d3dea413079d860e018d3ae14e11a64edb6353dd77265473d504` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-001-003` / `TC-IMPRANA-FR-IAM-001-003` | `REV_2b5dedc577a94b9212b2bf405b0f93446496dcb1b80d5fd4d4740206502f7047` / `REV_7c693b386b6fc898c4c2a4f3b145286238fce9634f24932251a50700e5e8dd4c` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-001-004` / `TC-IMPRANA-FR-IAM-001-004` | `REV_1cca07357dbd5aa12c0d2bd2cee1c88f0a63570a932415c757541c945799504e` / `REV_459414669f9039a5821bbda3ef38cd6bd0e91c4dfa13eab8f6f6585c52353a24` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-IAM-001-001 — Preview and send an invitation

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-001-001` is not created. Verification duty `TASK-FR-IAM-001-03` (qualification); source `docs/backlog/backlog.csv` record 83, exact block `8d69ddbd626cb8470c0a0d3da6751afa235a76d4b38a94e359682fd5e6de42f4`.

**Original preconditions**

1. an Organisation Administrator selects tenant, role template, explicit scopes, expiry and the intended verified identity

**Original actions**

1. they preview the invitation

**Exact source oracles — all required**

1. the effective capabilities are shown before sending
2. the invitation expires in seven days by default

Legacy same-requirement reuse candidates: `TC-IAM-001-01`, `TC-IAM-001-02`, `SEC-009`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_live_idp.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-001-002 — Accept an invitation

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-001-002` is not created. Verification duty `TASK-FR-IAM-001-03` (qualification); source `docs/backlog/backlog.csv` record 83, exact block `8253b49f31db253890983a7879e84141595d977e21650e418ef41970b58b72dc`.

**Original preconditions**

1. a valid invitation token and an inviter who still has authority

**Original actions**

1. the invitee proves control of the nominated identity and accepts

**Exact source oracles — all required**

1. exactly one membership is created

Legacy same-requirement reuse candidates: `TC-IAM-001-01`, `TC-IAM-001-02`, `SEC-009`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_live_idp.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-001-003 — Report bulk invitation outcomes

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-001-003` is not created. Verification duty `TASK-FR-IAM-001-03` (qualification); source `docs/backlog/backlog.csv` record 83, exact block `2b5dedc577a94b9212b2bf405b0f93446496dcb1b80d5fd4d4740206502f7047`.

**Original preconditions**

(Absent in original source; unresolved context is recorded separately.)

**Original actions**

1. the Organisation Administrator sends invitations in bulk

**Exact source oracles — all required**

1. outcomes are reported separately as created, duplicate, invalid and delivery failed
2. receiving the email alone is not treated as membership activation

**Separate proposed missing context (unapproved)**

1. given

Legacy same-requirement reuse candidates: `TC-IAM-001-01`, `TC-IAM-001-02`, `SEC-009`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_live_idp.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-001-004 — Reject forwarded, replayed or superseded invitations

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-001-004` is not created. Verification duty `TASK-FR-IAM-001-03` (qualification); source `docs/backlog/backlog.csv` record 83, exact block `1cca07357dbd5aa12c0d2bd2cee1c88f0a63570a932415c757541c945799504e`.

**Original preconditions**

1. an invitation forwarded to a different signed in account, a token that has already been consumed, or a token invalidated by a resend

**Original actions**

1. the token is used to accept

**Exact source oracles — all required**

1. acceptance fails
2. no protected tenant content is revealed

Legacy same-requirement reuse candidates: `TC-IAM-001-01`, `TC-IAM-001-02`, `SEC-009`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_live_idp.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
