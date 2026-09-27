# Release 0.6.0 — frozen internal reporting packages

Build 0.6.0 · API 1.7.0 · additive migration 0009 · 26 September 2026.

## Delivered behavior

The Reports workspace now creates internal drafts from an approved report template, a locked snapshot and an official result revision contained in that snapshot. Draft validation rejects public audiences, incompatible unit/precision bindings, evidence outside the snapshot and result revisions outside the snapshot. Submission requires all package fields, required template sections and required numeric binding codes.

Submission creates an immutable workflow candidate. Independent approval re-runs reconciliation and freezes a new approved Report revision. The same transaction writes an append-only package binding containing exact report, snapshot and template revisions plus a SHA-256 reconciliation digest. Returned and rejected candidates do not create a package binding.

Approved packages expose an authenticated deterministic HTML export. Rendering loads only pinned revisions, verifies the stored digest, HTML-escapes all author text, labels the artifact INTERNAL and APPROVED, renders official displayed values with units, and includes report/snapshot revision context and the reconciliation digest. Live source corrections and later snapshots cannot silently change an older export.

## Architecture and security delta

- `reporting_contracts.py` activates report submission and defines the authenticated export operation.
- `reporting.py` performs snapshot/template/result/evidence reconciliation, approval binding and deterministic rendering.
- Migration 0009 adds `report_package_binding` with forced RLS and SELECT/INSERT-only application authority.
- The generic review pipeline now accepts Report candidates while retaining exact candidate revision, current authority and natural-person independence checks.
- Report templates are part of the implemented read surface. The browser filters selectable results to OFFICIAL revisions in the selected snapshot; server checks remain authoritative.
- The export is served with the application CSP, `nosniff`, no-store policy, an ETag and an inline safe filename. It performs current authentication and object-scope authorization on every request.

## Qualification and limits

Four focused live cases cover approval/binding, deterministic escaped export, incomplete-package rejection, unit/precision mismatch, template requirements, internal-only audience, unapproved export denial, missing-resource behavior and cross-tenant isolation. Six Chromium scenarios cover the programme-period status screen, report drafting, submission, independent approval, rendered export and 390-pixel layout.

This release does not claim public publication. Disclosure review, recipient policy, redaction, expiry, link/download control, withdrawal, correction notices, PDF/DOCX/CSV generation, charts, narrative-number extraction, signatures and delivery tracking remain open. The HTML artifact is an authenticated internal export, not an accessible-publication certification.
