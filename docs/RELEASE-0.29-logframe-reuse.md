# v0.29 — approved logframe spreadsheet exports from TolaData reuse

Proposed local build 0.29.0 · schema 33 unchanged · domain API 1.19.0 (232 operations) ·
platform API 1.9.0 unchanged · 113 PARTIAL / 194 PENDING / 0 accepted unchanged.
Branch `release/0.29-logframe-reuse`, based on main `5676e02`. Not merged or deployed.

## Delivered

The Results framework screen offers **Download logframe CSV** and **Download logframe Excel**
for a selected programme's approved baseline, only to people with `framework.export`.
The exact approved revision is in the request and export context; an approved successor does not
change the earlier export. The workbook has Context, Logframe, Relationships, Assumptions and
Exceptions sheets. CSV preserves the same sections in a tagged rectangular table.

Hierarchy traversal places parents before children while retaining authored sibling order. Empty
frameworks remain exportable. The export carries definitions, placed indicator identifiers, owners,
theory-of-change links, risks/assumptions and documented exceptions. It intentionally contains no
current indicator names, targets, baselines, observations or actuals that could silently change the
meaning of an earlier approved framework.

Mercy Corps reuse: header styling is adapted from `indicators/xls_export_utils.py` at
`7ca89ab1e5f55cbe4577d16d7281c6cf0936fc3d`; hierarchy, empty-data and Unicode tests draw on its
framework-export scenarios. The full Apache 2.0 license and source/modification notice are under
`third_party/mercycorps-toladata`. Its Django models, permissions, calculation rules and legacy
merged-cell workaround are not imported. See `handover/MERCYCORPS-REUSE.md` for the comparison.

## Contract and persistence

Two implemented GET operations:

- `/v1/tenants/{tenant_id}/frameworks/{object_id}/logframe.csv?revision_id=<uuid>`
- `/v1/tenants/{tenant_id}/frameworks/{object_id}/logframe.xlsx?revision_id=<uuid>`

Both require separate `framework.export` authority, current `frameworks.read`, a matching approved
revision in the insert-only `framework_baseline` register, `programmes.read` and read visibility
for every placed indicator. A revision belonging to another framework and a hidden source both
return the normal unavailable 404. An unapproved revision returns 409
`APPROVED_FRAMEWORK_REQUIRED`. Every successful export records an AuditEvent plus outbox event
in the same tenant-locked transaction. The request correlation identifies the audit event.

No migration or new table. CSV and XLSX bytes are deterministic for identical content and pinned
library versions. XLSX metadata and ZIP timestamps are fixed; text cells cannot execute formulas.
CSV guards formula prefixes even after whitespace, controls or a BOM. XML-illegal control characters
are refused for XLSX with `LOGFRAME_TEXT_NOT_SUPPORTED`, rather than silently removed. The existing
500-node definition limit and an explicit 10 MiB artifact ceiling bound synchronous rendering.

The generated onboarding profile gains `framework.export` for MEL_ADMIN, PROGRAMME_MANAGER and
ANALYST. A new profile hash invalidates pending requests pinned to the previous profile, requiring
re-proposal. Existing tenant ceilings do not widen automatically: their reviewed grant/ceiling
process remains a prerequisite to assigning the new capability. This release does not weaken it.

## Limits

This is the export part of backlog slice 5, not an indicator library or standard-mapping feature.
It is an approved framework structure export, not an official indicator performance report.
Only CSV and XLSX, no PDF. Artifacts are generated on download, not persisted or published to
external recipients. Audit records authorization and generation, not proof of receipt by a person.
Repeated GET downloads have identical bytes but separate access audits; they are not command retries.

Local test results are in QUALIFICATION.md. Browser download assertions have been added to the
planning browser group; the repository's browser runner needs Linux x86_64 and has not run on this
macOS host. Native PostgreSQL, live identity-provider and container-stack CI must still qualify
the proposed branch. No requirements are accepted and no production readiness is inferred.

## Reproduction

```sh
make lint
IMPACT_PORT=8137 .venv/bin/python scripts/run.py test --pytest-path qualification/test_logframe.py --pytest-path qualification/test_planning.py --pytest-path qualification/test_usable_staging_unit.py --pytest-path qualification/test_version_unit.py
make test
make browser     # Linux x86_64
```

## Integration notes

New module: `apps/api/impact_api/logframe.py`; route registration in `main.py`; contract definitions
in `planning_contracts.py`; profile/fixture provisioning; Planning screen download links; browser
download check; `qualification/test_logframe.py`; attribution/license. Build/domain API bumps and
regenerated contracts are included; schema and platform API are unchanged.

The named local cases cover hierarchy ordering, invalid structures, Unicode, formulas, deterministic
bytes, blank/deep frameworks, control-character refusal, approved version pinning after a successor,
revision mismatch, audit, read without export authority, hidden indicators and foreign/revoked actors.
Native-only planning register checks remain separate. Ledger status remains unchanged; evidence is
additional bounded coverage for FR-PLN-001, not acceptance of its complete requirement.

Before merging, obtain all four green CI jobs and the owner's confirmation as required by AGENTS.md.
Opening a pull request triggers paid CI and therefore also requires owner confirmation here.
