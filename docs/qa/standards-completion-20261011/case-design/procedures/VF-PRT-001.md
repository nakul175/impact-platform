## QA v1.3 — source-bound case design (proposed)

Story `VF-PRT-001` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-VF-PRT-001-001` / `TC-IMPRANA-VF-PRT-001-001` | `REV_b49f3f8f6d8705fd15da0e2c9c0573f4f0948c8f3575cc4af67af8deeb6cdc25` / `REV_d2cb034f064972e424c4e8211bbec3bb9d68c678aa0e775157692d78ca76bbf6` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-PRT-001-002` / `TC-IMPRANA-VF-PRT-001-002` | `REV_334f043a2ca664c5b8ace04604d323aceb909cbb0a033c9096757824c67b5996` / `REV_75d5cdd4431778b65600340ee36c3b018e7e6821ae11a4c07af1ed4f582bd410` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-PRT-001-003` / `TC-IMPRANA-VF-PRT-001-003` | `REV_02ac23f613e8e13ba7374373cf8a75057cc60afdb067ec3c2aa4358303c42d6f` / `REV_185974b88a1a1d47a09f63255b0c046c347c0066e6d5f0029f9ff25878d2c86c` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-PRT-001-004` / `TC-IMPRANA-VF-PRT-001-004` | `REV_46bd5caed4d424d849e96f166f4cfd286d125d92b00684d8b5e902ab2ab0508d` / `REV_e59d5c724204d73ebb739a02b5c384d0ef77c21265f58b518c551f4161eb7f1c` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-VF-PRT-001-001 — Standard tenant export is delivered within 24 hours

Source persona: Organisation Administrator. Proposed fixture `FIX-VF-PRT-001-001` is not created. Verification duty `TASK-VF-PRT-001-03` (qualification); source `docs/backlog/backlog.csv` record 116, exact block `b49f3f8f6d8705fd15da0e2c9c0573f4f0948c8f3575cc4af67af8deeb6cdc25`.

**Original preconditions**

1. a standard tenant with up to one million structured rows and 10 GB of attachments

**Original actions**

1. the Organisation Administrator requests a tenant export under the agreed service process

**Exact source oracles — all required**

1. a complete asynchronous package with a documented manifest and machine-readable relationships is delivered within 24 hours
2. completeness, integrity, permissions and exclusions are verified within that time

Legacy same-requirement reuse candidates: `TC-VF-PRT-001`, `TC-AT20`, `SEC-040`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_report_exports.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-PRT-001-002 — Package is usable outside the product

Source persona: Organisation Administrator. Proposed fixture `FIX-VF-PRT-001-002` is not created. Verification duty `TASK-VF-PRT-001-03` (qualification); source `docs/backlog/backlog.csv` record 116, exact block `334f043a2ca664c5b8ace04604d323aceb909cbb0a033c9096757824c67b5996`.

**Original preconditions**

1. the delivered export package

**Original actions**

1. representative relationships and selected reports are reconstructed using only the package documentation

**Exact source oracles — all required**

1. the reconstruction succeeds

Legacy same-requirement reuse candidates: `TC-VF-PRT-001`, `TC-AT20`, `SEC-040`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_report_exports.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-PRT-001-003 — Larger exports show an estimate and progress

Source persona: Organisation Administrator. Proposed fixture `FIX-VF-PRT-001-003` is not created. Verification duty `TASK-VF-PRT-001-03` (qualification); source `docs/backlog/backlog.csv` record 116, exact block `02ac23f613e8e13ba7374373cf8a75057cc60afdb067ec3c2aa4358303c42d6f`.

**Original preconditions**

1. a tenant larger than the standard size

**Original actions**

1. an export is requested

**Exact source oracles — all required**

1. a visible estimate and progress are shown

Legacy same-requirement reuse candidates: `TC-VF-PRT-001`, `TC-AT20`, `SEC-040`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_report_exports.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-PRT-001-004 — Reject a collection of unlabelled files

Source persona: Organisation Administrator. Proposed fixture `FIX-VF-PRT-001-004` is not created. Verification duty `TASK-VF-PRT-001-03` (qualification); source `docs/backlog/backlog.csv` record 116, exact block `46bd5caed4d424d849e96f166f4cfd286d125d92b00684d8b5e902ab2ab0508d`.

**Original preconditions**

1. an export made up of unlabelled CSV files

**Original actions**

1. it is assessed

**Exact source oracles — all required**

1. it is not accepted as a complete tenant export

Legacy same-requirement reuse candidates: `TC-VF-PRT-001`, `TC-AT20`, `SEC-040`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_report_exports.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
