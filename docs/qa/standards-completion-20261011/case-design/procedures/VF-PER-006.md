## QA v1.3 — source-bound case design (proposed)

Story `VF-PER-006` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-VF-PER-006-001` / `TC-IMPRANA-VF-PER-006-001` | `REV_dffd6be6e81ee6476f974dcc6e5839aef98efca61bd061c368bd4fe6aff64ef8` / `REV_a791ade27fdaa21d45a6ba2ab11351a91d98187f793072050bd0f1fc72d0f6e6` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-PER-006-002` / `TC-IMPRANA-VF-PER-006-002` | `REV_68bc53dc0b714d44aebd3516ee12e1e7addeab3a3b239bc7248d1f177a41749e` / `REV_b7723a45713e0f0de5a6b12f7cbe7bcdfa2f80f5c7f5b985673c68b98009e1bb` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-PER-006-003` / `TC-IMPRANA-VF-PER-006-003` | `REV_fe27887b94244b5ba87a9b59de15d30cec29118ecdec40a811ef934ffdbdc72f` / `REV_ed3ea17e6ea691d6b7d55ba763b6241db6f007e94fdc5cac331da820ec27a793` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-VF-PER-006-001 — Dashboard reflects a new approved result within 60 seconds at p95

Source persona: Programme Manager. Proposed fixture `FIX-VF-PER-006-001` is not created. Verification duty `TASK-VF-PER-006-03` (qualification); source `docs/backlog/backlog.csv` record 115, exact block `dffd6be6e81ee6476f974dcc6e5839aef98efca61bd061c368bd4fe6aff64ef8`.

**Original preconditions**

1. a submission has been approved
2. its bounded calculation has finished

**Original actions**

1. the Programme Manager views the live dashboard

**Exact source oracles — all required**

1. the new approved result is shown within 60 seconds at p95 of calculation completion
2. version identifiers prove the new result is the one displayed

Legacy same-requirement reuse candidates: `TC-VF-PER-006`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_concurrency.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-PER-006-002 — Collection and review delays are shown separately

Source persona: Programme Manager. Proposed fixture `FIX-VF-PER-006-002` is not created. Verification duty `TASK-VF-PER-006-03` (qualification); source `docs/backlog/backlog.csv` record 115, exact block `68bc53dc0b714d44aebd3516ee12e1e7addeab3a3b239bc7248d1f177a41749e`.

**Original preconditions**

1. source receipt, validation, approval and calculation completion times are recorded

**Original actions**

1. data freshness is reported

**Exact source oracles — all required**

1. external source cadence and human review delay are displayed separately from the 60-second propagation metric

Legacy same-requirement reuse candidates: `TC-VF-PER-006`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_concurrency.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-PER-006-003 — Reject hidden delays or slow propagation

Source persona: Programme Manager. Proposed fixture `FIX-VF-PER-006-003` is not created. Verification duty `TASK-VF-PER-006-03` (qualification); source `docs/backlog/backlog.csv` record 115, exact block `fe27887b94244b5ba87a9b59de15d30cec29118ecdec40a811ef934ffdbdc72f`.

**Original preconditions**

1. a data freshness measurement

**Original actions**

1. collection or human review delay is hidden inside the propagation metric

**Exact source oracles — all required**

1. the measurement is rejected
2. propagation taking longer than 60 seconds at p95 from calculation completion fails the target

Legacy same-requirement reuse candidates: `TC-VF-PER-006`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_concurrency.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
