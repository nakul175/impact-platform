# Release 0.8.0 — controlled report publication

Build 0.8.0 · API 1.9.0 · additive migration 0011 · 26 September 2026.

This increment extends an independently approved, snapshot-bound internal report into a controlled publication for named active workspace members. The disclosure itself requires independent review, is pinned to one immutable report revision, expires within 90 days, and can be withdrawn without erasing the frozen artifacts or access history. Publication creates deterministic semantic HTML and CSV artifacts transactionally; the CSV can be disabled per recipient.

This is a development release, not a complete enterprise product or production certification. Anonymous/public links, external-recipient identity, provider delivery, schedules, signatures, charts, PDF/DOCX/XLSX, public search indexing, correction notices and production infrastructure remain open.

## Delivered behaviour

### Numeric narrative reconciliation

- Report narrative can refer to an approved numeric result only with a `{{binding_code}}` placeholder declared in that section.
- Submission rejects an unknown placeholder and rejects an otherwise bare numeric claim. This prevents an author from typing a number that is not reconciled to a pinned result revision.
- Rendering replaces each valid placeholder from the exact approved package. User-authored text is escaped before output.
- This is a bounded numeric-claim control, not semantic fact checking. Dates, words, qualitative claims, chart annotations and external facts are not automatically verified.

### Disclosure request and review

- A request starts only from the current approved revision of a frozen report package.
- The disclosure is always controlled (`public=false`). The contract deliberately has no anonymous-link or open-publication mode.
- The requester selects a declared purpose (`FUNDER_REPORTING`, `PARTNER_REPORTING` or `INTERNAL_OVERSIGHT`), a UTC expiry in the future and no more than 90 days away, and one to 100 unique active tenant memberships.
- Every recipient carries an explicit `allow_download` decision. HTML view permission does not imply CSV download permission.
- The recipient selector exposes a bounded, masked directory. It does not return email addresses or create external identities.
- Submission creates an immutable `Disclosure` candidate and an independent workflow for the exact report revision. The report author/requester cannot satisfy natural-person independence by using another membership.
- Review uses the ordinary exact-candidate controls: current reviewer eligibility, `report.publish`, `workflow.approve`, `disclosures.read`, tenant scope, candidate revision, decision idempotency and immutable decision records are rechecked by the server.

### Publication and recipient access

- Publication requires the approved disclosure head, the same approved report revision, a current eligible publisher and fresh authentication. It revalidates the expiry and every recipient before creating artifacts.
- HTML and CSV are generated from the same reconciled report package in one transaction. Each artifact records the report revision, disclosure revision, media type, bytes, SHA-256 digest and creation time.
- HTML uses semantic headings and tables. Content is escaped and numeric placeholders are rendered as bound values with machine-readable binding identifiers.
- Report HTML carries a dedicated content-security policy that permits only the exact SHA-256-pinned static stylesheet; scripts and all other resource types remain blocked.
- CSV is deterministic, uses a fixed column order, and protects text cells that could otherwise be interpreted as spreadsheet formulas. Numeric values remain decimal data rather than author-controlled formulas.
- Recipient access is authenticated and bound to the current active membership named by the approved disclosure. Cross-tenant, unlisted, expired and withdrawn access all return the ordinary unavailable response.
- Every successful view or download appends a separate access record with recipient membership, principal, mode, timestamp and correlation identifier.
- The application database role can insert but cannot read, update or delete access-log rows. It can read and insert artifact rows but cannot update or delete them.

### Withdrawal

- A current publisher can withdraw every active publication for the exact report revision with a required reason and fresh authentication.
- Withdrawal records the timestamp and reason on a new disclosure revision and immediately makes the recipient routes unavailable.
- Frozen artifact bytes, their digests, prior report revisions, workflow decisions and recipient-access events are retained. Withdrawal is a state change, not deletion.
- This increment does not send a withdrawal or correction notice to prior recipients and does not create an explicit supersession chain between separately published reports.

## Data and API changes

Migration `0011_controlled_publication.sql`:

- adds `published_at`, `withdrawn_at` and `withdrawal_reason` to the disclosure projection;
- adds immutable `impact.report_publication_artifact` rows for HTML and CSV, limited to five MiB per body;
- adds append-only `impact.report_publication_access` rows for successful VIEW and DOWNLOAD events;
- enables and forces tenant row-level security on both new tables;
- grants the application role only the minimum artifact and access-log operations used by this release.

API 1.9.0 adds nine implemented domain operations:

| Method | Route | Capability |
|---|---|---|
| POST | `/v1/tenants/{tenant_id}/disclosure-requests` | `disclosure.request` |
| GET | `/v1/tenants/{tenant_id}/disclosures` | `disclosures.read` |
| GET | `/v1/tenants/{tenant_id}/disclosures/{object_id}` | `disclosures.read` |
| GET | `/v1/tenants/{tenant_id}/publication-recipients` | `disclosure.request` |
| POST | `/v1/tenants/{tenant_id}/reports/{object_id}/actions/publish` | `report.publish` |
| POST | `/v1/tenants/{tenant_id}/reports/{object_id}/actions/withdraw` | `report.withdraw` |
| GET | `/v1/tenants/{tenant_id}/reports/{object_id}/export.csv` | `reports.read` |
| GET | `/v1/tenants/{tenant_id}/publications/{object_id}/view` | `publication.download` |
| GET | `/v1/tenants/{tenant_id}/publications/{object_id}/download.csv` | `publication.download` |

The implemented domain surface now contains 115 operations. The broader design OpenAPI remains intentionally larger and is not an implementation claim.

## Security and transaction rules

- Publication and withdrawal are derived-scope operations. A narrowly scoped publisher cannot use an object grant to create tenant-wide recipient exposure.
- Disclosure state transitions and artifact creation use the existing tenant advisory lock, optimistic revision checks, audit/outbox records and actor-owned operation receipts.
- Approval never substitutes for publication authority. The publishing actor's current capability, membership, grant expiry, scope and recent-authentication evidence are checked again when effects are created.
- Recipient access uses server-resolved current membership and principal identity. A disclosure identifier alone is not a bearer secret.
- Publication endpoints deliberately hide whether a disclosure exists when the caller is not a current eligible recipient.
- Withdrawal does not remove access evidence. Direct application-role attempts to update an artifact or read the protected access log are denied by PostgreSQL privileges in qualification.
- No raw invitation secret, password, email address or bearer token is embedded in a publication artifact or access record.

## Qualification evidence

The final local gate passed:

- 224 application unit, contract, integration, security and smoke checks; one preserved offline-sync test remains explicitly deselected;
- 143 preserved reference assertions;
- 47 Chromium workflows: eight core, 12 access-administration, 17 measurement/change/work-centre, and ten period/reporting/publication workflows;
- Ruff lint/format, Prettier, TypeScript and Vite production build;
- fresh-database application of all 11 migrations;
- narrative placeholder, unknown-placeholder and bare-number checks;
- self-approval denial, exact disclosure revision review, recipient-only view/download, per-recipient download denial, expiry/duplicate/inactive-recipient denial, withdrawal and preserved-history checks;
- forced-RLS cross-tenant denial and direct database privilege tests for immutable artifacts and write-only access logging;
- rendered 390-pixel reporting workspace with no document overflow or uncaught page errors.

Primary evidence is in `qualification/test_publication.py`, `qualification/test_reporting.py`, `tools/browser/reporting-check.mjs`, `docs/evidence/publication-preview.png`, `docs/evidence/controlled-publication.png` and the machine-readable records under `docs/evidence`.

## Explicit limits

- Publication recipients must already be active members of the same workspace. There is no external-contact directory, recipient invitation, federated guest flow or public audience.
- HTML and CSV are implemented. PDF, PDF/UA qualification, DOCX, XLSX, chart rendering, digital signatures and donor-specific layout packs are not.
- There is no provider delivery, email/SMS/push, scheduled distribution, bounce tracking, download quota, watermarking or expiring bearer link.
- Access records represent successful application-mediated access. This is not a qualified tamper-evident audit archive, SIEM export or proof that a recipient did not copy content after access.
- Withdrawal blocks future application access but cannot recall bytes already downloaded.
- Narrative reconciliation recognizes bounded numeric tokens and declared placeholders. It does not validate the truth of prose or data outside the frozen report package.
- PGlite qualification does not establish native PostgreSQL concurrency, production throughput, backup/recovery, external identity or accessibility conformance.

These limits remain release gates in `NEXT-DELIVERY.md`; the conservative completion ledger marks only bounded tested behaviour as partial.
