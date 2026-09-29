"""Conservative requirement ledger; API presence alone never qualifies a requirement."""

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
catalogue = json.loads((ROOT / "specification/contracts/fsd-requirements.json").read_text())
groups = [
    (
        "FR-TEN-001",
        "v0.10–0.13 implement operator-requested profiles, owner acceptance, independent activation, readiness/impact checks, access fencing and durable work holds. Initial access now requires an owner proposal, separate administrator acceptance and independent operator approval of fixed capability/expiry ceilings; business grants still require separate review. Recovery-contact nomination, registered-account/MFA verification, independent approval, replacement/renewal, revocation and current eligibility now gate activation/reactivation. v0.13 adds reviewed renewal/extension of unexpired delegated authority: the owner pins the exact current ceilings, grants and administrative assignments of both administrators, the second administrator accepts, an independent operator approves within 7 days and within 90 days of expiry, and a database-owned applicator re-dates only the pinned rows. Limits: expired authority is not renewable, tenants without exactly one second administrator are unsupported, and renewal requires current readiness including recovery-contact evidence. Partial: external channel verification/invitations, unavailable-owner recovery, support/exit access, workers, credential rechecks and archival/deletion remain open; native concurrency evidence is limited to the renewal-approval-versus-grant-revocation race in qualification/test_native_concurrency.py (v0.14).",
        [
            "apps/api/impact_api/tenant_lifecycle.py",
            "qualification/test_tenant_lifecycle.py",
            "tools/browser/tenant-check.mjs",
            "docs/RELEASE-0.10.md",
            "apps/api/impact_api/access_bootstrap.py",
            "qualification/test_access_bootstrap.py",
            "tools/browser/bootstrap-check.mjs",
            "docs/RELEASE-0.11.md",
            "apps/api/impact_api/recovery_contacts.py",
            "qualification/test_recovery_contacts.py",
            "tools/browser/recovery-check.mjs",
            "docs/RELEASE-0.12.md",
            "apps/api/impact_api/authority_renewal.py",
            "qualification/test_authority_renewal.py",
            "tools/browser/renewal-check.mjs",
            "docs/RELEASE-0.13.md",
            "qualification/test_native_concurrency.py",
        ],
    ),
    (
        "FR-IAM-009",
        "Provisioned-identity invitations, membership changes, independent role approval, suspension and revocation are implemented. v0.13 adds reviewed renewal/extension of unexpired delegated authority within the existing ceilings: owner proposal, second-administrator consent and independent operator approval, with no capability widening and no resurrection of revoked grants. v0.15 (#19) narrows what is delegable to capabilities of the 138 implemented operations (84 capabilities): a custom role naming a design-only capability is refused with CAPABILITY_NOT_DELEGABLE at create and at revise even when the creator holds a delegation ceiling for it (test_workspace_administration.py::test_custom_roles_delegate_only_implemented_capabilities), and the orphan create_organisation_units policy row is gone. Custom roles created before v0.15 are not re-checked. Federation assurance, recovery, all identity providers, renewal of expired authority, administrator replacement and full departure inventory are not qualified.",
        [
            "apps/api/impact_api/administration.py",
            "qualification/test_administration.py",
            "docs/RELEASE-0.2.md",
            "apps/api/impact_api/authority_renewal.py",
            "qualification/test_authority_renewal.py",
            "tools/browser/renewal-check.mjs",
            "docs/RELEASE-0.13.md",
            "apps/api/impact_api/contracts.py",
            "apps/api/impact_api/workspace_administration.py",
            "qualification/test_workspace_administration.py",
            "docs/RELEASE-0.15.md",
        ],
    ),
    (
        "FR-TEN-003 FR-IAM-001 FR-IAM-002 FR-IAM-006 FR-IAM-008 FR-IAM-013 FR-IAM-014 FR-ACC-003 FR-ACC-006 FR-ACC-012",
        "Provisioned-identity invitations, membership changes, independent role approval, suspension and revocation are implemented. Federation assurance, recovery, all identity providers and full departure inventory are not qualified.",
        [
            "apps/api/impact_api/administration.py",
            "qualification/test_administration.py",
            "docs/RELEASE-0.2.md",
        ],
    ),
    (
        "FR-ACC-001 FR-ACC-002 FR-ACC-004 FR-ACC-005 FR-ACC-011 FR-SEC-004 FR-SEC-007 FR-SEC-012 FR-INT-004 FR-INT-005",
        "Implemented routes enforce explicit grants, tenant fences, natural-person independence, revisions and retry receipts. Native concurrency evidence is limited to the raced approvals, operation replays, close reviews and renewal-versus-revocation cases of qualification/test_native_concurrency.py (v0.14); every future module, audit tamper evidence and production assurance remain open.",
        [
            "apps/api/impact_api/store.py",
            "apps/api/impact_api/auth.py",
            "qualification/test_live_application.py",
        ],
    ),
    (
        "FR-SEC-003",
        "Implemented routes enforce explicit grants, tenant fences, natural-person independence, revisions and retry receipts. v0.14 adds native PostgreSQL evidence for the database side of the fence: the API runs on three separately provisioned login roles (impact_app_login, impact_identity_login, impact_platform_login; NOINHERIT, NOBYPASSRLS, exactly one privilege-role membership each) with IMPACT_REQUIRE_UNPRIVILEGED_DB=1, and qualification/test_native_roles.py proves under those real logins (PostgreSQL 16.13 locally, 17.11 in CI) that each login assumes only its own role, that impact_app reads nothing without a transaction-local tenant and exactly one tenant with one, that it cannot read the control-plane tables, that impact_identity reaches identity tables only, that impact_platform writes only its RESTRICTIVE object types, and that the runtime guard refuses superuser, BYPASSRLS, owner-member and shared logins on every transaction (PRIVILEGED_RUNTIME_CONNECTION, SHARED_RUNTIME_LOGIN) with no login name in any response. The restore drill re-verifies ownership, RLS, policies, grants and the fences on a restored copy. Not covered: attachments, asynchronous jobs, caches, search, AI and support paths (none exist), connection pooling and context reset on pooled connections, audit tamper evidence, an isolation fixture with synthetic tenant markers across every module, and production assurance.",
        [
            "apps/api/impact_api/store.py",
            "apps/api/impact_api/auth.py",
            "qualification/test_live_application.py",
            "scripts/provision_logins.py",
            "qualification/test_native_roles.py",
            "scripts/restore_drill.py",
            "docs/evidence/native-application-tests.xml",
            "docs/evidence/native-qualification.json",
            "docs/RELEASE-0.14.md",
        ],
    ),
    (
        "FR-PLN-006 FR-PRG-001 FR-PRG-005 FR-PRG-006 FR-PRG-007 FR-IND-001 FR-IND-002 FR-IND-005 FR-IND-007 FR-IND-008 FR-IND-009 FR-IND-010 FR-IND-012 FR-DQ-006",
        "Manual FLOW measures, independently approved definitions/plans, reviewed obligation exceptions, eligible assignments, reference selection and programme readiness are implemented. Historical expected, required and excepted counts are preserved. Rich planning, reference administration, automated schedules and the other measurement profiles remain open.",
        ["apps/api/impact_api/measurement.py", "qualification/test_work_center.py", "docs/RELEASE-0.7.md"],
    ),
    (
        "FR-CAL-001 FR-CAL-002 FR-CAL-003 FR-CAL-005 FR-CAL-008 FR-CAL-009 FR-CAL-010 FR-CAL-015 FR-DAT-008 FR-ANA-004",
        "Decimal SUM and pooled ratios, revision-bound lineage, explicit contributor coverage and stale-result flags are implemented. Hierarchy, stock, overlap, weighting, dimensions and production workload qualification are not implemented.",
        [
            "apps/api/impact_api/domain.py",
            "apps/api/impact_api/service.py",
            "qualification/test_measurement.py",
        ],
    ),
    (
        "FR-CAL-011 FR-DAT-009 FR-WFL-001 FR-WFL-002 FR-WFL-003 FR-WFL-004 FR-WFL-010",
        "Single-stage independent review and governed source/plan/assignment amendments are implemented. Affected provisional result revisions receive durable invalidations and personal recalculation work; current approved inputs produce a replacement revision while old lineage remains immutable. Cross-period aggregates, dashboards, reports, distributed artifacts, bulk amendments, configurable multistage policies and escalation remain open.",
        ["apps/api/impact_api/work.py", "qualification/test_work_center.py", "docs/RELEASE-0.7.md"],
    ),
    (
        "FR-WFL-006",
        "A personal work centre implements deduplicated recalculation assignments and safe in-app notices with event identity, acknowledgement and exact-retry protection. Due obligations, returned work, preferences, digests, provider delivery attempts and escalations remain open.",
        ["apps/api/impact_api/work.py", "apps/web/src/WorkCenter.tsx", "docs/RELEASE-0.7.md"],
    ),
    (
        "FR-WFL-007 FR-WFL-008",
        "Programme-period close previews pin plans, sources and provisional results; independently reviewed exclusions remain visible but do not block required completion. Approval creates official results and an immutable versioned snapshot. Scoped, time-bounded restatement preserves and supersedes the original. Optional-late-source policy, distributed-artifact impact and multi-period downstream regeneration remain open.",
        [
            "apps/api/impact_api/period_governance.py",
            "qualification/test_period_governance.py",
            "docs/RELEASE-0.5.md",
        ],
    ),
    (
        "FR-RPT-003 FR-RPT-005 FR-RPT-007 FR-RPT-009 FR-RPT-010",
        "Internal reports bind to a locked snapshot, approved template and official result/evidence revisions. Independent approval records an append-only reconciliation digest. Numeric narrative claims must use known binding placeholders; deterministic semantic HTML and CSV artifacts are frozen for an independently reviewed, named-recipient, expiring disclosure and every view/download is logged. Withdrawal closes access without deleting artifacts or history. Charts, PDF/DOCX/XLSX, anonymous publication, delivery, supersession notices and distributed-artifact handling remain open.",
        [
            "apps/api/impact_api/reporting.py",
            "qualification/test_reporting.py",
            "qualification/test_publication.py",
            "docs/RELEASE-0.6.md",
            "docs/RELEASE-0.8.md",
        ],
    ),
    (
        "FR-RPT-004 FR-UX-001 FR-UX-002 FR-UX-003 FR-UX-004 FR-UX-005 FR-UX-009",
        "Browser workspaces, labelled dialogs, bound narrative authoring, controlled-publication actions, explicit status and health endpoints are implemented. Full accessibility/usability qualification, anonymous publication, service monitoring and all remaining screens are open.",
        ["apps/web/src/main.tsx", "tools/browser/reporting-check.mjs", "docs/IMPLEMENTATION.md"],
    ),
    (
        "FR-OPS-005",
        "Browser workspaces, labelled dialogs, bound narrative authoring, controlled-publication actions, explicit status and health endpoints are implemented. v0.14 adds to the health surface: with unprivileged connections required, /health/ready first verifies that the app, identity and platform connections are three distinct unprivileged logins and answers 503 with a reason code only (PRIVILEGED_RUNTIME_CONNECTION, SHARED_RUNTIME_LOGIN, PLATFORM_NOT_CONFIGURED; no login name reaches a response), the same check refuses every transaction, and the native restart check shows readiness and the runtime manifest unchanged across an API restart. Service monitoring proper remains open: no health view separated by component, no journey success, latency, backlog, freshness or quota measurement, no incident record, no tenant-cohort view, no metrics, log pipeline or alerting exists; full accessibility/usability qualification, anonymous publication and all remaining screens are also open.",
        [
            "apps/web/src/main.tsx",
            "tools/browser/reporting-check.mjs",
            "docs/IMPLEMENTATION.md",
            "apps/api/impact_api/main.py",
            "apps/api/impact_api/store.py",
            "qualification/test_native_roles.py",
            "qualification/test_native_restart.py",
            "docs/evidence/native-qualification.json",
            "docs/RELEASE-0.14.md",
        ],
    ),
    (
        "VF-DIN-002",
        "Native PostgreSQL only (qualification/test_native_concurrency.py, 11 cases, executed on PostgreSQL 16.13 in the workspace on 29 September 2026 and 17.11 in CI; skipped on PGlite, whose single process lock cannot contend): two independent reviewers approving one candidate revision at once admit exactly one decision (200 and CONFLICT_VERSION; one new revision each of candidate and workflow, one audit event, one outbox event, one receipt); the same command from two threads returns the one receipt and writes one revision; the same operation identifier with different payloads admits exactly one (CONFLICT_OPERATION for the other); two independent close reviews of one period produce one OFFICIAL snapshot version and PERIOD_ALREADY_SNAPSHOTTED for the other; a renewal approval raced with a pinned-grant revocation in both orders yields either the renewed set with the stale revocation refused (CONFLICT_VERSION) or the revoked grant with the approval refused (AUTHORITY_CHANGED), never both; ten reads complete beside a held tenant advisory lock while a write queues, and a write held past lock_timeout is refused with no receipt. Not covered: two concurrent edits of one record, repeated import commands and interrupted bulk jobs (no import or bulk job exists), the LLD lock order across objects under concurrent writers (the mixed-write case is a no-regression smoke test), connection pooling, and any load profile. The target's recoverable explicit partial outcomes exist only where an operation defines them.",
        [
            "qualification/test_native_concurrency.py",
            "apps/api/impact_api/service.py",
            "apps/api/impact_api/store.py",
            "docs/evidence/native-application-tests.xml",
            "docs/evidence/native-qualification.json",
            "docs/RELEASE-0.14.md",
        ],
    ),
    (
        "VF-DR-003",
        "A scripted, verified restore exists and has been executed (scripts/restore_drill.py; 29 September 2026 on PostgreSQL 16.13, and in the CI native job on 17.11 for commit c759e9e): pg_dump -Fc of the qualification database (3,427,234 bytes in 0.45 s), pg_restore into a sibling database (1.56 s), a migrator checksum pass that applies nothing and verifies all 16 ledgered checksums, the seeded OFFICIAL 46.36 present in its snapshot revision with its payload hash, equal row counts in all 151 impact tables (30,016 rows), identical ownership, RLS flags, policies, functions and grants, the tenant fences and control-plane denials intact for impact_app, and no credential altered. This is a CI-scale restore drill of a disposable qualification database, not a backup regime: no scheduled backup, retention window, off-site or immutable copy, protection against alteration or credential compromise, monthly restore cadence, quarterly disaster exercise, key recovery, attachment integrity (no attachments exist) or deletion/restriction replay before reopening exists, and no RPO or RTO is established. A restore of a production-scale database is not qualified.",
        [
            "scripts/restore_drill.py",
            "docs/evidence/native-restore-drill.json",
            "docs/evidence/native-qualification.json",
            "docs/RELEASE-0.14.md",
            "docs/current/OPERATIONS-GUIDE.md",
        ],
    ),
    (
        "FR-TEN-002 FR-TEN-010 FR-IAM-003 FR-IAM-006 FR-IAM-008 FR-IAM-010 FR-IAM-013 FR-ACC-002",
        "v0.9 adds versioned custom roles, independently reviewed flat group access, immediate organisation moves with cycle checks, renewal without old-access resurrection, nominated custody transfer, self-service session revocation/preferences and configured ACR enforcement. v0.13 adds reviewed renewal/extension of unexpired delegated authority (owner proposal pinning the exact current ceilings, second-administrator acceptance, independent operator approval, database-owned re-dating of only the pinned rows); expired authority is not renewable and single-administrator tenants are unsupported. Further onboarding acceptance, provider MFA/recovery qualification, action-bound step-up, future-effective organisation impact and full access certification remain open.",
        [
            "apps/api/impact_api/workspace_administration.py",
            "apps/api/impact_api/account.py",
            "qualification/test_workspace_administration.py",
            "tools/browser/workspace-check.mjs",
            "docs/RELEASE-0.9.md",
            "apps/api/impact_api/authority_renewal.py",
            "qualification/test_authority_renewal.py",
            "tools/browser/renewal-check.mjs",
            "docs/RELEASE-0.13.md",
        ],
    ),
    (
        "FR-IAM-002",
        "Provisioned-identity invitations, membership changes, independent role approval, suspension and revocation are implemented. v0.15 qualifies the login binding against a live provider (Keycloak 26.7.4, development mode, in-memory database, qualification/test_live_idp.py: 16 cases on PGlite and 16 on native PostgreSQL 16.13 login roles, 29 September 2026): sign-in binds the provider issuer and stable subject to the fixture identity (the fixture's auth_identity rows are re-pointed to the realm issuer by subject); tokens of another issuer (a second realm with the same client and a user carrying the same subject), a tampered signature, a key outside the provider JWKS, an expired token, an ID token presented as a bearer credential (typ check) and provider role claims are refused or confer nothing; a disabled provider account cannot sign in; missing assurance fails safely (a password-only session is refused every fresh-assurance operation). Not covered: an administrator-facing provider configuration, tenant binding and designated-account test mode, certificate or key expiry display and overlapping rotation, provider interruption, emergency local recovery, SAML or any provider other than one Keycloak realm, and a managed or customer-provided provider.",
        [
            "apps/api/impact_api/administration.py",
            "qualification/test_administration.py",
            "docs/RELEASE-0.2.md",
            "apps/api/impact_api/auth.py",
            "scripts/idp.py",
            "tools/idp/qualification-realm.json",
            "qualification/test_live_idp.py",
            "docs/evidence/idp-tests.xml",
            "docs/evidence/idp-native-tests.xml",
            "docs/evidence/idp-qualification.json",
            "docs/RELEASE-0.15.md",
        ],
    ),
    (
        "FR-IAM-003",
        "v0.9 adds versioned custom roles, independently reviewed flat group access, immediate organisation moves with cycle checks, renewal without old-access resurrection, nominated custody transfer, self-service session revocation/preferences and configured ACR enforcement. v0.13 adds reviewed renewal/extension of unexpired delegated authority (owner proposal pinning the exact current ceilings, second-administrator acceptance, independent operator approval, database-owned re-dating of only the pinned rows); expired authority is not renewable and single-administrator tenants are unsupported. v0.15 exercises step-up against a live provider: the qualification realm's browser flow is level 1 password and level 2 TOTP with an ACR map, the platform requests urn:impact:acr:mfa with max_age=0, a session at the password level reads normally but is refused every tenant and account fresh-assurance operation, a user without a second factor is sent to TOTP enrolment before any code is issued, and after TOTP a fresh-assurance operation succeeds until 300 s after the provider's own auth_time (FRESH_AUTHENTICATION_REQUIRED at 301 s, emulated by moving the recorded auth_time back) in qualification/test_live_idp.py and the idp-browser check. Not covered: completion of enrolment, passkeys, a challenge bound to the intended action (step-up is per session, not per pending action), blocking removal of the last qualifying factor, SMS exclusion, authenticator synchronisation disclosure and provider-side recovery.",
        [
            "apps/api/impact_api/workspace_administration.py",
            "apps/api/impact_api/account.py",
            "qualification/test_workspace_administration.py",
            "tools/browser/workspace-check.mjs",
            "docs/RELEASE-0.9.md",
            "apps/api/impact_api/authority_renewal.py",
            "qualification/test_authority_renewal.py",
            "tools/browser/renewal-check.mjs",
            "docs/RELEASE-0.13.md",
            "apps/api/impact_api/auth.py",
            "scripts/idp.py",
            "tools/idp/qualification-realm.json",
            "qualification/test_live_idp.py",
            "docs/evidence/idp-tests.xml",
            "docs/evidence/idp-native-tests.xml",
            "docs/evidence/idp-qualification.json",
            "docs/RELEASE-0.15.md",
            "tools/browser/idp-check.mjs",
            "docs/evidence/idp-browser-tests.json",
        ],
    ),
    (
        "FR-IAM-006",
        "v0.9 adds versioned custom roles, independently reviewed flat group access, immediate organisation moves with cycle checks, renewal without old-access resurrection, nominated custody transfer, self-service session revocation/preferences and configured ACR enforcement. v0.13 adds reviewed renewal/extension of unexpired delegated authority (owner proposal pinning the exact current ceilings, second-administrator acceptance, independent operator approval, database-owned re-dating of only the pinned rows); expired authority is not renewable and single-administrator tenants are unsupported. v0.15 adds live-provider logout (qualification/test_live_idp.py, qualification/test_backchannel_logout.py, idp-browser check): POST /auth/logout revokes the server session at once (the old cookie then gets 401) and returns the provider end-session URL with a sealed id_token_hint, after which the provider session is gone (prompt=none returns login_required); a logout after idle or absolute timeout still clears the cookie; a verified back-channel logout token revokes exactly the platform sessions of that provider session and a replayed token is refused. Server authority is therefore invalidated independently of what the browser still shows. Not covered: clearing in-memory client state and cached navigation, browser back and a queued export from a revoked session (no export job exists), shared-device mode, the idle warning that preserves drafts, and bearer access tokens, which remain valid until exp (120 s in the realm) after a provider logout.",
        [
            "apps/api/impact_api/workspace_administration.py",
            "apps/api/impact_api/account.py",
            "qualification/test_workspace_administration.py",
            "tools/browser/workspace-check.mjs",
            "docs/RELEASE-0.9.md",
            "apps/api/impact_api/authority_renewal.py",
            "qualification/test_authority_renewal.py",
            "tools/browser/renewal-check.mjs",
            "docs/RELEASE-0.13.md",
            "apps/api/impact_api/auth.py",
            "scripts/idp.py",
            "tools/idp/qualification-realm.json",
            "qualification/test_live_idp.py",
            "docs/evidence/idp-tests.xml",
            "docs/evidence/idp-native-tests.xml",
            "docs/evidence/idp-qualification.json",
            "docs/RELEASE-0.15.md",
            "qualification/test_backchannel_logout.py",
            "tools/browser/idp-check.mjs",
            "docs/evidence/idp-browser-tests.json",
        ],
    ),
]
# Requirements that stay PENDING, with what the latest increments do and do not show for them.
pending_notes = {
    "VF-IAM-001": "PENDING. v0.15 revokes browser sessions immediately on logout and on a verified back-channel logout token (qualification/test_live_idp.py, test_backchannel_logout.py), but the 60-second bound is not met or measured: bearer access tokens remain valid until exp (120 s in the qualification realm) after a provider logout, no revocation latency is measured from platform receipt, and suspension, grant removal, service credentials, generated downloads, search, AI and queued jobs are not polled (most of them do not exist). Retain the original acceptance criteria; this requirement remains open.",
}
partial = {key: (description, evidence) for ids, description, evidence in groups for key in ids.split()}
requirements = []
for group in ["functional", "nonfunctional"]:
    for req in catalogue[group]:
        description, evidence = partial.get(
            req["id"],
            (
                pending_notes.get(
                    req["id"],
                    "No complete implementation and acceptance evidence mapped. Retain the original acceptance criteria; this requirement remains open.",
                ),
                [],
            ),
        )
        requirements.append(
            {
                **req,
                "category": group,
                "status": "PARTIAL" if req["id"] in partial else "PENDING",
                "assessment": description,
                "evidence_paths": evidence,
                "release_gate": "Complete the original acceptance criteria and record passing implementation and qualification evidence.",
            }
        )
assert len(requirements) == 307 and len({r["id"] for r in requirements}) == 307
assert set(partial) <= {r["id"] for r in requirements}
assert not set(pending_notes) & set(partial)
for requirement in requirements:
    for path in requirement["evidence_paths"]:
        assert (ROOT / path).is_file(), path
summary = dict(Counter(r["status"] for r in requirements))
result = {
    "build": "0.15.0",
    "assessment_date": "2026-09-29",
    "enterprise_complete": False,
    "method": "PARTIAL means tested behavior exists for a bounded subset; PENDING does not imply that a scaffold or design contract is an implementation. No enterprise acceptance is inferred from passing subset tests.",
    "summary": summary,
    "requirements": requirements,
}
(ROOT / "docs/COMPLETION-LEDGER.json").write_text(json.dumps(result, indent=2) + "\n")
lines = [
    "# Requirement completion ledger",
    "",
    result["method"],
    "",
    f"Scope: 270 functional requirements and 37 non-functional qualification requirements. Status: {summary}. Enterprise completion: **false**.",
    "",
    "| Requirement | Title | Status | Evidence |",
    "|---|---|---|---|",
]
for req in requirements:
    paths = ", ".join(f"[{Path(p).name}](../{p})" for p in req["evidence_paths"])
    lines.append(f"| {req['id']} | {req['title']} | {req['status']} | {paths or 'Pending'} |")
(ROOT / "docs/COMPLETION-LEDGER.md").write_text("\n".join(lines) + "\n")
print(json.dumps(summary))
